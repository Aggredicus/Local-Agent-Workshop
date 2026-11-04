use std::fs;
use std::io::Write;
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};

static SERIAL: AtomicUsize = AtomicUsize::new(0);
fn binary() -> &'static str { env!("CARGO_BIN_EXE_law-swarm") }

fn command(args: &[&str]) -> std::process::Output {
    Command::new(binary()).args(args).output().expect("start law-swarm")
}

#[test]
fn end_to_end_local_replay_and_worker_protocol() {
    let n = SERIAL.fetch_add(1, Ordering::SeqCst);
    let dir = std::env::temp_dir().join(format!("law-cli-{}-{n}", std::process::id()));
    let dir_string = dir.to_string_lossy().into_owned();
    let flags = ["submit", "--state", &dir_string, "--id", "t1", "--thread", "hello", "--target", "local", "--tool", "sum", "--input", "17, -5, 2"];
    assert!(command(&flags).status.success());
    assert!(command(&flags).status.success(), "identical submissions must be idempotent");
    let done = command(&["drive", "--state", &dir_string]);
    assert!(done.status.success());
    assert!(String::from_utf8_lossy(&done.stdout).contains("completed \"14\""));
    let status = command(&["status", "--state", &dir_string]);
    assert!(String::from_utf8_lossy(&status.stdout).contains("done"));
    let more = command(&["drive", "--state", &dir_string]);
    assert!(more.status.success());
    assert!(more.stdout.is_empty(), "completed task must never run twice");

    let mut proc = Command::new(binary()).arg("worker")
        .stdin(Stdio::piped()).stdout(Stdio::piped()).spawn().expect("spawn worker");
    proc.stdin.take().expect("stdin").write_all(b"LAW-WORK/1\ttwo\tuppercase\t68656c6c6f\n").expect("send");
    let result = proc.wait_with_output().expect("wait worker");
    assert!(result.status.success());
    assert_eq!(String::from_utf8_lossy(&result.stdout), "LAW-RESULT/1\ttwo\tOK\t48454c4c4f\n");
    fs::remove_dir_all(dir).expect("remove test state");
}

#[test]
fn rejects_unauthorized_execution_and_host_options() {
    let failed = command(&["worker"]);
    assert!(!failed.status.success());
    let dir = std::env::temp_dir().join(format!("law-cli-reject-{}", std::process::id()));
    let d = dir.to_string_lossy().into_owned();
    let result = command(&["submit", "--state", &d, "--id", "t", "--thread", "test", "--target", "ssh:-oProxyCommand=bad", "--tool", "uppercase", "--input", "abc"]);
    assert!(!result.status.success());
    assert!(command(&["submit", "--state", &d, "--id", "t", "--thread", "test", "--target", "local", "--tool", "bash", "--input", "echo bad"]).status.success() == false);
    fs::remove_dir_all(dir).expect("remove test state");
}
