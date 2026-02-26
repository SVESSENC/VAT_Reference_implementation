# Autonomous Project Manager Loop

This project supports a local orchestrator that can continuously pick the next Jira task, assign it, run implementation/review commands, and update Jira status.

## What it can do

1. Poll Jira for the next `Open` ticket (configurable JQL).
2. Assign that ticket to a worker from a configured pool (round-robin).
3. Move it to `In Progress`.
4. Run an implementation command.
5. Run a review command.
6. If review passes, move ticket to `Done`; if review fails, leave it active and comment details.
7. If Claude hits token/rate limits, automatically reroute command execution to Codex (configurable fallback).

## Safety constraints

- Uses a lock file so only one loop instance runs at a time.
- Uses retry/backoff for Jira rate limits.
- Requires explicit PASS pattern in review output.
- Writes state to `.auto-pm-state.json` for deterministic worker rotation.

## Setup

1. Configure Jira credentials in `.env.jira.local`:
   - `JIRA_BASE_URL`
   - `JIRA_EMAIL`
   - `JIRA_API_TOKEN`
2. Copy config template:
   - `Copy-Item automation/auto-project-manager.example.json automation/auto-project-manager.local.json`
3. Edit `automation/auto-project-manager.local.json`:
   - `worker_display_names`
   - `selection_jql`
   - `commands.implement.primary` (Claude command)
   - `commands.implement.fallback` (Codex command)
   - `commands.review.primary` (Claude command)
   - `commands.review.fallback` (Codex command)

## Run once (safe dry-run)

```powershell
py automation/auto_project_manager.py --config automation/auto-project-manager.local.json --dry-run --once
```

## Run continuously

```powershell
py automation/auto_project_manager.py --config automation/auto-project-manager.local.json
```

## Important

- The loop only automates orchestration. It does not inherently create code unless your configured implementation command invokes an AI coding agent or script that writes code.
- Keep merge/deploy approval manual until you trust the loop behavior.
- Fallback is pattern-driven. Default patterns include common Claude limit responses (`hit your limit`, `usage limit`, `quota`, `rate limit`).
