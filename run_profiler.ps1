# Run ADTC profiler on this submission.
#
# Usage:
#   .\run_profiler.ps1              # Fast local check (host OS, full RAM)
#   .\run_profiler.ps1 -Constrained # ADTC Standard Laptop profile (Docker, 7.5 GB cap, Ubuntu)
#
# Requires GGUF model: .\download_model.ps1
param(
    [switch]$Constrained
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Parent = Split-Path -Parent $Root
$ProfilerRepo = Join-Path $Parent "adtc-profiler"
$LlamaBin = Join-Path $Parent "tools\llama.cpp"

if (-not (Test-Path (Join-Path $Root "model\SmolLM2-360M-Instruct-Q4_K_M.gguf"))) {
    Write-Host "GGUF model missing. Run .\download_model.ps1 first."
    exit 1
}

if ($Constrained) {
    $OutFile = Join-Path $Root "submission_constrained.json"
    $Artifacts = Join-Path $Root "profiler_artifacts"
    New-Item -ItemType Directory -Force -Path $Artifacts | Out-Null

    $image = "adtc-profiler:latest"
    $imageExists = docker image inspect $image 2>$null
    if (-not $imageExists) {
        Write-Host "Building adtc-profiler Docker image (first run may take 10-20 min)..."
        docker build -t $image $ProfilerRepo
    }

  # ADTC audit sandbox uses 7.5 GB memory limit on Ubuntu reference stack
    $submissionMount = ($Root -replace '\\', '/')
    $artifactsMount = ($Artifacts -replace '\\', '/')

    Write-Host "Running profiler in Docker (memory=7.5g, Ubuntu, CPU-only llama.cpp)..."
    Write-Host "This matches the ADTC Standard Laptop RAM budget (8 GB profile)."

    docker run --rm `
        --memory=7.5g `
        --memory-swap=7.5g `
        --cpus=4 `
        -v "${submissionMount}:/submission:ro" `
        -v "${artifactsMount}:/artifacts" `
        $image run `
        --submission /submission `
        --mode participant `
        --output /artifacts/submission_constrained.json `
        --skip-accuracy

    if (Test-Path (Join-Path $Artifacts "submission_constrained.json")) {
        Copy-Item -Force (Join-Path $Artifacts "submission_constrained.json") $OutFile
        Write-Host "Report written to: $OutFile"
    } else {
        Write-Host "Profiler did not produce output. Check Docker logs above."
        exit 1
    }
    exit 0
}

# --- Host run (development machine) ---
$OutFile = Join-Path $Root "submission.json"

chcp 65001 | Out-Null
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

if (-not (Test-Path (Join-Path $LlamaBin "llama-bench.exe"))) {
    Write-Host "llama-bench not found. Expected at: $LlamaBin"
    Write-Host "Use -Constrained for Docker-based run, or download win-cpu-x64 from llama.cpp releases."
    exit 1
}

$env:PATH = "$LlamaBin;$env:PATH"

$ProfilerExe = Join-Path $ProfilerRepo ".venv\Scripts\adtc-profiler.exe"
if (-not (Test-Path $ProfilerExe)) {
    Write-Host "adtc-profiler venv not found at $ProfilerRepo"
    Write-Host "Setup once:"
    Write-Host "  cd `"$ProfilerRepo`""
    Write-Host "  uv venv --python 3.12 .venv"
    Write-Host "  uv pip install -e ."
    Write-Host "Or use: .\run_profiler.ps1 -Constrained"
    exit 1
}

Write-Host "Running adtc-profiler on host (not memory-limited; use -Constrained for 8 GB profile)..."
& $ProfilerExe run --submission $Root --mode participant --output $OutFile --skip-accuracy
Write-Host "Report written to: $OutFile"
