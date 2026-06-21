# Download ONNX coffee leaf classifier (image classification - not GGUF)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModelDir = Join-Path $Root "model"
$ModelFile = Join-Path $ModelDir "coffee_model.onnx"
$ModelUrl = if ($env:CLASSIFIER_URL) { $env:CLASSIFIER_URL } else {
    "https://github.com/JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector/releases/download/v1.0.0/coffee_model.onnx"
}

New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null

if (Test-Path $ModelFile) {
    $sizeMb = [math]::Round((Get-Item $ModelFile).Length / 1MB, 1)
    Write-Host "Classifier already present ($sizeMb MB) - skipping"
    exit 0
}

foreach ($legacy in @(
    (Join-Path $Root "coffee_model.onnx"),
    (Join-Path $Root "app\coffee_model.onnx")
)) {
    if (Test-Path $legacy) {
        Copy-Item $legacy $ModelFile
        Write-Host "Copied classifier from $legacy"
        exit 0
    }
}

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

$TempFile = Join-Path $ModelDir ("coffee_model." + [guid]::NewGuid().ToString("N") + ".download")

Write-Host "Downloading ONNX classifier (~29 MB)..."
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
