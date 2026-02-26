#!/usr/bin/env python3
"""
Autonomous Jira orchestrator loop.

Flow per cycle:
1. Pick next open issue by JQL.
2. Assign worker.
3. Move to In Progress.
4. Run implementation command.
5. Run review command.
6. If review PASS, move to Done. Otherwise keep ticket active and comment findings.

This script is intentionally conservative: it uses a single lock file, explicit retries for 429,
and writes state to disk so assignment rotation is deterministic across restarts.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKOFF_SECONDS = [15, 30, 60, 120]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        return f"{self.stdout}\n{self.stderr}".strip()


@dataclass
class StepExecution:
    result: CommandResult
    runner: str
    fallback_used: bool


class JiraClient:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url.rstrip("/")
        raw = f"{email}:{token}".encode("utf-8")
        auth = f"Basic {base64.b64encode(raw).decode('ascii')}"
        self.headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _parse_retry_after(self, headers: urllib.error.HTTPError.headers) -> float | None:  # type: ignore[type-arg]
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        reset_header = headers.get("X-RateLimit-Reset")
        if reset_header:
            try:
                reset_ts = float(reset_header)
                return max(reset_ts - datetime.now(timezone.utc).timestamp(), 0.0)
            except ValueError:
                pass
        return None

    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url=url, method=method, headers=self.headers, data=body)
        for attempt in range(len(BACKOFF_SECONDS) + 1):
            try:
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    if not data:
                        return None
                    return json.loads(data.decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    if attempt >= len(BACKOFF_SECONDS):
                        raise RuntimeError(f"429 retry budget exhausted for {method} {url}") from exc
                    wait = self._parse_retry_after(exc.headers)  # type: ignore[arg-type]
                    if wait is None:
                        wait = BACKOFF_SECONDS[attempt]
                    print(f"[WARN] 429 on {path}; sleeping {wait:.1f}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"{exc.code} {method} {path}: {detail}") from exc
        return None

    def search_issues(self, jql: str, fields: list[str], max_results: int = 10) -> list[dict[str, Any]]:
        enc_jql = urllib.parse.quote(jql)
        enc_fields = urllib.parse.quote(",".join(fields))
        path = f"/rest/api/3/search/jql?jql={enc_jql}&fields={enc_fields}&maxResults={max_results}"
        data = self.request_json("GET", path)
        if not isinstance(data, dict):
            return []
        issues = data.get("issues", [])
        return issues if isinstance(issues, list) else []

    def assign_issue(self, issue_key: str, account_id: str | None) -> None:
        self.request_json(
            "PUT",
            f"/rest/api/3/issue/{urllib.parse.quote(issue_key)}/assignee",
            {"accountId": account_id},
        )

    def transition_issue(self, issue_key: str, transition_id: str) -> None:
        self.request_json(
            "POST",
            f"/rest/api/3/issue/{urllib.parse.quote(issue_key)}/transitions",
            {"transition": {"id": transition_id}},
        )

    def add_comment(self, issue_key: str, text: str) -> None:
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": text}],
                    }
                ],
            }
        }
        self.request_json(
            "POST",
            f"/rest/api/3/issue/{urllib.parse.quote(issue_key)}/comment",
            payload,
        )

    def find_assignable_users(self, project_key: str) -> list[dict[str, Any]]:
        path = f"/rest/api/3/user/assignable/search?project={urllib.parse.quote(project_key)}&maxResults=1000"
        data = self.request_json("GET", path)
        return data if isinstance(data, list) else []


class LockFile:
    def __init__(self, path: Path):
        self.path = path
        self.handle: int | None = None

    def __enter__(self) -> "LockFile":
        try:
            self.handle = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(self.handle, str(os.getpid()).encode("ascii"))
        except FileExistsError as exc:
            raise RuntimeError(f"Lock file exists: {self.path}") from exc
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.handle is not None:
            os.close(self.handle)
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = value


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_runtime_context(issue: dict[str, Any], assignee: dict[str, str], config: dict[str, Any]) -> dict[str, str]:
    key = str(issue.get("key", ""))
    fields = issue.get("fields", {}) if isinstance(issue.get("fields"), dict) else {}
    summary = str(fields.get("summary", ""))
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "issue_key": key,
        "issue_summary": summary,
        "assignee_name": assignee["display_name"],
        "assignee_account_id": assignee["account_id"],
        "date": now_date,
        "project_key": str(config.get("project_key", "")),
    }


def render_template(template: str, context: dict[str, str]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def run_command(command_template: str, context: dict[str, str], timeout_seconds: int) -> CommandResult:
    command = render_template(command_template, context)
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return CommandResult(completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def normalize_patterns(raw_patterns: Any) -> list[str]:
    if not isinstance(raw_patterns, list):
        return []
    patterns: list[str] = []
    for item in raw_patterns:
        text = str(item).strip()
        if text:
            patterns.append(text)
    return patterns


def normalize_step_command(
    step_value: Any,
    default_patterns: list[str],
) -> dict[str, Any]:
    if isinstance(step_value, str):
        return {
            "primary": step_value,
            "fallback": "",
            "fallback_on_patterns": list(default_patterns),
            "fallback_on_returncode": False,
        }
    if not isinstance(step_value, dict):
        raise ValueError("Step command must be string or object")

    primary = str(step_value.get("primary", "")).strip()
    if not primary:
        raise ValueError("Step command object requires non-empty 'primary'")
    fallback = str(step_value.get("fallback", "")).strip()
    patterns = normalize_patterns(step_value.get("fallback_on_patterns", default_patterns))
    return {
        "primary": primary,
        "fallback": fallback,
        "fallback_on_patterns": patterns,
        "fallback_on_returncode": bool(step_value.get("fallback_on_returncode", False)),
    }


def should_use_fallback(result: CommandResult, patterns: list[str], fallback_on_returncode: bool) -> bool:
    output = result.combined_output
    for pattern in patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return True
    return fallback_on_returncode and result.returncode != 0


def run_step_with_fallback(
    label: str,
    step_cfg: dict[str, Any],
    context: dict[str, str],
    timeout_seconds: int,
) -> StepExecution:
    primary = str(step_cfg["primary"])
    fallback = str(step_cfg.get("fallback", ""))
    patterns = list(step_cfg.get("fallback_on_patterns", []))
    fallback_on_returncode = bool(step_cfg.get("fallback_on_returncode", False))

    primary_result = run_command(primary, context, timeout_seconds)
    if fallback and should_use_fallback(primary_result, patterns, fallback_on_returncode):
        print(f"[WARN] {label}: primary command triggered fallback.")
        fallback_result = run_command(fallback, context, timeout_seconds)
        return StepExecution(result=fallback_result, runner="fallback", fallback_used=True)
    return StepExecution(result=primary_result, runner="primary", fallback_used=False)


def determine_review_pass(
    result: CommandResult,
    pass_pattern: str,
    fail_pattern: str,
) -> bool:
    output = result.combined_output
    if result.returncode != 0:
        return False
    if re.search(fail_pattern, output, re.IGNORECASE):
        return False
    return bool(re.search(pass_pattern, output, re.IGNORECASE))


def resolve_worker_pool(jira: JiraClient, project_key: str, display_names: list[str]) -> list[dict[str, str]]:
    assignable = jira.find_assignable_users(project_key)
    by_name: dict[str, dict[str, Any]] = {}
    for user in assignable:
        display = str(user.get("displayName", "")).strip()
        account_id = str(user.get("accountId", "")).strip()
        if display and account_id:
            by_name[display.lower()] = {"display_name": display, "account_id": account_id}

    pool: list[dict[str, str]] = []
    missing: list[str] = []
    for name in display_names:
        found = by_name.get(name.lower())
        if found:
            pool.append({"display_name": str(found["display_name"]), "account_id": str(found["account_id"])})
        else:
            missing.append(name)

    if missing:
        raise RuntimeError(f"Worker(s) not assignable in Jira project {project_key}: {', '.join(missing)}")
    if not pool:
        raise RuntimeError("Worker pool is empty")
    return pool


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous Jira project manager loop.")
    parser.add_argument(
        "--config",
        default="automation/auto-project-manager.local.json",
        help="Path to orchestrator JSON config.",
    )
    parser.add_argument(
        "--env-file",
        default=".env.jira.local",
        help="Optional env file for Jira credentials.",
    )
    parser.add_argument("--once", action="store_true", help="Run exactly one scheduling cycle.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without Jira writes or command execution.")
    args = parser.parse_args()

    config_path = Path(args.config)
    env_path = Path(args.env_file)
    load_env_file(env_path)

    if not config_path.exists():
        print(f"[ERROR] Missing config file: {config_path}", file=sys.stderr)
        return 1

    config = load_json_file(config_path)
    required_keys = [
        "project_key",
        "selection_jql",
        "worker_display_names",
        "status_transition_ids",
        "commands",
        "poll_seconds",
        "state_file",
        "lock_file",
    ]
    missing = [k for k in required_keys if k not in config]
    if missing:
        print(f"[ERROR] Missing config keys: {', '.join(missing)}", file=sys.stderr)
        return 1

    base_url = os.getenv("JIRA_BASE_URL", "").strip()
    email = os.getenv("JIRA_EMAIL", "").strip()
    token = os.getenv("JIRA_API_TOKEN", "").strip()
    if not base_url or not email or not token:
        print("[ERROR] Missing Jira credentials. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN.", file=sys.stderr)
        return 1

    jira = JiraClient(base_url, email, token)
    project_key = str(config["project_key"])
    state_path = Path(str(config["state_file"]))
    lock_path = Path(str(config["lock_file"]))
    poll_seconds = max(int(config.get("poll_seconds", 60)), 10)
    command_timeout_seconds = max(int(config.get("command_timeout_seconds", 1800)), 30)

    transition_ids = config["status_transition_ids"]
    in_progress_id = str(transition_ids["In Progress"])
    done_id = str(transition_ids["Done"])

    commands = config["commands"]
    fallback_rules = config.get("fallback_rules", {})
    default_fallback_patterns = normalize_patterns(
        fallback_rules.get(
            "patterns",
            [
                r"hit your limit",
                r"usage limit",
                r"quota",
                r"rate limit",
                r"resets \d",
            ],
        )
    )
    implement_cmd = normalize_step_command(commands["implement"], default_fallback_patterns)
    review_cmd = normalize_step_command(commands["review"], default_fallback_patterns)

    comments_cfg = config.get("comments", {})
    start_comment_tmpl = str(
        comments_cfg.get(
            "start",
            "Auto manager started work on {issue_key} with {assignee_name} on {date}.",
        )
    )
    done_comment_tmpl = str(
        comments_cfg.get(
            "done",
            "Auto manager review PASS on {date}. Completed by {assignee_name}.",
        )
    )
    fail_comment_tmpl = str(
        comments_cfg.get(
            "fail",
            "Auto manager review FAIL on {date}. Review output: {review_output}",
        )
    )
    impl_fail_comment_tmpl = str(
        comments_cfg.get(
            "implement_fail",
            "Auto manager implementation command failed on {date}. Output: {implement_output}",
        )
    )

    review_rules = config.get("review", {})
    pass_pattern = str(review_rules.get("pass_pattern", r"\bPASS\b"))
    fail_pattern = str(review_rules.get("fail_pattern", r"\bFAIL\b"))

    try:
        with LockFile(lock_path):
            print(f"[INFO] Started auto project manager loop for project {project_key}")
            workers = resolve_worker_pool(jira, project_key, list(config["worker_display_names"]))
            state = {"last_worker_index": -1}
            if state_path.exists():
                try:
                    loaded_state = load_json_file(state_path)
                    if isinstance(loaded_state, dict):
                        state.update(loaded_state)
                except Exception:
                    pass

            cycles = 0
            while True:
                issues = jira.search_issues(
                    jql=str(config["selection_jql"]),
                    fields=["summary", "status"],
                    max_results=1,
                )
                if not issues:
                    print("[INFO] No matching open issue found.")
                else:
                    issue = issues[0]
                    next_index = (int(state.get("last_worker_index", -1)) + 1) % len(workers)
                    assignee = workers[next_index]
                    state["last_worker_index"] = next_index
                    save_json_file(state_path, state)

                    ctx = build_runtime_context(issue, assignee, config)
                    key = ctx["issue_key"]
                    print(f"[INFO] Selected {key}: {ctx['issue_summary']}")
                    print(f"[INFO] Worker: {assignee['display_name']}")

                    if args.dry_run:
                        print("[DRY-RUN] Would assign, transition, run implement/review commands (with fallback), and post comments.")
                    else:
                        jira.assign_issue(key, assignee["account_id"])
                        jira.transition_issue(key, in_progress_id)
                        jira.add_comment(key, render_template(start_comment_tmpl, ctx))

                        implement_exec = run_step_with_fallback("implement", implement_cmd, ctx, command_timeout_seconds)
                        implement_res = implement_exec.result
                        if implement_res.returncode != 0:
                            fail_ctx = dict(ctx)
                            fail_ctx["implement_runner"] = implement_exec.runner
                            fail_ctx["implement_output"] = implement_res.combined_output[:3000]
                            jira.add_comment(key, render_template(impl_fail_comment_tmpl, fail_ctx))
                            print(f"[WARN] Implement command failed for {key}.")
                        else:
                            review_exec = run_step_with_fallback("review", review_cmd, ctx, command_timeout_seconds)
                            review_res = review_exec.result
                            review_ok = determine_review_pass(review_res, pass_pattern, fail_pattern)
                            if review_ok:
                                jira.transition_issue(key, done_id)
                                jira.add_comment(key, render_template(done_comment_tmpl, ctx))
                                print(f"[OK] {key} moved to Done.")
                            else:
                                fail_ctx = dict(ctx)
                                fail_ctx["review_runner"] = review_exec.runner
                                fail_ctx["review_output"] = review_res.combined_output[:3000]
                                jira.add_comment(key, render_template(fail_comment_tmpl, fail_ctx))
                                print(f"[WARN] Review failed for {key}; left active.")

                cycles += 1
                if args.once or int(config.get("max_cycles", 0)) == cycles:
                    break
                time.sleep(poll_seconds)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
