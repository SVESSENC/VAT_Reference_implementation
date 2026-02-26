# Jira Integration

Use the bundled script to batch assignee updates, ticket transitions, and comments at the end of a work session.

## Environment variables

Set these before running:

- `JIRA_BASE_URL` (example: `https://datahubdev.atlassian.net`)
- `JIRA_EMAIL` (Atlassian account email)
- `JIRA_API_TOKEN` (Atlassian API token)

Optional:

- `JIRA_PROJECT_KEY` (used only for reporting)
- `JIRA_SLEEP_SECONDS` (default delay between API calls, default `2.0`)

## Plan file format

Create a JSON plan file:

```json
{
  "assignees": [
    { "issue": "TC-18", "email": "gusv@netcompany.com" },
    { "issue": "TC-19", "account_id": "<jira-account-id>" },
    { "issue": "TC-20", "unassign": true }
  ],
  "moves": [
    { "issue": "TC-15", "to": "Done" },
    { "issue": "TC-10", "to": "In Progress" }
  ],
  "comments": [
    {
      "issue": "TC-10",
      "body": "Started on branch: feature/TC-10-prompt-templates"
    }
  ]
}
```

Assignee rules:
- Provide exactly one of `email`, `account_id`, or `unassign: true`.
- `email` is resolved to Jira `accountId` at runtime.
- Use `account_id` directly if email lookup is ambiguous or restricted.

## Run

```powershell
py C:\Users\gusv\.codex\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.json
```

Dry-run:

```powershell
py C:\Users\gusv\.codex\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.json --dry-run
```

## Start-Work Flow (pick ticket and launch execution brief)

Use the start-flow script when beginning a session. It will:

1. Pick a ticket (`--issue` or first Open via JQL)
2. Infer module + owner agent
3. Build a feature branch name
4. Move ticket to `In Progress` and add a start comment
5. Generate an agent-ready markdown brief

Run:

```powershell
py .\skills\project-leader-agent\scripts\jira_start_flow.py --issue TC-10 --output .\.claude\prompts\jira-start-brief-TC-10.md
```

Auto-pick next Open ticket:

```powershell
py .\skills\project-leader-agent\scripts\jira_start_flow.py --output .\.claude\prompts\jira-start-brief.md
```

Dry-run:

```powershell
py .\skills\project-leader-agent\scripts\jira_start_flow.py --issue TC-10 --dry-run
```

Then start the selected owner agent using the generated brief in `.claude/prompts/`.

## Default transition map

The script ships with this status-to-transition map:

- `Done` -> `151`
- `In Progress` -> `181`
- `In Review` -> `211`
- `Rejected` -> `171`
- `Cancelled` -> `191`
- `Open` -> `201`

Use `--transition-map-file` to override with your own JSON map when your Jira workflow differs.
