# Example Koyeb deployment helper (free tier) for AetherCore Gateway + Search Helper
# Copy to `koyeb_deploy.ps1`, set real secrets in dev.env, then run it.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Load-EnvFile {
    param (
        [Parameter(Mandatory = $true)]
        [string] $Path
    )
    $map = @{}
    if (-not (Test-Path $Path)) {
        throw "dev.env (or dev.env.example) not found at $Path"
    }
    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*$' -or $_ -match '^\s*#') { return }
        if ($_ -notmatch '=') { return }
        $parts = $_ -split '=',2
        $key = $parts[0].Trim()
        $val = $parts[1].Trim()
        if ($key) { $map[$key] = $val }
    }
    return $map
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$devEnvPath = Join-Path $scriptDir "dev.env.example"
$envMap = Load-EnvFile -Path $devEnvPath

# Placeholder token; replace in dev.env before running the real script
$token = $envMap['KOYEB_API_KEY']
if (-not $token -or $token -like 'YOUR_*') { throw "Set KOYEB_API_KEY in dev.env before running the real deploy script." }

function Require-Value {
    param($Key)
    if (-not $envMap[$Key] -or $envMap[$Key] -like 'YOUR_*') { throw "$Key must be set in dev.env with a real value" }
}

Require-Value -Key 'API_KEY'
Require-Value -Key 'UPSTASH_REDIS_REST_URL'
Require-Value -Key 'UPSTASH_REDIS_REST_TOKEN'

$gatewayKey = $envMap['GATEWAY_API_KEY']
if (-not $gatewayKey -or $gatewayKey -like 'YOUR_*') { $gatewayKey = $envMap['API_KEY'] }

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

foreach ($k in @('GOOGLE_API_KEY','GOOGLE_CSE_ID','BRAVE_API','SERPER_API_KEY','WEBSCRAPING_API_KEY','SCRAPINGANT_API_KEY','GEMINI_API_KEY')) {
    if ($envMap[$k] -and $envMap[$k] -notlike 'YOUR_*') { $envVars[$k] = $envMap[$k] }
}

$envArgs = @()
foreach ($pair in $envVars.GetEnumerator()) {
    $envArgs += @('--env', "$($pair.Key)=$($pair.Value)")
}

$koyebExe = Join-Path $repoRoot "koyeb-cli/koyeb.exe"
if (-not (Test-Path $koyebExe)) { $koyebExe = "koyeb" }

Write-Host "This is an example script. Copy to koyeb_deploy.ps1 and set real secrets in dev.env before running." -ForegroundColor Yellow

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

Write-Host "Command preview:" -ForegroundColor Cyan
Write-Host ($cmd -join ' ')
