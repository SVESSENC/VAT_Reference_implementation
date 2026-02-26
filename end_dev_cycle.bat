@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "LOG_DIR=logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TS=%%I"
set "LOG_FILE=%LOG_DIR%\dev-cycle-end-%TS%.log"

echo === Development Cycle End ===
>>"%LOG_FILE%" echo === Development Cycle End ===
echo Repo: %CD%
>>"%LOG_FILE%" echo Repo: %CD%
echo Log: %LOG_FILE%
>>"%LOG_FILE%" echo Log: %LOG_FILE%

if not exist ".env.jira.local" (
  echo [ERROR] Missing .env.jira.local
  >>"%LOG_FILE%" echo [ERROR] Missing .env.jira.local
  exit /b 1
)
if not exist "jira-plan.local.json" (
  echo [ERROR] Missing jira-plan.local.json
  >>"%LOG_FILE%" echo [ERROR] Missing jira-plan.local.json
  exit /b 1
)

echo [INFO] Loading Jira environment from .env.jira.local
>>"%LOG_FILE%" echo [INFO] Loading Jira environment from .env.jira.local
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
  echo [ERROR] JIRA_BASE_URL not set after loading .env.jira.local
  >>"%LOG_FILE%" echo [ERROR] JIRA_BASE_URL not set after loading .env.jira.local
  exit /b 1
)
if not defined JIRA_EMAIL (
  echo [ERROR] JIRA_EMAIL not set after loading .env.jira.local
  >>"%LOG_FILE%" echo [ERROR] JIRA_EMAIL not set after loading .env.jira.local
  exit /b 1
)
if not defined JIRA_API_TOKEN (
  echo [ERROR] JIRA_API_TOKEN not set after loading .env.jira.local
  >>"%LOG_FILE%" echo [ERROR] JIRA_API_TOKEN not set after loading .env.jira.local
  exit /b 1
)

set "DRY_RUN_ARG="
if /I "%~1"=="--dry-run" set "DRY_RUN_ARG=--dry-run"

echo [INFO] Applying Jira batch update from jira-plan.local.json %DRY_RUN_ARG%
>>"%LOG_FILE%" echo [INFO] Applying Jira batch update from jira-plan.local.json %DRY_RUN_ARG%
powershell -NoProfile -Command "& { py .\skills\project-leader-agent\scripts\jira_batch_update.py --plan-file .\jira-plan.local.json %DRY_RUN_ARG% 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append }"
if errorlevel 1 (
  echo [ERROR] Jira batch update failed.
  >>"%LOG_FILE%" echo [ERROR] Jira batch update failed.
  exit /b 1
)

echo [INFO] Jira batch update completed.
>>"%LOG_FILE%" echo [INFO] Jira batch update completed.
echo === Development Cycle End Complete ===
>>"%LOG_FILE%" echo === Development Cycle End Complete ===
exit /b 0
