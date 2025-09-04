# PowerShell script for floss development tasks
# Usage: .\dev.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  install      - Install package in development mode"
    Write-Host "  install-dev  - Install package with development dependencies"
    Write-Host "  format       - Format code with black and isort"
    Write-Host "  lint         - Run all linting checks (black, isort, flake8, mypy)"
    Write-Host "  test         - Run tests with pytest"
    Write-Host "  quality      - Run all quality checks (lint + test)"
    Write-Host "  clean        - Remove build artifacts and cache files"
    Write-Host "  pre-commit   - Install and run pre-commit hooks"
}

function Install-Package {
    Write-Host "📦 Installing package in development mode..." -ForegroundColor Blue
    pip install -e .
}

function Install-Dev {
    Write-Host "📦 Installing package with development dependencies..." -ForegroundColor Blue
    pip install -e ".[dev]"
}

function Format-Code {
    Write-Host "🎨 Formatting code..." -ForegroundColor Blue
    isort floss/
    black floss/
    Write-Host "✅ Code formatting complete!" -ForegroundColor Green
}

function Run-Lint {
    Write-Host "🔍 Running code quality checks..." -ForegroundColor Blue

    Write-Host "Checking code formatting with Black..." -ForegroundColor Yellow
    black --check --diff floss/
    if ($LASTEXITCODE -ne 0) { throw "Black check failed" }

    Write-Host "Checking import sorting with isort..." -ForegroundColor Yellow
    isort --check-only --diff floss/
    if ($LASTEXITCODE -ne 0) { throw "isort check failed" }

    Write-Host "Checking code style with Flake8..." -ForegroundColor Yellow
    flake8 floss/
    if ($LASTEXITCODE -ne 0) { throw "Flake8 check failed" }

    Write-Host "Checking type hints with MyPy..." -ForegroundColor Yellow
    mypy floss/
    if ($LASTEXITCODE -ne 0) { throw "MyPy check failed" }

    Write-Host "✅ All linting checks passed!" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Blue
    pytest tests/ -v
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
    Write-Host "✅ All tests passed!" -ForegroundColor Green
}

function Run-Quality {
    Write-Host "🚀 Running all quality checks..." -ForegroundColor Blue
    try {
        Run-Lint
        Run-Tests
        Write-Host "🎉 All quality checks passed!" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Quality checks failed: $_" -ForegroundColor Red
        exit 1
    }
}

function Install-PreCommit {
    Write-Host "🪝 Setting up pre-commit hooks..." -ForegroundColor Blue
    pre-commit install
    pre-commit run --all-files
}

function Clean-Artifacts {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Blue

    $paths = @(
        "build/",
        "dist/",
        "*.egg-info/",
        ".mypy_cache/",
        ".pytest_cache/"
    )

    foreach ($path in $paths) {
        if (Test-Path $path) {
            Remove-Item $path -Recurse -Force
            Write-Host "Removed $path" -ForegroundColor Yellow
        }
    }

    # Remove __pycache__ directories
    Get-ChildItem -Path . -Name "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

    # Remove .pyc and .pyo files
    Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item -Force
    Get-ChildItem -Path . -Filter "*.pyo" -Recurse | Remove-Item -Force

    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

# Main command dispatch
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Package }
    "install-dev" { Install-Dev }
    "format" { Format-Code }
    "lint" { Run-Lint }
    "test" { Run-Tests }
    "quality" { Run-Quality }
    "pre-commit" { Install-PreCommit }
    "clean" { Clean-Artifacts }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
