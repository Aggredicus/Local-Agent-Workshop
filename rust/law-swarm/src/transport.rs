//! Worker implementations. The only network path is a pinned-host-key SSH
//! session and a fixed remote command; no arbitrary command requests exist.

use crate::protocol::{decode_request, decode_response, encode_request, encode_response, Target, Tool, WorkOrder, MAX_WIRE};
use std::io::{Read, Write};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

pub fn execute(order: &WorkOrder) -> Result<String, String> {
    order.validate()?;
    match &order.target {
        Target::Local => run_builtin(&order.tool, &order.input),
        Target::Ssh(host) => execute_over_ssh(order, host, Duration::from_secs(30)),
    }
}

pub fn run_builtin(tool: &Tool, input: &str) -> Result<String, String> {
    match tool {
        Tool::Uppercase => Ok(input.to_uppercase()),
        Tool::WordCount => Ok(input.split_whitespace().count().to_string()),
        Tool::Sum => {
            let mut count = 0;
            let mut sum = 0i64;
            for item in input.split(|c: char| c == ',' || c.is_whitespace()).filter(|v| !v.is_empty()) {
                let number: i64 = item.parse().map_err(|_| "sum requires signed 64-bit integers".to_string())?;
                sum = sum.checked_add(number).ok_or("integer overflow")?;
                count += 1;
            }
            if count == 0 { return Err("sum requires at least one integer".into()); }
            Ok(sum.to_string())
        }
    }
}

/// One request, one response; suitable for SSH standard streams. This process
/// exposes no TCP listener, no direct shell execution, and no filesystem tools.
pub fn worker_once(request: &str) -> Result<String, String> {
    let (id, tool, input) = decode_request(request)?;
    let result = run_builtin(&tool, &input);
    let bounded = match result {
        Ok(output) if output.len() <= crate::protocol::MAX_INPUT => Ok(output),
        Ok(_) => Err("worker output exceeded size limit".to_string()),
        Err(error) => Err(error),
    };
    Ok(encode_response(&id, &bounded))
}

fn execute_over_ssh(order: &WorkOrder, host: &str, timeout: Duration) -> Result<String, String> {
    // The host has been strictly validated by WorkOrder::validate. SSH verifies
    // its pre-paired key; BatchMode rejects interactive authentication.
    let mut child = Command::new("ssh")
        .args(["-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=8", "-o", "NumberOfPasswordPrompts=0", "--", host, "law-swarm worker"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("ssh process could not start: {e}"))?;

    if let Some(mut stdin) = child.stdin.take() {
        if let Err(e) = stdin.write_all(encode_request(order).as_bytes()) {
            let _ = child.kill();
            let _ = child.wait();
            return Err(format!("cannot send worker request: {e}"));
        }
    }
    let started = Instant::now();
    let status = loop {
        match child.try_wait() {
            Ok(Some(status)) => break status,
            Ok(None) if started.elapsed() < timeout => std::thread::sleep(Duration::from_millis(25)),
            Ok(None) => {
                let _ = child.kill();
                let _ = child.wait();
                return Err("remote worker exceeded 30-second time limit".into());
            }
            Err(e) => {
                let _ = child.kill();
                let _ = child.wait();
                return Err(format!("cannot wait for SSH: {e}"));
            }
        }
    };
    // The child has exited, so these bounded reads cannot block waiting for EOF.
    let mut stdout = String::new();
    let mut stderr = String::new();
    if let Some(mut out) = child.stdout.take() {
        out.take((MAX_WIRE + 1) as u64).read_to_string(&mut stdout).map_err(|_| "non-UTF-8 SSH response")?;
    }
    if let Some(mut err) = child.stderr.take() {
        err.take(4096).read_to_string(&mut stderr).map_err(|_| "non-UTF-8 SSH error")?;
    }
    if !status.success() {
        return Err(format!("SSH worker failed ({}): {}", status, stderr.trim().chars().take(240).collect::<String>()));
    }
    decode_response(&stdout, &order.id)?
}

pub fn stdin_worker_once() -> Result<(), String> {
    let mut text = String::new();
    std::io::stdin().take((MAX_WIRE + 1) as u64).read_to_string(&mut text).map_err(|e| e.to_string())?;
    let response = worker_once(&text)?;
    std::io::stdout().write_all(response.as_bytes()).map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn side_effect_free_worker_round_trip() {
        let job = WorkOrder { id: "A".into(), thread: "t".into(), tool: Tool::WordCount, input: "hello Rust world".into(), target: Target::Local };
        let output = worker_once(&encode_request(&job)).expect("worker response");
        assert_eq!(decode_response(&output, "A"), Ok(Ok("3".to_string())));
    }
    #[test]
    fn integer_overflow_is_an_error_not_a_panic() {
        assert_eq!(run_builtin(&Tool::Sum, "8, -3, 2"), Ok("7".into()));
        assert!(run_builtin(&Tool::Sum, "9223372036854775807, 1").is_err());
        assert!(run_builtin(&Tool::Sum, "").is_err());
    }
}
