# ============================================================
# MPI-ODM Single System Run Script (Windows PowerShell)
# Distributed Aerial 3D Object Mapping Using MPI
# ============================================================

param(
    [switch]$SkipDocker,
    [switch]$SkipSplit,
    [int]$NumProcesses = 4
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Refresh PATH to include MS-MPI
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$env:MSMPI_INC = [System.Environment]::GetEnvironmentVariable("MSMPI_INC","Machine")
$env:MSMPI_LIB32 = [System.Environment]::GetEnvironmentVariable("MSMPI_LIB32","Machine")
$env:MSMPI_LIB64 = [System.Environment]::GetEnvironmentVariable("MSMPI_LIB64","Machine")

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  MPI-ODM Distributed Photogrammetry        " -ForegroundColor Cyan
Write-Host "  Single System Execution                   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 0: Verify prerequisites ---
Write-Host "[Step 0] Verifying prerequisites..." -ForegroundColor Yellow

if (-not (Test-Path $Python)) {
    Write-Host "  ERROR: Python venv not found at $Python" -ForegroundColor Red
    Write-Host "  Run: python -m venv venv && venv\Scripts\pip install mpi4py pyodm trimesh numpy" -ForegroundColor Red
    exit 1
}
Write-Host "  Python venv: OK" -ForegroundColor Green

$mpiexec = Get-Command mpiexec -ErrorAction SilentlyContinue
if (-not $mpiexec) {
    Write-Host "  ERROR: mpiexec not found. Install MS-MPI." -ForegroundColor Red
    exit 1
}
Write-Host "  MS-MPI: OK" -ForegroundColor Green

# --- Step 1: Start NodeODM ---
if (-not $SkipDocker) {
    Write-Host ""
    Write-Host "[Step 1] Starting NodeODM Docker container..." -ForegroundColor Yellow

    $dockerCheck = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Docker not found. Install Docker Desktop." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Docker: $dockerCheck" -ForegroundColor Green

    # Stop existing container if running
    try { docker rm -f nodeodm 2>$null | Out-Null } catch { }

    docker run -d --name nodeodm --restart unless-stopped -p 3000:3000 opendronemap/nodeodm
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to start NodeODM container." -ForegroundColor Red
        exit 1
    }

    Write-Host "  Waiting for NodeODM to initialize..." -ForegroundColor Gray
    Start-Sleep -Seconds 10

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:3000/info" -TimeoutSec 10
        Write-Host "  NodeODM ready: version=$($response.version)" -ForegroundColor Green
    } catch {
        Write-Host "  WARNING: NodeODM may not be fully ready yet. Continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[Step 1] Skipping Docker (--SkipDocker)" -ForegroundColor Gray
}

# --- Step 2: Split dataset ---
if (-not $SkipSplit) {
    Write-Host ""
    Write-Host "[Step 2] Splitting dataset across $NumProcesses nodes..." -ForegroundColor Yellow
    & $Python src/split_dataset.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Dataset split failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Dataset split: OK" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[Step 2] Skipping split (--SkipSplit)" -ForegroundColor Gray
}

# --- Step 3: MPI Hello Test ---
Write-Host ""
Write-Host "[Step 3] Running MPI hello test..." -ForegroundColor Yellow
mpiexec -n $NumProcesses $Python src/hello_mpi.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: MPI hello test failed." -ForegroundColor Red
    exit 1
}
Write-Host "  MPI test: OK" -ForegroundColor Green

# --- Step 4: Run MPI-ODM distributed processing ---
Write-Host ""
Write-Host "[Step 4] Running MPI-ODM distributed processing ($NumProcesses ranks)..." -ForegroundColor Yellow
Write-Host "  This will take a while depending on dataset size and hardware." -ForegroundColor Gray
$sw = [System.Diagnostics.Stopwatch]::StartNew()

mpiexec -n $NumProcesses $Python src/mpi_odm_main.py

$sw.Stop()
$totalMinutes = [math]::Round($sw.Elapsed.TotalMinutes, 2)

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: MPI-ODM processing failed after $totalMinutes minutes." -ForegroundColor Red
    exit 1
}
Write-Host "  MPI-ODM processing completed in $totalMinutes minutes." -ForegroundColor Green

# --- Step 5: Verify outputs ---
Write-Host ""
Write-Host "[Step 5] Verifying outputs..." -ForegroundColor Yellow
& $Python src/verify_outputs.py

# --- Step 6: Merge models ---
Write-Host ""
Write-Host "[Step 6] Merging 3D models..." -ForegroundColor Yellow
& $Python src/merge_models.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Model merging failed." -ForegroundColor Red
    exit 1
}
Write-Host "  Merge: OK" -ForegroundColor Green

# --- Done ---
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ALL STEPS COMPLETED SUCCESSFULLY          " -ForegroundColor Cyan
Write-Host "  Total processing time: $totalMinutes min  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output files:" -ForegroundColor White
Write-Host "  Summary:    shared/final/mpi_summary.json" -ForegroundColor Gray
Write-Host "  Merged OBJ: shared/final/final_merged.obj" -ForegroundColor Gray
Write-Host "  Merged PLY: shared/final/final_merged.ply" -ForegroundColor Gray
