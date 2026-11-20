$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvExample = Join-Path $ScriptDir ".env.example"
$EnvPath = Join-Path $ScriptDir ".env"
$ComposePath = Join-Path $ScriptDir "docker-compose.yml"

function New-RandomSecret {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }
    return [BitConverter]::ToString($bytes).Replace("-", "").ToLowerInvariant()
}

if (-not (Test-Path $EnvExample)) {
    throw "Missing .env.example at $EnvExample"
}

if (-not (Test-Path $EnvPath)) {
    $content = Get-Content -Raw -Path $EnvExample
    $content = $content.Replace("BETTER_AUTH_SECRET=REPLACE_DURING_INSTALL", "BETTER_AUTH_SECRET=$(New-RandomSecret)")
    $content = $content.Replace("PAPERCLIP_TOOL_ACTION_SIGNING_SECRET=REPLACE_DURING_INSTALL", "PAPERCLIP_TOOL_ACTION_SIGNING_SECRET=$(New-RandomSecret)")
    [System.IO.File]::WriteAllText($EnvPath, $content, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Created a private .env file and generated two separate signing secrets."
}
else {
    Write-Host "Existing .env found; keeping its secrets unchanged."
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed. Install Docker Desktop, start it, then run this script again."
}

& docker info --format '{{.ServerVersion}}' *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Engine is not running. Start Docker Desktop, then run this script again."
}

& docker compose version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose v2 is not available. Update Docker Desktop, then run this script again."
}

Push-Location $ScriptDir
try {
    & docker compose --env-file $EnvPath -f $ComposePath up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Paperclip container failed to start. Inspect Docker Desktop or run: docker compose --env-file .env -f docker-compose.yml logs"
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Paperclip container has been started."
Write-Host "Open: http://localhost:3100"
Write-Host "Logs: docker compose --env-file .env -f docker-compose.yml logs -f"
Write-Host "Data persists under deploy/paperclip/data."
Write-Host "No model provider key is added by this script; connect one in Paperclip when ready."
