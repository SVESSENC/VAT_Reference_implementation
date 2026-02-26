#!/usr/bin/env python3
"""
Batch Jira assignees, transitions, and comments with retry/backoff handling.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TRANSITIONS = {
    "Done": "151",
    "In Progress": "181",
    "In Review": "211",
    "Rejected": "171",
    "Cancelled": "191",
    "Open": "201",
}

BACKOFF_SECONDS = [15, 30, 60, 120]


def _env_or_arg(value: str | None, env_key: str) -> str:
    resolved = value or os.getenv(env_key)
    if not resolved:
        raise ValueError(f"Missing required value: --{env_key.lower().replace('_', '-')} or {env_key}")
    return resolved


def _auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return f"Basic {base64.b64encode(raw).decode('ascii')}"


def _parse_retry_after(headers: urllib.error.HTTPError.headers) -> float | None:  # type: ignore[type-arg]
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
            now_ts = datetime.now(timezone.utc).timestamp()
            return max(reset_ts - now_ts, 0.0)
        except ValueError:
            pass

    return None


def _request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url=url, method=method, data=body, headers=headers)

    for attempt in range(len(BACKOFF_SECONDS) + 1):
        try:
            with urllib.request.urlopen(req) as response:
                response_bytes = response.read()
                if not response_bytes:
                    return None
                return json.loads(response_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            status = exc.code
            if status == 429:
                if attempt >= len(BACKOFF_SECONDS):
                    raise RuntimeError(f"429 retry budget exhausted for {method} {url}") from exc
                wait_seconds = _parse_retry_after(exc.headers)  # type: ignore[arg-type]
                if wait_seconds is None:
                    wait_seconds = BACKOFF_SECONDS[attempt]
                print(f"[WARN] 429 for {url}. Waiting {wait_seconds:.1f}s then retrying...", file=sys.stderr)
                time.sleep(wait_seconds)
                continue

            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{status} for {method} {url}: {error_body}") from exc

    return None


def _adf_comment(text: str) -> dict[str, Any]:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _resolve_account_id_by_email(
    base_url: str,
    headers: dict[str, str],
    email: str,
    cache: dict[str, str],
) -> str:
    if email in cache:
        return cache[email]

    query = urllib.parse.quote(email)
    url = f"{base_url}/rest/api/3/user/search/query?query={query}&maxResults=50"
    response = _request_json("GET", url, headers)
    if not isinstance(response, list):
        raise RuntimeError(f"Unexpected user search response for {email}")

    exact: list[dict[str, Any]] = []
    for item in response:
        if not isinstance(item, dict):
            continue
        email_address = str(item.get("emailAddress", "")).strip().lower()
        if email_address == email.lower():
            exact.append(item)

    candidates = exact if exact else [item for item in response if isinstance(item, dict)]
    if len(candidates) != 1:
        raise RuntimeError(
            f"Could not uniquely resolve Jira user for '{email}'. "
            f"Provide account_id directly in plan."
        )

    account_id = str(candidates[0].get("accountId", "")).strip()
    if not account_id:
        raise RuntimeError(f"Resolved Jira user for '{email}' but accountId was empty")

    cache[email] = account_id
    return account_id


def _normalize_plan(
    plan: dict[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]]:
    moves_raw = plan.get("moves", [])
    assignees_raw = plan.get("assignees", [])
    comments_raw = plan.get("comments", [])

    if not isinstance(moves_raw, list):
        raise ValueError("'moves' must be a list")
    if not isinstance(assignees_raw, list):
        raise ValueError("'assignees' must be a list")
    if not isinstance(comments_raw, list):
        raise ValueError("'comments' must be a list")

    moves: list[dict[str, str]] = []
    assignees: list[dict[str, Any]] = []
    comments: list[dict[str, str]] = []

    for item in moves_raw:
        if not isinstance(item, dict):
            raise ValueError("Each move must be an object")
        issue = str(item.get("issue", "")).strip()
        to_status = str(item.get("to", "")).strip()
        if not issue or not to_status:
            raise ValueError("Each move requires non-empty 'issue' and 'to'")
        moves.append({"issue": issue, "to": to_status})

    for item in assignees_raw:
        if not isinstance(item, dict):
            raise ValueError("Each assignee entry must be an object")
        issue = str(item.get("issue", "")).strip()
        account_id_raw = item.get("account_id")
        email_raw = item.get("email")
        unassign = bool(item.get("unassign", False))
        account_id = str(account_id_raw).strip() if account_id_raw is not None else ""
        email = str(email_raw).strip() if email_raw is not None else ""
        assignment_mode_count = int(bool(account_id)) + int(bool(email)) + int(unassign)
        if not issue:
            raise ValueError("Each assignee entry requires non-empty 'issue'")
        if assignment_mode_count != 1:
            raise ValueError(
                "Each assignee entry must provide exactly one of 'account_id', 'email', or 'unassign: true'"
            )
        assignee_item: dict[str, Any] = {"issue": issue, "unassign": unassign}
        if account_id:
            assignee_item["account_id"] = account_id
        if email:
            assignee_item["email"] = email
        assignees.append(assignee_item)

    for item in comments_raw:
        if not isinstance(item, dict):
            raise ValueError("Each comment must be an object")
        issue = str(item.get("issue", "")).strip()
        body = str(item.get("body", "")).strip()
        if not issue or not body:
            raise ValueError("Each comment requires non-empty 'issue' and 'body'")
        comments.append({"issue": issue, "body": body})

    return moves, assignees, comments


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply batched Jira assignees/transitions/comments from a JSON plan."
    )
    parser.add_argument("--plan-file", required=True, help="Path to JSON file containing moves/assignees/comments.")
    parser.add_argument("--base-url", help="Jira base URL. Falls back to JIRA_BASE_URL.")
    parser.add_argument("--email", help="Jira account email. Falls back to JIRA_EMAIL.")
    parser.add_argument("--token", help="Jira API token. Falls back to JIRA_API_TOKEN.")
    parser.add_argument("--transition-map-file", help="JSON file mapping status names to transition IDs.")
    parser.add_argument("--sleep-seconds", type=float, default=float(os.getenv("JIRA_SLEEP_SECONDS", "2.0")))
    parser.add_argument("--dry-run", action="store_true", help="Print intended operations without API calls.")
    args = parser.parse_args()

    try:
        plan = _load_json(Path(args.plan_file))
        moves, assignees, comments = _normalize_plan(plan)
    except Exception as exc:
        print(f"[ERROR] Failed to load plan: {exc}", file=sys.stderr)
        return 1

    transitions = dict(DEFAULT_TRANSITIONS)
    if args.transition_map_file:
        try:
            custom = _load_json(Path(args.transition_map_file))
            if not isinstance(custom, dict):
                raise ValueError("Transition map JSON must be an object")
            transitions.update({str(k): str(v) for k, v in custom.items()})
        except Exception as exc:
            print(f"[ERROR] Failed to load transition map: {exc}", file=sys.stderr)
            return 1

    if args.dry_run:
        print("[DRY-RUN] Planned assignees:")
        for assignee in assignees:
            if assignee.get("unassign"):
                target = "UNASSIGN"
            elif assignee.get("account_id"):
                target = f"account_id={assignee['account_id']}"
            else:
                target = f"email={assignee['email']} (resolved at runtime)"
            print(f"  - {assignee['issue']} -> {target}")
        print("[DRY-RUN] Planned transitions:")
        for move in moves:
            transition_id = transitions.get(move["to"])
            print(f"  - {move['issue']} -> {move['to']} (id={transition_id or 'UNKNOWN'})")
        print("[DRY-RUN] Planned comments:")
        for comment in comments:
            print(f"  - {comment['issue']}: {comment['body']}")
        return 0

    try:
        base_url = _env_or_arg(args.base_url, "JIRA_BASE_URL").rstrip("/")
        email = _env_or_arg(args.email, "JIRA_EMAIL")
        token = _env_or_arg(args.token, "JIRA_API_TOKEN")
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    headers = {
        "Authorization": _auth_header(email, token),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    print(
        f"[INFO] Applying {len(assignees)} assignees, {len(moves)} transitions, and {len(comments)} comments..."
    )

    assignee_cache: dict[str, str] = {}

    for assignee in assignees:
        issue = str(assignee["issue"])
        if assignee.get("unassign"):
            account_id: str | None = None
            target_text = "UNASSIGN"
        elif assignee.get("account_id"):
            account_id = str(assignee["account_id"])
            target_text = account_id
        else:
            email_value = str(assignee["email"])
            try:
                account_id = _resolve_account_id_by_email(base_url, headers, email_value, assignee_cache)
            except Exception as exc:
                print(f"[ERROR] Failed to resolve assignee email '{email_value}': {exc}", file=sys.stderr)
                return 1
            target_text = f"{email_value} ({account_id})"

        url = f"{base_url}/rest/api/3/issue/{urllib.parse.quote(issue)}/assignee"
        payload = {"accountId": account_id}
        try:
            _request_json("PUT", url, headers, payload)
            print(f"[OK] Assigned {issue} -> {target_text}")
        except Exception as exc:
            print(f"[ERROR] Failed assignee update {issue}: {exc}", file=sys.stderr)
            return 1
        time.sleep(max(args.sleep_seconds, 0.0))

    for move in moves:
        transition_id = transitions.get(move["to"])
        if not transition_id:
            print(
                f"[ERROR] Unknown transition for status '{move['to']}'. "
                f"Provide --transition-map-file with this status mapping.",
                file=sys.stderr,
            )
            return 1

        url = f"{base_url}/rest/api/3/issue/{urllib.parse.quote(move['issue'])}/transitions"
        payload = {"transition": {"id": transition_id}}
        try:
            _request_json("POST", url, headers, payload)
            print(f"[OK] Transitioned {move['issue']} -> {move['to']}")
        except Exception as exc:
            print(f"[ERROR] Failed transition {move['issue']} -> {move['to']}: {exc}", file=sys.stderr)
            return 1
        time.sleep(max(args.sleep_seconds, 0.0))

    for comment in comments:
        url = f"{base_url}/rest/api/3/issue/{urllib.parse.quote(comment['issue'])}/comment"
        payload = {"body": _adf_comment(comment["body"])}
        try:
            _request_json("POST", url, headers, payload)
            print(f"[OK] Comment added to {comment['issue']}")
        except Exception as exc:
            print(f"[ERROR] Failed comment on {comment['issue']}: {exc}", file=sys.stderr)
            return 1
        time.sleep(max(args.sleep_seconds, 0.0))

    print("[INFO] Jira batch update complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
