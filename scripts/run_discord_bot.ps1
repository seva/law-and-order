# Stable launcher for the Discord enforcement bot.
#
# Secret hygiene: the bot token is read from the environment only. It is
# never stored in this file, the repo, or any artifact; missing
# configuration fails fast instead of starting half-configured.
#
# Operational behavior: single-instance guard (a second gateway session
# for the same token would fight the first), append-only log at
# logs/discord_bot.log, non-zero exit propagated to the caller.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

if (-not $env:DISCORD_BOT_TOKEN) {
    Write-Error "launcher: DISCORD_BOT_TOKEN is not set - refusing to start (set it as a user environment variable)"
    exit 1
}
if (-not $env:DISCORD_RULING_CHANNEL_ID) {
    Write-Error "launcher: DISCORD_RULING_CHANNEL_ID is not set - refusing to start"
    exit 1
}

$existing = Get-CimInstance Win32_Process -Filter "Name like 'python%'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'law_and_order\.wiring\.discord_live' -and $_.ProcessId -ne $PID }
if ($existing) {
    Write-Error "launcher: discord_live already running (PID $($existing.ProcessId -join ',')) - refusing duplicate gateway session"
    exit 1
}

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    Write-Error "launcher: python not found on PATH"
    exit 1
}

$env:PYTHONPATH = Join-Path $repo "src"
$logDir = Join-Path $repo "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir "discord_bot.log"

Add-Content -LiteralPath $log -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] launcher: starting discord_live"
& $python -u -m law_and_order.wiring.discord_live *>> $log
$code = $LASTEXITCODE
Add-Content -LiteralPath $log -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] launcher: process exited code=$code"
exit $code
