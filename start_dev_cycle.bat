@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "LOG_DIR=logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TS=%%I"
set "LOG_FILE=%LOG_DIR%\dev-cycle-%TS%.log"
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

if /I "%~1"=="--dry-run" (
  set "DRY_RUN_ARG=--dry-run"
) else (
  set "ISSUE_ARG=%~1"
)
if /I "%~2"=="--dry-run" set "DRY_RUN_ARG=--dry-run"

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
