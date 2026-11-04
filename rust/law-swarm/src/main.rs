use law_swarm::protocol::{Target, Tool, WorkOrder};
use law_swarm::runtime::Workbench;
use law_swarm::transport::stdin_worker_once;
use std::collections::BTreeMap;
use std::path::PathBuf;

fn usage() -> &'static str {
    "LAW Swarm v0.1 (original Rust, no third-party dependencies)\n\
     Usage:\n\
       law-swarm init --state DIR\n\
       law-swarm submit --state DIR --id ID --thread THREAD --target local|ssh:USER@HOST --tool uppercase|word-count|sum --input TEXT\n\
       law-swarm drive --state DIR [--parallel 2] [--budget 10]\n\
       law-swarm status --state DIR\n\
       law-swarm worker\n\
       law-swarm advertise\n\
     Note: local and SSH workers run only three harmless, allowlisted tools.\n\
     SSH requires an already-trusted host key and noninteractive authentication."
}

fn options(args: &[String]) -> Result<BTreeMap<String, String>, String> {
    if args.len() % 2 != 0 { return Err("flags need values".into()); }
    let mut opts = BTreeMap::new();
    for pair in args.chunks_exact(2) {
        let key = pair[0].strip_prefix("--").ok_or("expected --flag VALUE")?;
        if !["state", "id", "thread", "target", "tool", "input", "parallel", "budget"].contains(&key) {
            return Err(format!("unknown flag: --{key}"));
        }
        if opts.insert(key.to_string(), pair[1].clone()).is_some() { return Err(format!("duplicate flag --{key}")); }
    }
    Ok(opts)
}

fn need<'a>(opts: &'a BTreeMap<String, String>, flag: &str) -> Result<&'a str, String> {
    opts.get(flag).map(|s| s.as_str()).ok_or_else(|| format!("missing --{flag}"))
}

fn path(opts: &BTreeMap<String, String>) -> Result<PathBuf, String> {
    Ok(PathBuf::from(need(opts, "state")?))
}

fn execute() -> Result<(), String> {
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let Some(command) = argv.first().map(String::as_str) else { return Err(usage().into()); };
    match command {
        "--help" | "help" => { println!("{}", usage()); Ok(()) }
        "worker" if argv.len() == 1 => stdin_worker_once(),
        "advertise" if argv.len() == 1 => {
            // Informational advertisement, not proof of device identity.
            println!("law-swarm/0.1 tools=uppercase,word-count,sum transport=ssh-stdio");
            Ok(())
        }
        "init" | "submit" | "drive" | "status" => {
            let opts = options(&argv[1..])?;
            let mut workshop = Workbench::open(&path(&opts)?)?;
            match command {
                "init" => println!("LAW state initialized"),
                "submit" => {
                    let order = WorkOrder {
                        id: need(&opts, "id")?.to_string(),
                        thread: need(&opts, "thread")?.to_string(),
                        tool: Tool::parse(need(&opts, "tool")?)?,
                        input: need(&opts, "input")?.to_string(),
                        target: Target::parse(need(&opts, "target")?)?,
                    };
                    let added = workshop.submit(order)?;
                    println!("{}", if added { "queued" } else { "already queued (same ID and body)" });
                }
                "drive" => {
                    let parallel: usize = opts.get("parallel").map(|v| v.parse().map_err(|_| "bad --parallel")).transpose()?.unwrap_or(2);
                    let budget: usize = opts.get("budget").map(|v| v.parse().map_err(|_| "bad --budget")).transpose()?.unwrap_or(10);
                    for (id, result) in workshop.drive(parallel, budget)? {
                        match result {
                            Ok(value) => println!("{id}: completed {value:?}"),
                            Err(error) => println!("{id}: failed {error:?}"),
                        }
                    }
                }
                "status" => {
                    for job in workshop.jobs() {
                        let state = match job.result {
                            Some(Ok(_)) => "done",
                            Some(Err(_)) => "failed",
                            None if job.attempts > 0 => "pending/recoverable",
                            None => "queued",
                        };
                        println!("{}\t{}\t{}\t{}\tattempts={}", job.order.id, job.order.thread, job.order.target.label(), state, job.attempts);
                    }
                }
                _ => unreachable!(),
            }
            Ok(())
        }
        _ => Err(usage().into()),
    }
}

fn main() {
    if let Err(error) = execute() {
        eprintln!("error: {error}");
        std::process::exit(2);
    }
}
