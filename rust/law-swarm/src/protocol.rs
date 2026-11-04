//! Original, deliberately small wire contract. This is not RAP or an Infinity API.
//! All network access is delegated to the system SSH client.

use std::fmt;

pub const MAX_INPUT: usize = 8192;
pub const MAX_WIRE: usize = 32768;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Tool {
    Uppercase,
    WordCount,
    Sum,
}

impl Tool {
    pub fn parse(s: &str) -> Result<Self, String> {
        match s {
            "uppercase" => Ok(Self::Uppercase),
            "word-count" => Ok(Self::WordCount),
            "sum" => Ok(Self::Sum),
            _ => Err(format!("tool not allowlisted: {s}")),
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            Self::Uppercase => "uppercase",
            Self::WordCount => "word-count",
            Self::Sum => "sum",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Target {
    Local,
    Ssh(String),
}

impl Target {
    pub fn parse(s: &str) -> Result<Self, String> {
        if s == "local" {
            return Ok(Self::Local);
        }
        let host = s.strip_prefix("ssh:").ok_or("target must be local or ssh:USER@HOST")?;
        validate_host(host)?;
        Ok(Self::Ssh(host.to_string()))
    }

    pub fn label(&self) -> String {
        match self {
            Self::Local => "local".to_string(),
            Self::Ssh(host) => format!("ssh:{host}"),
        }
    }
}

/// Restrict the SSH destination to a simple, literal name. No CLI options,
/// whitespace, shell metacharacters, remote command, or SSH config snippets.
fn validate_host(host: &str) -> Result<(), String> {
    if host.is_empty() || host.len() > 200 || host.starts_with('-') {
        return Err("invalid SSH destination".into());
    }
    let pieces: Vec<_> = host.split('@').collect();
    if pieces.len() > 2 || pieces.iter().any(|p| p.is_empty() || p.starts_with('-')) {
        return Err("invalid SSH destination".into());
    }
    if !host.bytes().all(|b| b.is_ascii_alphanumeric() || b"._-@".contains(&b)) {
        return Err("invalid SSH destination characters".into());
    }
    Ok(())
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct WorkOrder {
    pub id: String,
    pub thread: String,
    pub tool: Tool,
    pub input: String,
    pub target: Target,
}

impl WorkOrder {
    pub fn validate(&self) -> Result<(), String> {
        validate_id(&self.id)?;
        validate_id(&self.thread)?;
        if self.input.len() > MAX_INPUT {
            return Err(format!("input exceeds {MAX_INPUT} bytes"));
        }
        Target::parse(&self.target.label())?;
        Ok(())
    }
}

pub fn validate_id(s: &str) -> Result<(), String> {
    if s.is_empty() || s.len() > 64 || !s.bytes().all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b)) {
        return Err("IDs must use 1..64 ASCII letters, numbers, underscore, or hyphen".into());
    }
    Ok(())
}

pub fn hex_encode(bytes: &[u8]) -> String {
    let mut out = String::with_capacity(bytes.len() * 2);
    const H: &[u8] = b"0123456789abcdef";
    for b in bytes {
        out.push(H[(b >> 4) as usize] as char);
        out.push(H[(b & 15) as usize] as char);
    }
    out
}

// Retain Rust 1.80 compatibility: newer integer and slice helpers are optional.
#[allow(clippy::manual_is_multiple_of, clippy::chunks_exact_to_as_chunks)]
pub fn hex_decode(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 { return Err("odd hex string length".into()); }
    let mut out = Vec::with_capacity(s.len() / 2);
    for pair in s.as_bytes().chunks_exact(2) {
        let n = |c: u8| -> Result<u8, String> {
            match c {
                b'0'..=b'9' => Ok(c - b'0'),
                b'a'..=b'f' => Ok(c - b'a' + 10),
                b'A'..=b'F' => Ok(c - b'A' + 10),
                _ => Err("invalid hex digit".into()),
            }
        };
        out.push((n(pair[0])? << 4) | n(pair[1])?);
    }
    Ok(out)
}

fn decode_text(value: &str) -> Result<String, String> {
    String::from_utf8(hex_decode(value)?).map_err(|e| format!("invalid UTF-8: {e}"))
}

pub fn encode_request(job: &WorkOrder) -> String {
    format!("LAW-WORK/1\t{}\t{}\t{}\n", job.id, job.tool.name(), hex_encode(job.input.as_bytes()))
}

pub fn decode_request(s: &str) -> Result<(String, Tool, String), String> {
    if s.len() > MAX_WIRE { return Err("oversized worker request".into()); }
    let mut p = s.trim_end_matches(['\r', '\n']).split('\t');
    if p.next() != Some("LAW-WORK/1") { return Err("unknown worker protocol".into()); }
    let id = p.next().ok_or("missing task ID")?;
    validate_id(id)?;
    let tool = Tool::parse(p.next().ok_or("missing tool")?)?;
    let input = decode_text(p.next().ok_or("missing input")?)?;
    if p.next().is_some() || input.len() > MAX_INPUT { return Err("invalid worker request".into()); }
    Ok((id.to_string(), tool, input))
}

pub fn encode_response(id: &str, outcome: &Result<String, String>) -> String {
    let (status, text) = match outcome {
        Ok(value) => ("OK", value),
        Err(error) => ("ERR", error),
    };
    format!("LAW-RESULT/1\t{id}\t{status}\t{}\n", hex_encode(text.as_bytes()))
}

pub fn decode_response(s: &str, expected_id: &str) -> Result<Result<String, String>, String> {
    if s.len() > MAX_WIRE { return Err("oversized worker response".into()); }
    let mut p = s.trim_end_matches(['\r', '\n']).split('\t');
    if p.next() != Some("LAW-RESULT/1") || p.next() != Some(expected_id) {
        return Err("unexpected response protocol or task ID".into());
    }
    let status = p.next().ok_or("missing worker status")?;
    let value = decode_text(p.next().ok_or("missing worker output")?)?;
    if p.next().is_some() { return Err("unexpected worker response fields".into()); }
    match status {
        "OK" => Ok(Ok(value)),
        "ERR" => Ok(Err(value)),
        _ => Err("unknown worker status".into()),
    }
}

impl fmt::Display for Tool {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.name())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn request_response_round_trip_handles_unicode_and_delimiters() {
        let task = WorkOrder { id: "task_1".into(), thread: "alpha".into(), tool: Tool::Uppercase, input: "नमस्ते\t🌍\n".into(), target: Target::Local };
        let (id, tool, text) = decode_request(&encode_request(&task)).expect("decode request");
        assert_eq!((id, tool, text), (task.id, task.tool, task.input));
        assert_eq!(decode_response(&encode_response("task_1", &Ok("hello\n".into())), "task_1"), Ok(Ok("hello\n".into())));
    }

    #[test]
    fn refuses_untrusted_targets_and_messages() {
        assert!(Target::parse("ssh:-oProxyCommand=evil").is_err());
        assert!(Target::parse("ssh:host;touch /tmp/x").is_err());
        assert!(Target::parse("ssh:alice@192.168.1.7").is_ok());
        assert!(decode_request("LAW-WORK/1\tbad id\tuppercase\t41\n").is_err());
        assert!(decode_response("LAW-RESULT/1\tother\tOK\t41\n", "expected").is_err());
    }
}
