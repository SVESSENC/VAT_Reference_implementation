#!/usr/bin/env python3
"""
Pick a Jira ticket and prepare an agent execution brief.

Flow:
1. Select ticket (explicit --issue or first Open from JQL).
2. Infer module and owner agent from ticket content.
3. Build feature branch name.
4. Transition ticket to In Progress + add start comment (unless --dry-run).
5. Write an agent-ready markdown brief.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_JQL = 'project = TC AND status = "Open" ORDER BY priority DESC, created ASC'
IN_PROGRESS_TRANSITION_ID = "181"


def _env_or_arg(value: str | None, env_key: str) -> str:
    resolved = value or os.getenv(env_key)
    if not resolved:
        raise ValueError(f"Missing required value: --{env_key.lower().replace('_', '-')} or {env_key}")
    return resolved


def _auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return f"Basic {base64.b64encode(raw).decode('ascii')}"


def _request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any] | None:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, method=method, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{exc.code} for {method} {url}: {error_body}") from exc


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


def _text_from_adf(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_text_from_adf(item) for item in node)
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type")
    if node_type == "text":
        return str(node.get("text", ""))
    if node_type == "hardBreak":
        return "\n"

    content = node.get("content")
    if isinstance(content, list):
        parts = [_text_from_adf(item) for item in content]
        text = "".join(parts)
        if node_type in {"paragraph", "heading", "listItem"}:
            return text + "\n"
        return text
    return ""


def _extract_description(fields: dict[str, Any]) -> str:
    description = fields.get("description")
    if description is None:
        return ""
    if isinstance(description, str):
        return description.strip()
    text = _text_from_adf(description).strip()
    return re.sub(r"\n{3,}", "\n\n", text)


def _extract_acceptance_criteria(fields: dict[str, Any], description_text: str) -> str:
    custom_value = fields.get("customfield_10000")
    if isinstance(custom_value, str) and custom_value.strip():
        return custom_value.strip()

    pattern = re.compile(
        r"(acceptance criteria|ac)\s*[:\-]\s*(.+)$",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(description_text)
    if not match:
        return ""
    return match.group(2).strip()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug[:60] if slug else "work-item"


def _contains_keyword(text_lower: str, keyword: str) -> bool:
    keyword = keyword.lower()
    if " " in keyword:
        return keyword in text_lower
    return bool(re.search(rf"\b{re.escape(keyword)}\b", text_lower))


def _contains_any(text_lower: str, keywords: list[str]) -> bool:
    return any(_contains_keyword(text_lower, kw) for kw in keywords)


def _infer_module(text: str) -> tuple[str, str]:
    text_lower = text.lower()
    keyword_groups = [
        ("shared", ["shared types", "shared constants", "vatinput", "vatoutput"]),
        ("frontend", ["frontend", "ui", "form", "component", "display"]),
        ("api", ["api", "endpoint", "route", "request", "validation", "rest"]),
        (
            "engine",
            [
                "engine",
                "vat logic",
                "calculation",
                "jurisdiction",
                "rate",
                "exemption",
                "reverse charge",
            ],
        ),
    ]
    for module, keywords in keyword_groups:
        if _contains_any(text_lower, keywords):
            if module == "shared":
                return module, "Mentions shared scope; requires team sign-off before coding."
            return module, "Keyword-based inference from ticket text."
    return "unknown", "No strong module keywords found."


def _infer_owner_agent(text: str) -> tuple[str, str]:
    text_lower = text.lower()
    rules = [
        ("db-expert-agent", ["database", "db", "schema", "index", "migration", "query"]),
        ("devops-agent", ["deploy", "pipeline", "ci", "cd", "infra", "observability", "rollback"]),
        ("tester-agent", ["test", "qa", "regression", "coverage", "integration test"]),
        ("architect-agent", ["architecture", "adr", "system design", "component boundary"]),
        ("critic-agent", ["review", "audit", "risk analysis", "quality gate"]),
    ]
    for agent, keywords in rules:
        if _contains_any(text_lower, keywords):
            return agent, "Keyword-based role routing."
    return "developer-agent", "Default execution owner for implementation work."


def _module_scope(module: str) -> str:
    scopes = {
        "engine": "/src/engine/** and /tests/engine/**",
        "api": "/src/api/** and /tests/api/**",
        "frontend": "/src/frontend/**",
        "shared": "/src/shared/** (team sign-off required before changes)",
        "unknown": "Module unclear; resolve before coding.",
    }
    return scopes.get(module, "Module unclear; resolve before coding.")


def _build_brief(
    issue_key: str,
    summary: str,
    description: str,
    acceptance_criteria: str,
    module: str,
    module_reason: str,
    owner_agent: str,
    owner_reason: str,
    branch_name: str,
    comment_body: str,
) -> str:
    ac_text = acceptance_criteria if acceptance_criteria else "Not explicitly provided in Jira fields."
    desc_text = description if description else "No description provided."

    return f"""# Jira Start Brief: {issue_key}

## Ticket
- Key: `{issue_key}`
- Summary: {summary}
- Branch: `{branch_name}`

## Routing
- Module: `{module}` ({module_reason})
- Owner agent: `{owner_agent}` ({owner_reason})
- Allowed scope: `{_module_scope(module)}`

## Description
{desc_text}

## Acceptance Criteria
{ac_text}

## Jira Start Comment
{comment_body}

## Start Prompt
Use `${owner_agent}` on ticket `{issue_key}`.

You are working on module `{module}`.
Scope is strictly `{_module_scope(module)}`.

Objective:
- Implement ticket `{issue_key}`: {summary}

Requirements:
- Follow `CLAUDE.md` and `docs/agent-rules.md` guardrails.
- If module is `shared` or `unknown`, stop and ask for confirmation before coding.
- If any contract/rule is unclear, stop and ask rather than guessing.

Deliverables:
- Implementation (or design/review output if role-specific)
- Verification evidence
- Risks and open questions
"""


def _fetch_issue_by_jql(base_url: str, headers: dict[str, str], jql: str) -> dict[str, Any]:
    url = f"{base_url}/rest/api/3/search/jql"
    payload = {
        "jql": jql,
        "maxResults": 1,
        "fields": ["summary", "description", "status"],
    }
    response = _request_json("POST", url, headers, payload)
    if not isinstance(response, dict):
        raise RuntimeError("Unexpected Jira search response")
    issues = response.get("issues", [])
    if not isinstance(issues, list) or not issues:
        raise RuntimeError(f"No issues returned for JQL: {jql}")
    issue = issues[0]
    if not isinstance(issue, dict):
        raise RuntimeError("Unexpected issue structure in Jira search response")
    return issue


def _fetch_issue_by_key(base_url: str, headers: dict[str, str], issue_key: str) -> dict[str, Any]:
    issue_quoted = urllib.parse.quote(issue_key)
    url = f"{base_url}/rest/api/3/issue/{issue_quoted}?fields=summary,description,status"
    response = _request_json("GET", url, headers)
    if not isinstance(response, dict):
        raise RuntimeError(f"Unexpected Jira issue response for {issue_key}")
    return response


def _transition_in_progress(base_url: str, headers: dict[str, str], issue_key: str) -> None:
    issue_quoted = urllib.parse.quote(issue_key)
    url = f"{base_url}/rest/api/3/issue/{issue_quoted}/transitions"
    payload = {"transition": {"id": IN_PROGRESS_TRANSITION_ID}}
    _request_json("POST", url, headers, payload)


def _add_comment(base_url: str, headers: dict[str, str], issue_key: str, comment_text: str) -> None:
    issue_quoted = urllib.parse.quote(issue_key)
    url = f"{base_url}/rest/api/3/issue/{issue_quoted}/comment"
    payload = {"body": _adf_comment(comment_text)}
    _request_json("POST", url, headers, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pick a Jira ticket and generate an agent start brief.")
    parser.add_argument("--issue", help="Explicit issue key (e.g., TC-10). If omitted, uses first Open via JQL.")
    parser.add_argument("--jql", default=DEFAULT_JQL, help="JQL used when --issue is not provided.")
    parser.add_argument("--base-url", help="Jira base URL. Falls back to JIRA_BASE_URL.")
    parser.add_argument("--email", help="Jira email. Falls back to JIRA_EMAIL.")
    parser.add_argument("--token", help="Jira token. Falls back to JIRA_API_TOKEN.")
    parser.add_argument(
        "--output",
        default=".claude/prompts/jira-start-brief.md",
        help="Output markdown brief path.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not transition/comment in Jira.")
    args = parser.parse_args()

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

    try:
        issue = (
            _fetch_issue_by_key(base_url, headers, args.issue)
            if args.issue
            else _fetch_issue_by_jql(base_url, headers, args.jql)
        )
    except Exception as exc:
        print(f"[ERROR] Could not fetch Jira issue: {exc}", file=sys.stderr)
        return 1

    issue_key = str(issue.get("key", "")).strip()
    fields = issue.get("fields", {})
    if not issue_key or not isinstance(fields, dict):
        print("[ERROR] Jira issue response missing key/fields", file=sys.stderr)
        return 1

    summary = str(fields.get("summary", "")).strip() or "(no summary)"
    description = _extract_description(fields)
    acceptance_criteria = _extract_acceptance_criteria(fields, description)

    inference_text = f"{summary}\n\n{description}\n\n{acceptance_criteria}"
    module, module_reason = _infer_module(inference_text)
    owner_agent, owner_reason = _infer_owner_agent(inference_text)
    branch_name = f"feature/{issue_key}-{_slugify(summary)}"
    comment_body = f"Started on branch: {branch_name}\nScope: {summary}"

    if args.dry_run:
        print(f"[DRY-RUN] Would transition {issue_key} -> In Progress (id={IN_PROGRESS_TRANSITION_ID})")
        print(f"[DRY-RUN] Would add comment on {issue_key}: {comment_body}")
    else:
        try:
            _transition_in_progress(base_url, headers, issue_key)
            _add_comment(base_url, headers, issue_key, comment_body)
            print(f"[OK] Transitioned {issue_key} -> In Progress")
            print(f"[OK] Comment added to {issue_key}")
        except Exception as exc:
            print(f"[ERROR] Jira start flow failed: {exc}", file=sys.stderr)
            return 1

    brief = _build_brief(
        issue_key=issue_key,
        summary=summary,
        description=description,
        acceptance_criteria=acceptance_criteria,
        module=module,
        module_reason=module_reason,
        owner_agent=owner_agent,
        owner_reason=owner_reason,
        branch_name=branch_name,
        comment_body=comment_body,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(brief, encoding="utf-8")

    print(f"[INFO] Selected issue: {issue_key}")
    print(f"[INFO] Suggested branch: {branch_name}")
    print(f"[INFO] Inferred module: {module}")
    print(f"[INFO] Owner agent: {owner_agent}")
    print(f"[INFO] Brief written: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
