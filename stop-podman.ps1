# PowerShell Stop Script for GEN-AI-UI-Heuristics Podman Deployment

param(
    [string]$PodName = "heuristic-evaluation-pod",
    [string]$ContainerName = "heuristic-evaluation-app"
)

# Colors for output (Windows PowerShell compatible)
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🛑 Stopping GEN-AI-UI-Heuristics Podman Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Stop the pod and containers
Write-Status "Stopping Podman pod and containers..."

# Stop using kube yaml (recommended)
if (Test-Path "podman-compose.yml") {
    Write-Status "Stopping using Podman Kube YAML..."
    try {
        podman play kube --down podman-compose.yml 2>$null
    } catch {
        Write-Warning "Failed to stop using kube yaml, trying manual cleanup..."
    }
}

# Manual cleanup as fallback
Write-Status "Performing manual cleanup..."
try { podman pod stop $PodName 2>$null } catch { Write-Warning "Pod $PodName not found or already stopped" }
try { podman pod rm $PodName 2>$null } catch { Write-Warning "Pod $PodName not found or already removed" }
try { podman container stop $ContainerName 2>$null } catch { Write-Warning "Container $ContainerName not found or already stopped" }
try { podman container rm $ContainerName 2>$null } catch { Write-Warning "Container $ContainerName not found or already removed" }

Write-Success "✅ Application stopped successfully!"

# Show remaining containers/pods (for verification)
Write-Status "Checking for any remaining related containers..."
try {
    $remaining = podman ps -a --filter "name=$ContainerName" --format "table {{.Names}}" | Select-String -Pattern $ContainerName
    if ($remaining) {
        Write-Warning "Found remaining containers: $remaining"
    } else {
        Write-Success "No remaining containers found"
    }
} catch {
    Write-Success "No remaining containers found"
}

Write-Host ""
Write-Success "🎉 Cleanup completed successfully!"
Write-Status "To restart the application, run: .\build-podman.ps1"
