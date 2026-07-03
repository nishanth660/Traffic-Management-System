# Script to run all Python files in the traffic management system
# This script will attempt to find Python and run all .py files

Write-Host "=== Traffic Management System - Running All Python Files ===" -ForegroundColor Cyan
Write-Host ""

# Function to find Python executable
function Find-Python {
    $pythonPaths = @(
        "python",
        "python3",
        "py",
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "$env:ProgramFiles\Python*\python.exe",
        "C:\Python*\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        try {
            if ($path -like "*\*") {
                # Wildcard path - search for it
                $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($found) {
                    $result = & $found.FullName --version 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        return $found.FullName
                    }
                }
            } else {
                # Direct command
                $result = & $path --version 2>&1
                if ($LASTEXITCODE -eq 0 -and $result -notlike "*was not found*" -and $result -notlike "*not recognized*") {
                    return $path
                }
            }
        } catch {
            continue
        }
    }
    return $null
}

# Find Python
Write-Host "Searching for Python installation..." -ForegroundColor Yellow
$python = Find-Python

if (-not $python) {
    Write-Host "ERROR: Python is not installed or not found in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Or run the python-installer.exe in this directory if available." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Python, make sure to:" -ForegroundColor Yellow
    Write-Host "  1. Add Python to PATH during installation" -ForegroundColor Yellow
    Write-Host "  2. Restart your terminal/PowerShell" -ForegroundColor Yellow
    Write-Host "  3. Run this script again" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Python: $python" -ForegroundColor Green
$version = & $python --version
Write-Host "Python version: $version" -ForegroundColor Green
Write-Host ""

# Get current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

# Find all Python files (excluding __pycache__ and extensions)
$pythonFiles = Get-ChildItem -Path $scriptDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { 
        $_.FullName -notlike "*__pycache__*" -and 
        $_.FullName -notlike "*\extensions\*" -and
        $_.FullName -notlike "*\flutter\*" -and
        $_.FullName -notlike "*\agent-extensions\*"
    } | 
    Sort-Object FullName

Write-Host "Found $($pythonFiles.Count) Python files to run:" -ForegroundColor Cyan
$pythonFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
Write-Host ""

# Files that are class definitions (not directly runnable)
$classOnlyFiles = @(
    "car_detection.py",
    "simulation_generator.py"
)

# Files that need specific arguments or dependencies
$filesNeedingArgs = @{
    "real_traffic_detector.py" = "Needs real_traffic_video.mp4"
    "simple_detection.py" = "Needs real_traffic_video.mp4"
    "download_video.py" = "May need internet connection"
}

$successCount = 0
$errorCount = 0
$skippedCount = 0

foreach ($file in $pythonFiles) {
    $fileName = $file.Name
    $filePath = $file.FullName
    $relativePath = $file.FullName.Replace($scriptDir, "").TrimStart("\")
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Running: $relativePath" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    # Skip class-only files
    if ($classOnlyFiles -contains $fileName) {
        Write-Host "Skipping (class definition only)" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    # Check if file needs special handling
    if ($filesNeedingArgs.ContainsKey($fileName)) {
        $requirement = $filesNeedingArgs[$fileName]
        Write-Host "Note: $requirement" -ForegroundColor Yellow
    }
    
    try {
        # Change to file's directory
        Push-Location $file.DirectoryName
        
        # Run the Python file
        $output = & $python $filePath 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "✓ Successfully executed" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "✗ Error (Exit code: $exitCode)" -ForegroundColor Red
            if ($output) {
                Write-Host $output -ForegroundColor Red
            }
            $errorCount++
        }
    } catch {
        Write-Host "✗ Exception: $_" -ForegroundColor Red
        $errorCount++
    } finally {
        Pop-Location
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total files found: $($pythonFiles.Count)" -ForegroundColor White
Write-Host "Successfully executed: $successCount" -ForegroundColor Green
Write-Host "Errors: $errorCount" -ForegroundColor Red
Write-Host "Skipped (class definitions): $skippedCount" -ForegroundColor Yellow
Write-Host ""

