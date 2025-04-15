# Define parameters with improved descriptions
param (
    [switch]$ClearTerminal, # Clears the terminal after execution
    [switch]$DeactivateEnv, # Deactivates the virtual environment after execution
    [switch]$ExitTerminal, # Exits the terminal after execution
    [switch]$Help           # Displays the help message
)

# Stop execution on errors.
# This ensures that the script will terminate immediately if any error occurs.
$ErrorActionPreference = "Stop"

# Display help message if -Help or -h is provided.
# This provides usage instructions to the user.
if ($Help) {
    Write-Host "Usage: .\build_executable.ps1 [-ClearTerminal] [-DeactivateEnv] [-ExitTerminal] [-Help]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Red
    Write-Host "  -ClearTerminal   Clears the terminal after execution." -ForegroundColor Blue
    Write-Host "  -DeactivateEnv   Deactivates the virtual environment after execution." -ForegroundColor Blue
    Write-Host "  -ExitTerminal    Exits the terminal after execution." -ForegroundColor Blue
    Write-Host "  -Help            Displays this help message." -ForegroundColor Blue
    exit # Exit the script after displaying the help message
}

# Check if WiFi-Center.exe exists
$exePath = Join-Path -Path $PSScriptRoot -ChildPath "WiFi-Center.exe"
if (Test-Path $exePath) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "|| WiFi-Center.exe already exists!    ||" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    $response = Read-Host "Would you like to delete it and rebuild? (yes/no)"
    if ($response -eq "yes") {
        Remove-Item -Path $exePath -Force
        Write-Host "Existing executable deleted. Proceeding with rebuild..." -ForegroundColor Yellow
    }
    else {
        Write-Host "Rebuild canceled. Exiting script." -ForegroundColor Red
        exit
    }
}

# Function to check if virtual environment is activated.
# It checks for the existence of the VIRTUAL_ENV environment variable.
function Test-VenvActivated {
    return $null -ne $Env:VIRTUAL_ENV
}

# Path to the virtual environment (modify if needed).
# This is the default path, but can be changed if the virtual environment is located elsewhere.
$VenvPath = ".\.venv"

# Activate virtual environment if not already active.
# If the virtual environment is not detected, it will be created.
if (-not (Test-VenvActivated)) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "|| Virtual environment not detected.  ||" -ForegroundColor Yellow
    Write-Host "|| Activating...                      ||" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow

    # Check if the Activate.ps1 script exists in the virtual environment
    if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
        # Activate the virtual environment
        & "$VenvPath\Scripts\Activate.ps1"
    }
    else {
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "|| Virtual environment not found.     ||" -ForegroundColor Yellow
        Write-Host "|| Creating one...                    ||" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        # Create the virtual environment
        python -m venv .venv
        # Activate the virtual environment
        & "$VenvPath\Scripts\Activate.ps1"
    }
}
else {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "|| Virtual environment is already     ||" -ForegroundColor Green
    Write-Host "|| activated.                         ||" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

# Run PyInstaller to build the executable.
# This command uses PyInstaller to create a standalone executable from the Python script.
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "|| Building the executable...         ||" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Execute the PyInstaller command
# --runtime-tmpdir="." `
pyinstaller --name "WiFi-Center" --onefile --windowed `
    --icon="assets\master_icon.ico" `
    --add-data="styles:styles" `
    --add-data="assets:assets" `
    --add-data="core:core" `
    --add-data="helpers:helpers" `
    .\master.py

Write-Host "========================================" -ForegroundColor Green
Write-Host "|| Build completed. Check the 'dist'  ||" -ForegroundColor Green
Write-Host "|| folder.                            ||" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Clean up after build.
# This removes temporary files created by PyInstaller.
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "|| Cleaning up temporary files...     ||" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# Remove the 'build' directory and the '.spec' file
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Force "WiFi-Center.spec" -ErrorAction SilentlyContinue
Write-Host "========================================" -ForegroundColor Green
Write-Host "|| Cleanup complete.                  ||" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Move the executable file.
# This moves the executable from the 'dist' folder to the root directory.
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "|| Moving the executable file...      ||" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Define the source and destination paths for the executable
$sourcePath = Join-Path -Path $PSScriptRoot -ChildPath "dist\WiFi-Center.exe"
$destinationPath = Join-Path -Path $PSScriptRoot -ChildPath "WiFi-Center.exe"

# Move the executable file
Move-Item -Path $sourcePath -Destination $destinationPath

# Remove the 'dist' directory
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Write-Host "========================================" -ForegroundColor Green
Write-Host "|| File moved successfully.           ||" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green


# Deactivate the environment if the parameter is provided.
# This deactivates the virtual environment if the -DeactivateEnv parameter is used.
if ($DeactivateEnv) {
    deactivate
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "|| Virtual environment deactivated.   ||" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
}
else {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "|| Virtual environment remains active.||" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

# Clear the terminal if the parameter is provided.
# This clears the terminal if the -ClearTerminal parameter is used.
if ($ClearTerminal) {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "|| Terminal cleared.                  ||" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow

    # Wait for 2 seconds before clearing the terminal again
    Start-Sleep -Seconds 2
    Clear-Host
    Clear-Host
    Clear-Host
}
else {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "|| Terminal remains unchanged.        ||" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

# Exit the Terminal if the parameter is provided.
# This exits the terminal if the -ExitTerminal parameter is used.
if ($ExitTerminal) {
    $host.SetShouldExit(0)
    exit
}
