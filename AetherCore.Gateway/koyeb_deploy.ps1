# Koyeb deployment helper (free tier) for AetherCore Gateway + Search Helper
# - Reads API keys and config from dev.env
# - Builds from the repository root as an archive with Dockerfile at Aethercore.Gateway/Dockerfile
# - Forces free Nano instance in Washington (was) and routes /aethercore -> 8000, /search -> 3000

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Load-EnvFile {
    param (
        [Parameter(Mandatory = $true)]
        [string] $Path
    )
    $map = @{}
    if (-not (Test-Path $Path)) {
        throw "dev.env not found at $Path"
    }
    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*$' -or $_ -match '^\s*#') { return }
        if ($_ -notmatch '=') { return }
        $parts = $_ -split '=', 2
        $key = $parts[0].Trim()
        $val = $parts[1].Trim()
        if ($key) { $map[$key] = $val }
    }
    return $map
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$devEnvPath = Join-Path $scriptDir "dev.env"
$envMap = Load-EnvFile -Path $devEnvPath

$token = $envMap['KOYEB_API_KEY']
if (-not $token) { $token = $envMap['KOYEB_PERSONAL_ACCESS_TOKEN'] }
if (-not $token) { throw "KOYEB_API_KEY or KOYEB_PERSONAL_ACCESS_TOKEN is required in dev.env" }

function Require-Value {
    param($Key)
    if (-not $envMap[$Key]) { throw "$Key is required in dev.env" }
}

# Required secrets
Require-Value -Key 'API_KEY'
Require-Value -Key 'UPSTASH_REDIS_REST_URL'
Require-Value -Key 'UPSTASH_REDIS_REST_TOKEN'

$gatewayKey = $envMap['GATEWAY_API_KEY']
if (-not $gatewayKey) { $gatewayKey = $envMap['API_KEY'] }

$envVars = [ordered]@{
    ENVIRONMENT              = 'production'
    DEBUG                    = 'false'
    PORT                     = '8000'
    HOST                     = '0.0.0.0'
    LOG_LEVEL                = ($envMap['LOG_LEVEL'] | ForEach-Object { if ($_ -ne '') { $_ } else { 'INFO' } })
    CORS_ORIGINS             = 'https://chat.openai.com,https://chatgpt.com'
    RATE_LIMIT_REQUESTS      = ($envMap['RATE_LIMIT_REQUESTS'] | ForEach-Object { if ($_ -ne '') { $_ } else { '100' } })
    RATE_LIMIT_WINDOW        = ($envMap['RATE_LIMIT_WINDOW'] | ForEach-Object { if ($_ -ne '') { $_ } else { '3600' } })
    SKILLS_CONFIG_PATH       = '../AetherCore.System/skills_config.json'
    SEARCH_ENGINE_SERVER_URL = 'http://localhost:3000'
    SEARCH_ENGINE_PORT       = '3000'
    API_KEY                  = $envMap['API_KEY']
    GATEWAY_API_KEY          = $gatewayKey
    UPSTASH_REDIS_REST_URL   = $envMap['UPSTASH_REDIS_REST_URL']
    UPSTASH_REDIS_REST_TOKEN = $envMap['UPSTASH_REDIS_REST_TOKEN']
}

# Optional provider keys
foreach ($k in @('GOOGLE_API_KEY','GOOGLE_CSE_ID','BRAVE_API','SERPER_API_KEY','WEBSCRAPING_API_KEY','SCRAPINGANT_API_KEY','GEMINI_API_KEY')) {
    if ($envMap[$k]) { $envVars[$k] = $envMap[$k] }
}

$envArgs = @()
foreach ($pair in $envVars.GetEnumerator()) {
    $envArgs += @('--env', "$($pair.Key)=$($pair.Value)")
}

# Prefer bundled CLI if present, otherwise fallback to PATH
$koyebExe = Join-Path $repoRoot "koyeb-cli/koyeb.exe"
if (-not (Test-Path $koyebExe)) { $koyebExe = "koyeb" }

Write-Host "Deploying gateway-aethercore to Koyeb (free nano, was) with archive builder..." -ForegroundColor Cyan

$cmd = @(
    $koyebExe, 'deploy', $repoRoot, 'aethercore/gateway-aethercore',
    '--token', $token,
    '--archive-builder', 'docker',
    '--archive-docker-dockerfile', 'Aethercore.Gateway/Dockerfile',
    '--ports', '8000:http', '--ports', '3000:http',
    '--routes', '/aethercore:8000', '--routes', '/search:3000',
    '--instance-type', 'nano',
    '--regions', 'was',
    '--scale', '1',
    '--checks', '8000:http:/health', '--checks', '3000:tcp', '--checks-grace-period', '8000=60',
    '--skip-cache'
) + $envArgs + @('--wait')

Push-Location $repoRoot
& $cmd
Pop-Location
