//! Append-only, single-writer state machine. The model's "agent" is a durable
//! task record, not a resident worker, and an event advances it one step.
//!
//! The first release only admits side-effect-free tools: a crash after
//! dispatch can lead to at-least-once execution, never an unsafe mutation.

use crate::protocol::{hex_decode, hex_encode, validate_id, Target, Tool, WorkOrder, MAX_INPUT};
use crate::transport;
use std::collections::{BTreeMap, HashSet};
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

const MAX_JOURNAL_BYTES: usize = 32 * 1024 * 1024;
const MAX_ATTEMPTS: u8 = 3;

pub type Receipt = (String, Result<String, String>);

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Record {
    Accepted(WorkOrder),
    Started(String),
    Completed { id: String, result: Result<String, String> },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct JobState {
    pub order: WorkOrder,
    pub attempts: u8,
    pub result: Option<Result<String, String>>,
}

#[derive(Clone, Debug, Default)]
struct Projection {
    jobs: BTreeMap<String, JobState>,
    arrival: Vec<String>,
}

impl Projection {
    fn apply(&mut self, record: &Record) -> Result<(), String> {
        match record {
            Record::Accepted(order) => {
                order.validate()?;
                if let Some(existing) = self.jobs.get(&order.id) {
                    if existing.order == *order { return Ok(()); }
                    return Err("duplicate job ID with different contents".into());
                }
                self.arrival.push(order.id.clone());
                self.jobs.insert(order.id.clone(), JobState { order: order.clone(), attempts: 0, result: None });
            }
            Record::Started(id) => {
                let job = self.jobs.get_mut(id).ok_or("start before accept")?;
                if job.result.is_some() || job.attempts >= MAX_ATTEMPTS {
                    return Err("cannot start an already terminal or exhausted job".into());
                }
                job.attempts += 1;
            }
            Record::Completed { id, result } => {
                let job = self.jobs.get_mut(id).ok_or("completion before acceptance")?;
                if job.attempts == 0 || job.result.is_some() {
                    return Err("completion is not matched to an active job".into());
                }
                if result.as_ref().map_or_else(|e| e.len(), |v| v.len()) > MAX_INPUT {
                    return Err("completion exceeds size limit".into());
                }
                job.result = Some(result.clone());
            }
        }
        Ok(())
    }

    /// Select at most one unfinished job per conversation and at most one
    /// job per target in a slice. A thread's later jobs cannot overtake an
    /// unfinished predecessor, but different threads can advance together.
    fn ready(&self, slots: usize) -> Vec<WorkOrder> {
        let mut active_threads = HashSet::new();
        let mut active_targets = HashSet::new();
        let mut ready = Vec::new();
        for id in &self.arrival {
            let Some(job) = self.jobs.get(id) else { continue };
            if job.result.is_some() { continue; }
            if !active_threads.insert(job.order.thread.clone()) { continue; }
            if !active_targets.insert(job.order.target.label()) { continue; }
            ready.push(job.order.clone());
            if ready.len() == slots { break; }
        }
        ready
    }
}

fn checksum(bytes: &[u8]) -> u32 {
    // Ordinary CRC32 for torn/corrupt record detection; never an auth token.
    let mut crc = !0u32;
    for b in bytes {
        crc ^= u32::from(*b);
        for _ in 0..8 {
            crc = (crc >> 1) ^ (if crc & 1 == 1 { 0xEDB8_8320 } else { 0 });
        }
    }
    !crc
}

fn as_text(s: &str) -> String { hex_encode(s.as_bytes()) }
fn from_text(s: &str) -> Result<String, String> {
    String::from_utf8(hex_decode(s)?).map_err(|_| "invalid journal UTF-8".into())
}

fn pack(record: &Record) -> String {
    let body = match record {
        Record::Accepted(o) => format!("A\t{}\t{}\t{}\t{}\t{}", o.id, o.thread, o.tool.name(), as_text(&o.target.label()), as_text(&o.input)),
        Record::Started(id) => format!("S\t{id}"),
        Record::Completed { id, result } => match result {
            Ok(value) => format!("C\t{id}\tOK\t{}", as_text(value)),
            Err(error) => format!("C\t{id}\tERR\t{}", as_text(error)),
        },
    };
    format!("LAW-JOURNAL/1\t{:08x}\t{body}\n", checksum(body.as_bytes()))
}

fn unpack(line: &str) -> Result<Record, String> {
    let mut parts = line.trim_end_matches('\n').splitn(3, '\t');
    if parts.next() != Some("LAW-JOURNAL/1") { return Err("unknown journal record version".into()); }
    let checksum_field = parts.next().ok_or("missing checksum")?;
    let expected = u32::from_str_radix(checksum_field, 16).map_err(|_| "invalid checksum".to_string())?;
    let body = parts.next().ok_or("missing body")?;
    if checksum(body.as_bytes()) != expected { return Err("journal checksum mismatch".into()); }
    let p: Vec<&str> = body.split('\t').collect();
    match p.as_slice() {
        ["A", id, thread, tool, target, input] => {
            let order = WorkOrder { id: (*id).into(), thread: (*thread).into(), tool: Tool::parse(tool)?, target: Target::parse(&from_text(target)?)?, input: from_text(input)? };
            order.validate()?;
            Ok(Record::Accepted(order))
        }
        ["S", id] => {
            validate_id(id)?;
            Ok(Record::Started((*id).to_string()))
        }
        ["C", id, status, value] => {
            validate_id(id)?;
            let value = from_text(value)?;
            let result = match *status {
                "OK" => Ok(value),
                "ERR" => Err(value),
                _ => return Err("invalid completion status".into()),
            };
            Ok(Record::Completed { id: (*id).to_string(), result })
        }
        _ => Err("invalid journal record structure".into()),
    }
}

/// Exclusive process ownership without extra dependencies. A crash may leave
/// this sentinel; users must verify that no writer remains before removing it.
struct FileSentinel(PathBuf);
impl Drop for FileSentinel {
    fn drop(&mut self) { let _ = fs::remove_file(&self.0); }
}

pub struct Workbench {
    file: File,
    _sentinel: FileSentinel,
    projection: Projection,
}

impl Workbench {
    pub fn open(dir: &Path) -> Result<Self, String> {
        fs::create_dir_all(dir).map_err(|e| format!("create state directory: {e}"))?;
        let lock_path = dir.join("writer.lock");
        let mut lock = OpenOptions::new().write(true).create_new(true).open(&lock_path)
            .map_err(|e| format!("only one LAW writer is allowed; inspect {} before recovery: {e}", lock_path.display()))?;
        writeln!(lock, "pid={}", std::process::id()).map_err(|e| e.to_string())?;
        let sentinel = FileSentinel(lock_path);
        let path = dir.join("events.lawlog");
        let mut file = OpenOptions::new().read(true).write(true).create(true).truncate(false).open(path).map_err(|e| e.to_string())?;
        let size = file.metadata().map_err(|e| e.to_string())?.len();
        if size > MAX_JOURNAL_BYTES as u64 { return Err("journal exceeds configured size limit".into()); }
        let mut data = Vec::new();
        file.read_to_end(&mut data).map_err(|e| e.to_string())?;
        let mut projection = Projection::default();
        let mut consumed = 0usize;
        for line in data.split_inclusive(|c| *c == b'\n') {
            if !line.ends_with(b"\n") {
                // Incomplete last write: discard only the final uncommitted fragment.
                eprintln!("warning: dropping incomplete journal tail");
                break;
            }
            let text = std::str::from_utf8(line).map_err(|_| "journal not valid UTF-8".to_string())?;
            let record = unpack(text)?;
            projection.apply(&record)?;
            consumed += line.len();
        }
        file.set_len(consumed as u64).map_err(|e| e.to_string())?;
        file.sync_data().map_err(|e| e.to_string())?;
        Ok(Self { file, _sentinel: sentinel, projection })
    }

    fn append(&mut self, record: Record) -> Result<(), String> {
        // Validate against a copy first so an invalid transition never reaches disk.
        let mut next = self.projection.clone();
        next.apply(&record)?;
        use std::io::{Seek, SeekFrom};
        self.file.seek(SeekFrom::End(0)).map_err(|e| e.to_string())?;
        self.file.write_all(pack(&record).as_bytes()).map_err(|e| e.to_string())?;
        self.file.sync_data().map_err(|e| e.to_string())?;
        self.projection = next;
        Ok(())
    }

    pub fn submit(&mut self, order: WorkOrder) -> Result<bool, String> {
        order.validate()?;
        if let Some(existing) = self.projection.jobs.get(&order.id) {
            if existing.order == order { return Ok(false); }
            return Err("job ID already refers to different work".into());
        }
        self.append(Record::Accepted(order))?;
        Ok(true)
    }

    pub fn jobs(&self) -> Vec<JobState> {
        self.projection.arrival.iter().filter_map(|id| self.projection.jobs.get(id).cloned()).collect()
    }

    /// Run bounded, independent slices. Each tool dispatch happens only after
    /// a durable Started record; its eventual completion is another event.
    pub fn drive(&mut self, parallel: usize, budget: usize) -> Result<Vec<Receipt>, String> {
        if !(1..=16).contains(&parallel) || !(1..=100).contains(&budget) {
            return Err("parallel must be 1..16 and budget 1..100".into());
        }
        let mut receipts = Vec::new();
        while receipts.len() < budget {
            let ready = self.projection.ready(parallel.min(budget - receipts.len()));
            if ready.is_empty() { break; }
            let mut launch = Vec::new();
            for order in ready {
                let attempts = self.projection.jobs.get(&order.id).ok_or("missing job")?.attempts;
                if attempts >= MAX_ATTEMPTS {
                    let result = Err(format!("exhausted {MAX_ATTEMPTS} attempts after interrupted execution"));
                    self.append(Record::Completed { id: order.id.clone(), result: result.clone() })?;
                    receipts.push((order.id, result));
                    continue;
                }
                self.append(Record::Started(order.id.clone()))?;
                launch.push(order);
            }
            let completed = std::thread::scope(|scope| {
                let handles: Vec<_> = launch.iter().map(|task| scope.spawn(move || transport::execute(task))).collect();
                handles.into_iter().zip(launch.iter()).map(|(h, task)| {
                    let outcome = h.join().unwrap_or_else(|_| Err("worker thread panicked".into()));
                    (task.id.clone(), outcome)
                }).collect::<Vec<_>>()
            });
            for (id, outcome) in completed {
                let trimmed = match outcome {
                    Ok(v) if v.len() <= MAX_INPUT => Ok(v),
                    Ok(_) => Err("worker output exceeded size limit".into()),
                    Err(e) => Err(e.chars().take(MAX_INPUT / 4).collect()),
                };
                self.append(Record::Completed { id: id.clone(), result: trimmed.clone() })?;
                receipts.push((id, trimmed));
            }
        }
        Ok(receipts)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};
    static SERIAL: AtomicUsize = AtomicUsize::new(0);
    fn temp_state() -> PathBuf {
        let n = SERIAL.fetch_add(1, Ordering::SeqCst);
        let path = std::env::temp_dir().join(format!("law-runtime-test-{}-{n}", std::process::id()));
        let _ = fs::remove_dir_all(&path);
        path
    }
    fn order(id: &str, thread: &str) -> WorkOrder {
        WorkOrder { id: id.into(), thread: thread.into(), tool: Tool::WordCount, input: "one two three".into(), target: Target::Local }
    }
    #[test]
    fn restores_state_and_deduplicates_identical_submissions() {
        let path = temp_state();
        {
            let mut w = Workbench::open(&path).expect("open");
            assert!(w.submit(order("t1", "alpha")).expect("submit"));
            assert!(!w.submit(order("t1", "alpha")).expect("replay"));
            assert_eq!(w.drive(2, 3).expect("drive")[0], ("t1".into(), Ok("3".into())));
        }
        let w = Workbench::open(&path).expect("reopen");
        assert_eq!(w.jobs()[0].result, Some(Ok("3".into())));
        drop(w);
        fs::remove_dir_all(path).expect("cleanup");
    }
    #[test]
    fn isolates_threads_and_preserves_order() {
        let mut p = Projection::default();
        p.apply(&Record::Accepted(order("a", "same"))).expect("apply");
        p.apply(&Record::Accepted(order("b", "same"))).expect("apply");
        p.apply(&Record::Accepted(order("c", "other"))).expect("apply");
        // Same target: v0.1 admits only one concurrent task to avoid overload.
        assert_eq!(p.ready(8).iter().map(|j| j.id.as_str()).collect::<Vec<_>>(), vec!["a"]);
        p.apply(&Record::Started("a".into())).expect("start");
        p.apply(&Record::Completed { id: "a".into(), result: Ok("3".into()) }).expect("finish");
        assert_eq!(p.ready(8)[0].id, "b");
    }
    #[test]
    fn rejects_corrupted_journal_and_double_writers() {
        let path = temp_state();
        let w = Workbench::open(&path).expect("open");
        assert!(Workbench::open(&path).is_err());
        drop(w);
        fs::write(path.join("events.lawlog"), b"LAW-JOURNAL/1\t00000000\tbad\n").expect("write");
        assert!(Workbench::open(&path).is_err());
        fs::remove_dir_all(path).expect("cleanup");
    }
    #[test]
    fn interrupted_attempt_is_retried_from_journal() {
        let path = temp_state();
        {
            let mut w = Workbench::open(&path).expect("open");
            w.submit(order("t1", "t")).expect("submit");
            w.append(Record::Started("t1".into())).expect("start");
        }
        let mut w = Workbench::open(&path).expect("reopen");
        assert_eq!(w.drive(1, 1).expect("retry")[0].1, Ok("3".into()));
        assert_eq!(w.jobs()[0].attempts, 2);
        drop(w);
        fs::remove_dir_all(path).expect("cleanup");
    }
    #[test]
    fn incomplete_trailing_record_is_ignored_but_complete_corruption_is_not() {
        let path = temp_state();
        {
            let mut w = Workbench::open(&path).expect("open");
            w.submit(order("a", "t")).expect("submit");
        }
        let path_log = path.join("events.lawlog");
        let mut append = OpenOptions::new().append(true).open(&path_log).expect("append");
        append.write_all(b"LAW-JOURNAL/1\tdeadbeef\tpartial").expect("write");
        drop(append);
        let w = Workbench::open(&path).expect("reopen");
        assert_eq!(w.jobs().len(), 1);
        drop(w);
        assert!(!fs::read_to_string(path_log).expect("read").contains("partial"));
        fs::remove_dir_all(path).expect("cleanup");
    }
}
