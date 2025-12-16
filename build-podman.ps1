# PowerShell Build and Deploy Script for GEN-AI-UI-Heuristics with Podman
# This script builds the container image and runs it using Podman on Windows

param(
    [string]$ImageName = "localhost/heuristic-evaluation:latest",
    [string]$ContainerName = "heuristic-evaluation-app",
    [string]$PodName = "heuristic-evaluation-pod"
)

# Colors for output (Windows PowerShell compatible)
function Write-Status { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host "🚀 Building and Deploying GEN-AI-UI-Heuristics with Podman" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path "GEN-AI-Heuristics\.env")) {
    Write-Warning ".env file not found in GEN-AI-Heuristics directory"
    Write-Warning "Creating template .env file - please update with your OpenAI API key"
    
    $envTemplate = @"
# OpenAI API Key - Required for heuristic evaluation
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Additional environment variables
# STREAMLIT_THEME_BASE=light
# STREAMLIT_THEME_PRIMARY_COLOR=#ff6b35
"@
    
    $envTemplate | Out-File -FilePath "GEN-AI-Heuristics\.env" -Encoding UTF8
    Write-Warning "Please edit GEN-AI-Heuristics\.env and add your OpenAI API key before continuing"
    Read-Host "Press Enter to continue once you've updated the .env file"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
if (-not (Test-Path "uploads")) { New-Item -ItemType Directory -Name "uploads" | Out-Null }
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Name "data" | Out-Null }

# Clean up any existing containers/pods
Write-Status "Cleaning up existing containers..."
try {
    podman pod rm -f $PodName 2>$null
    podman container rm -f $ContainerName 2>$null
} catch {
    # Ignore errors for non-existent containers
}

# Build the image
Write-Status "Building Docker image with Podman..."
podman build -f Dockerfile.podman -t $ImageName .

if ($LASTEXITCODE -eq 0) {
    Write-Success "Image built successfully: $ImageName"
} else {
    Write-Error "Failed to build image"
    exit 1
}

# Load environment variables
if (Test-Path "GEN-AI-Heuristics\.env") {
    Get-Content "GEN-AI-Heuristics\.env" | ForEach-Object {
        if ($_ -match '^([^#].*)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Validate OpenAI API key
$openaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "Process")
if ([string]::IsNullOrEmpty($openaiKey) -or $openaiKey -eq "your_openai_api_key_here") {
    Write-Error "OpenAI API key is not set or still has default value"
    Write-Error "Please update the OPENAI_API_KEY in GEN-AI-Heuristics\.env file"
    exit 1
}

# Run with Podman using the YAML file
Write-Status "Starting application with Podman Kube..."
$env:OPENAI_API_KEY = $openaiKey
podman play kube podman-compose.yml

if ($LASTEXITCODE -eq 0) {
    Write-Success "Application started successfully!"
    Write-Host ""
    Write-Success "🌐 Access your application at: http://localhost:8501"
    Write-Host ""
    Write-Status "Container logs: podman logs $ContainerName"
    Write-Status "Stop application: podman pod stop $PodName"
    Write-Status "Remove application: podman pod rm $PodName"
    Write-Host ""
    Write-Status "Waiting for application to be ready..."
    
    # Wait for health check
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "✅ Application is ready and healthy!"
                break
            }
        } catch {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
    
    if ($i -eq 31) {
        Write-Warning "Health check timeout - application may still be starting"
        Write-Status "Check logs with: podman logs $ContainerName"
    }
    
} else {
    Write-Error "Failed to start application"
    exit 1
}

Write-Host ""
Write-Success "🎉 Deployment completed successfully!"
Write-Status "Your Streamlit Heuristic Evaluation app is running at http://localhost:8501"
