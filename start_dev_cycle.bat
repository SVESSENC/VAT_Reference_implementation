@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "LOG_DIR=logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TS=%%I"
set "LOG_FILE=%LOG_DIR%\dev-cycle-%TS%-%RANDOM%.log"
set "OUTPUT_FILE=.claude\prompts\jira-start-brief.md"
set "METADATA_FILE=.claude\prompts\jira-start-brief.json"

call :log "=== Development Cycle Start ==="
call :log "Repo: %CD%"
call :log "Log: %LOG_FILE%"

if not exist ".env.jira.local" (
  call :log "[ERROR] Missing .env.jira.local"
  exit /b 1
)

call :log "[INFO] Loading Jira environment from .env.jira.local"
for /f "usebackq tokens=1,* delims==" %%A in (".env.jira.local") do (
  set "K=%%~A"
  set "V=%%~B"
  if defined K (
    if not "!K:~0,1!"=="#" (
      for /f "tokens=* delims= " %%K in ("!K!") do set "K=%%K"
      if defined K (
        set "V=!V:"=!"
        set "!K!=!V!"
      )
    )
  )
)

if not defined JIRA_BASE_URL (
  call :log "[ERROR] JIRA_BASE_URL not set after loading .env.jira.local"
  exit /b 1
)
if not defined JIRA_EMAIL (
  call :log "[ERROR] JIRA_EMAIL not set after loading .env.jira.local"
  exit /b 1
)
if not defined JIRA_API_TOKEN (
  call :log "[ERROR] JIRA_API_TOKEN not set after loading .env.jira.local"
  exit /b 1
)

set "ISSUE_ARG="
set "DRY_RUN_ARG="
set "RUN_AGENT=1"
for %%A in (%*) do (
  if /I "%%~A"=="--dry-run" set "DRY_RUN_ARG=--dry-run"
  if /I "%%~A"=="--no-agent" set "RUN_AGENT=0"
  if /I not "%%~A"=="--dry-run" if /I not "%%~A"=="--no-agent" if not defined ISSUE_ARG set "ISSUE_ARG=%%~A"
)

if defined ISSUE_ARG (
  call :log "[INFO] Running Jira start flow for issue: %ISSUE_ARG%"
  call :run_and_log py .\skills\project-leader-agent\scripts\jira_start_flow.py --issue %ISSUE_ARG% --output %OUTPUT_FILE% --metadata-output %METADATA_FILE% %DRY_RUN_ARG%
) else (
  call :log "[INFO] Running Jira start flow for next Open ticket"
  call :run_and_log py .\skills\project-leader-agent\scripts\jira_start_flow.py --output %OUTPUT_FILE% --metadata-output %METADATA_FILE% %DRY_RUN_ARG%
)

if errorlevel 1 (
  call :log "[ERROR] Start flow failed. Check the log above."
  exit /b 1
)

if not exist "%METADATA_FILE%" (
  call :log "[ERROR] Missing metadata file: %METADATA_FILE%"
  exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%A in (`powershell -NoProfile -Command "$m=Get-Content -Raw '%METADATA_FILE%' | ConvertFrom-Json; Write-Output ('ISSUE='+$m.issue); Write-Output ('BRANCH='+$m.branch); Write-Output ('OWNER_AGENT='+$m.owner_agent); Write-Output ('MODULE='+$m.module)"`) do (
  set "%%A=%%B"
)

if not defined ISSUE (
  call :log "[ERROR] Could not parse issue from metadata."
  exit /b 1
)
if not defined BRANCH (
  call :log "[ERROR] Could not parse branch from metadata."
  exit /b 1
)
if not defined OWNER_AGENT (
  call :log "[ERROR] Could not parse owner agent from metadata."
  exit /b 1
)

if defined DRY_RUN_ARG (
  call :log "[INFO] Dry-run mode: skipping git branch changes."
) else (
  call :log "[INFO] Creating/switching to branch: !BRANCH!"
  git show-ref --verify --quiet refs/heads/!BRANCH!
  if !errorlevel! equ 0 (
    call :run_and_log git checkout !BRANCH!
  ) else (
    call :run_and_log git checkout -b !BRANCH!
  )
  if errorlevel 1 (
    call :log "[ERROR] Git branch step failed."
    exit /b 1
  )

  git ls-remote --exit-code --heads origin !BRANCH! >nul 2>&1
  if !errorlevel! equ 0 (
    call :log "[INFO] Branch already exists on origin: !BRANCH! ; skipping kickoff push"
  ) else (
    call :log "[INFO] Creating kickoff commit so branch is visible on GitHub."
    call :run_and_log git commit --allow-empty -m "chore: start !ISSUE! development cycle"
    if errorlevel 1 (
      call :log "[ERROR] Kickoff commit failed."
      exit /b 1
    )
    call :run_and_log git push -u origin !BRANCH!
    if errorlevel 1 (
      call :log "[ERROR] Kickoff push failed."
      exit /b 1
    )
  )

  set "PR_BASE=dev"
  set "PR_TITLE=feat: !ISSUE! automated cycle"
  set "PR_BODY=Auto-created by start_dev_cycle.bat for !ISSUE!."
  call :log "[INFO] Ensuring PR exists for !BRANCH! -> !PR_BASE!."
  where gh >nul 2>&1
  if !errorlevel! equ 0 (
    call :run_and_log gh pr view --head !BRANCH! --base !PR_BASE!
    if errorlevel 1 (
      call :run_and_log gh pr create --base !PR_BASE! --head !BRANCH! --title "!PR_TITLE!" --body "!PR_BODY!"
      if errorlevel 1 (
        call :log "[WARN] Could not auto-create PR with gh."
      )
    ) else (
      call :log "[INFO] PR already exists for branch !BRANCH!."
    )
  ) else (
    for /f "usebackq delims=" %%U in (`powershell -NoProfile -Command "$u=(git remote get-url origin).Trim(); if($u -match 'github.com[:/](.+)$'){ $p=($Matches[1] -replace '\\.git$',''); 'https://github.com/' + $p + '/compare/!PR_BASE!...!BRANCH!?expand=1' }"`) do set "PR_URL=%%U"
    if defined PR_URL (
      call :log "[WARN] Auto PR skipped. Install/auth gh CLI to enable automatic creation."
      call :log "[INFO] PR create URL: !PR_URL!"
    )
  )
)

set "SKILLS=!OWNER_AGENT!,reviewer-agent"
if /I "!OWNER_AGENT!"=="reviewer-agent" set "SKILLS=reviewer-agent"
if /I "!OWNER_AGENT!"=="critic-agent" set "SKILLS=critic-agent,reviewer-agent"
set "SESSION_PROMPT=.claude\prompts\active-session-!ISSUE!.md"

call :log "[INFO] Building agent session prompt for skills: !SKILLS!"
call :run_and_log py .\claude-skills\build_prompt.py --skills !SKILLS! --include-references --output !SESSION_PROMPT!
if errorlevel 1 (
  call :log "[ERROR] Failed to build owner-agent session prompt."
  exit /b 1
)

if exist "!SESSION_PROMPT!" (
  call :log "[INFO] Opening generated session prompt: !SESSION_PROMPT!"
  start "" "!SESSION_PROMPT!"
)

if defined DRY_RUN_ARG (
  call :log "[INFO] Dry-run mode: skipping agent execution."
) else (
  if "!RUN_AGENT!"=="1" (
    where codex >nul 2>&1
    if errorlevel 1 (
      call :log "[ERROR] codex CLI not found. Cannot auto-run owner agent."
      exit /b 1
    )
    set "MAX_REVIEW_CYCLES=3"
    set "REVIEW_RESULT=.claude\prompts\review-result-!ISSUE!.txt"
    set "REVIEW_VERDICT=UNKNOWN"
    set "PASS_REACHED=0"

    for /L %%R in (1,1,!MAX_REVIEW_CYCLES!) do (
      if "!PASS_REACHED!"=="1" (
        rem PASS already reached; skip remaining cycles.
      ) else (
        if "%%R"=="1" (
          call :log "[INFO] Starting owner agent run via codex exec ; cycle %%R/!MAX_REVIEW_CYCLES!."
          call :run_and_log codex -C "%CD%" exec --dangerously-bypass-approvals-and-sandbox "Read .claude\\prompts\\active-session-!ISSUE!.md and .claude\\prompts\\jira-start-brief.md from the repository, then start working on the ticket now."
        ) else (
          set "RETRY_PROMPT=.claude\prompts\retry-fix-!ISSUE!.md"
          > "!RETRY_PROMPT!" echo Ticket !ISSUE! failed reviewer gate.
          >>"!RETRY_PROMPT!" echo You must fix all findings below before the next review.
          >>"!RETRY_PROMPT!" echo.
          >>"!RETRY_PROMPT!" echo Reviewer findings:
          >>"!RETRY_PROMPT!" echo -----------------
          type "!REVIEW_RESULT!" >> "!RETRY_PROMPT!"
          call :log "[INFO] Re-running owner agent after review FAIL ; cycle %%R/!MAX_REVIEW_CYCLES!."
          call :run_and_log codex -C "%CD%" exec --dangerously-bypass-approvals-and-sandbox "You are developer-agent. Read !RETRY_PROMPT!, fix every reviewer finding in repo code, and keep changes within the ticket scope."
        )
        if errorlevel 1 (
          call :log "[ERROR] Owner agent run failed."
          exit /b 1
        )

        call :log "[INFO] Running reviewer pass/fail check."
        call :run_and_log codex -C "%CD%" exec --dangerously-bypass-approvals-and-sandbox -o !REVIEW_RESULT! "You are review-agent. Review ticket !ISSUE! changes in this repo. Respond with PASS or FAIL on the first line, then concise findings."
        if errorlevel 1 (
          call :log "[ERROR] Reviewer agent run failed."
          exit /b 1
        )

        set "REVIEW_VERDICT=UNKNOWN"
        for /f "usebackq delims=" %%V in (`powershell -NoProfile -Command "$l=Get-Content -Path '!REVIEW_RESULT!' | Where-Object { $_.Trim() -ne '' } | Select-Object -First 1; if($null -eq $l){ 'UNKNOWN' } elseif($l.Trim().ToUpper().StartsWith('PASS')){ 'PASS' } elseif($l.Trim().ToUpper().StartsWith('FAIL')){ 'FAIL' } else { 'UNKNOWN' }"`) do set "REVIEW_VERDICT=%%V"
        call :log "[INFO] Reviewer verdict: !REVIEW_VERDICT!"

        if /I "!REVIEW_VERDICT!"=="PASS" set "PASS_REACHED=1"
      )
    )

    set "JIRA_PLAN=.claude\prompts\jira-auto-close-!ISSUE!.json"
    set "FINAL_STATUS=In Review"
    if /I "!PASS_REACHED!"=="1" (
      > "!JIRA_PLAN!" echo {
      >>"!JIRA_PLAN!" echo   "moves": [
      >>"!JIRA_PLAN!" echo     { "issue": "!ISSUE!", "to": "Done" }
      >>"!JIRA_PLAN!" echo   ],
      >>"!JIRA_PLAN!" echo   "comments": [
      >>"!JIRA_PLAN!" echo     { "issue": "!ISSUE!", "body": "Review: reviewer-agent PASS. Auto-closed by start_dev_cycle.bat." }
      >>"!JIRA_PLAN!" echo   ]
      >>"!JIRA_PLAN!" echo }
      call :log "[INFO] Applying Jira close plan Done for !ISSUE!."
      set "FINAL_STATUS=Done"
    ) else (
      > "!JIRA_PLAN!" echo {
      >>"!JIRA_PLAN!" echo   "moves": [
      >>"!JIRA_PLAN!" echo     { "issue": "!ISSUE!", "to": "In Review" }
      >>"!JIRA_PLAN!" echo   ],
      >>"!JIRA_PLAN!" echo   "comments": [
      >>"!JIRA_PLAN!" echo     { "issue": "!ISSUE!", "body": "Review: reviewer-agent !REVIEW_VERDICT!. Max retries reached; moved to In Review by start_dev_cycle.bat." }
      >>"!JIRA_PLAN!" echo   ]
      >>"!JIRA_PLAN!" echo }
      call :log "[INFO] Max retries reached. Applying Jira review plan In Review for !ISSUE!."
    )

    call :run_and_log py .\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file !JIRA_PLAN!
    if errorlevel 1 (
      call :log "[ERROR] Jira auto-transition failed."
      exit /b 1
    )

    set "REPORT_DIR=finished-tickets"
    set "REPORT_FILE=!REPORT_DIR!\!ISSUE!.md"
    set "ROADMAP_FILE=!REPORT_DIR!\ROADMAP.md"
    if not exist "!REPORT_DIR!" mkdir "!REPORT_DIR!"

    call :log "[INFO] Writing ticket report markdown: !REPORT_FILE!"
    call :run_and_log powershell -NoProfile -Command "$issue='!ISSUE!'; $branch='!BRANCH!'; $module='!MODULE!'; $owner='!OWNER_AGENT!'; $status='!FINAL_STATUS!'; $verdict='!REVIEW_VERDICT!'; $log='!LOG_FILE!'; $review=''; if(Test-Path '!REVIEW_RESULT!'){ $review = Get-Content -Raw '!REVIEW_RESULT!' }; $changes = git status --short; if(-not $changes){ $changes='(no local changes)' }; $md = @(); $md += '# ' + $issue + ' - Cycle Report'; $md += ''; $md += '- Date: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'); $md += '- Branch: `' + $branch + '`'; $md += '- Module: `' + $module + '`'; $md += '- Owner Agent: `' + $owner + '`'; $md += '- Reviewer Verdict: `' + $verdict + '`'; $md += '- Jira Status Applied: `' + $status + '`'; $md += '- Log File: `' + $log + '`'; $md += ''; $md += '## Implementation Summary'; $md += '- Automated cycle executed for ' + $issue + '.'; $md += '- See changed files and review findings below.'; $md += ''; $md += '## Changed Files Snapshot'; $md += '```text'; $md += $changes; $md += '```'; $md += ''; $md += '## Reviewer Comments'; $md += '```text'; if([string]::IsNullOrWhiteSpace($review)){ $md += '(no reviewer output captured)'} else { $md += $review.TrimEnd() }; $md += '```'; Set-Content -Path '!REPORT_FILE!' -Value ($md -join [Environment]::NewLine)"
    if errorlevel 1 (
      call :log "[ERROR] Failed writing ticket report markdown."
      exit /b 1
    )

    call :log "[INFO] Updating roadmap checklist: !ROADMAP_FILE!"
    call :run_and_log powershell -NoProfile -Command "$issue='!ISSUE!'; $status='!FINAL_STATUS!'; $branch='!BRANCH!'; $check = if($status -eq 'Done'){ '[x]' } else { '[ ]' }; $line = '- ' + $check + ' ' + $issue + ' - ' + $status + ' - ' + $branch; if(-not (Test-Path '!ROADMAP_FILE!')){ Set-Content -Path '!ROADMAP_FILE!' -Value @('# Ticket Roadmap','','- [ ] TEMPLATE - status - branch') }; $rows = Get-Content '!ROADMAP_FILE!'; $updated = $false; for($i=0; $i -lt $rows.Count; $i++){ if($rows[$i] -match ('^- \\[[ x]\\] ' + [regex]::Escape($issue) + '\\b')){ $rows[$i] = $line; $updated = $true } }; if(-not $updated){ $rows += $line }; Set-Content -Path '!ROADMAP_FILE!' -Value $rows"
    if errorlevel 1 (
      call :log "[ERROR] Failed updating roadmap checklist."
      exit /b 1
    )
  ) else (
    call :log "[INFO] --no-agent set: skipping owner agent execution."
  )
)

call :log "[INFO] Development cycle bootstrapped for !ISSUE!."
call :log "[INFO] Module: !MODULE! ; Owner agent: !OWNER_AGENT!"
call :log "[INFO] End session command: end_dev_cycle.bat"
call :log "=== Development Cycle Ready ==="

exit /b 0

:run_and_log
set "CMD=%*"
set "TMP_OUT=%LOG_DIR%\run-%RANDOM%-%RANDOM%.log"
cmd /c "%CMD%" > "%TMP_OUT%" 2>&1
set "RC=%errorlevel%"
type "%TMP_OUT%"
type "%TMP_OUT%" >> "%LOG_FILE%"
del /q "%TMP_OUT%" >nul 2>&1
exit /b %RC%

:log
if "%~1"=="" (
  echo.
  >>"%LOG_FILE%" echo.
) else (
  echo %~1
  >>"%LOG_FILE%" echo %~1
)
exit /b 0
