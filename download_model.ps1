# ADTC 2026 - download GGUF LLM (llama.cpp evaluation model)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModelDir = Join-Path $Root "model"
$ModelFile = Join-Path $ModelDir "SmolLM2-360M-Instruct-Q4_K_M.gguf"
$ModelUrl = if ($env:MODEL_URL) { $env:MODEL_URL } else {
    "https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf"
}

New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null

if (Test-Path $ModelFile) {
    $sizeMb = [math]::Round((Get-Item $ModelFile).Length / 1MB, 1)
    Write-Host "GGUF model already present ($sizeMb MB) - skipping download"
    exit 0
}

# Remove stale partial from a failed or interrupted download
$stalePartial = "$ModelFile.partial"
if (Test-Path $stalePartial) {
    try {
        Remove-Item -Force $stalePartial
        Write-Host "Removed stale partial download"
    }
    catch {
        Write-Host "Another download may still be running (locked: $stalePartial)."
        Write-Host "Wait for it to finish, or close the other PowerShell window, then run this script again."
        exit 1
    }
}

$TempFile = Join-Path $ModelDir ("SmolLM2-360M-Instruct-Q4_K_M." + [guid]::NewGuid().ToString("N") + ".download")

Write-Host "Downloading GGUF LLM (~248 MB)..."
Write-Host "URL: $ModelUrl"

try {
    Invoke-WebRequest -Uri $ModelUrl -OutFile $TempFile -UseBasicParsing
    Move-Item -Force $TempFile $ModelFile
    $sizeMb = [math]::Round((Get-Item $ModelFile).Length / 1MB, 1)
    Write-Host "done: $ModelFile ($sizeMb MB)"
}
catch {
    if (Test-Path $TempFile) {
        Remove-Item -Force $TempFile -ErrorAction SilentlyContinue
    }
    throw
}
