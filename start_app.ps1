# UX Heuristic Evaluation Tool Startup Script

Write-Host "====================================" -ForegroundColor Green
Write-Host " UX Heuristic Evaluation Tool" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found in current directory!" -ForegroundColor Red
    Write-Host "Please navigate to the GEN-AI-Heuristics folder first:" -ForegroundColor Yellow
    Write-Host "  cd GEN-AI-Heuristics" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found main.py - Starting application..." -ForegroundColor Green
Write-Host ""
Write-Host "🌐 The app will be available at:" -ForegroundColor Cyan
Write-Host "   Local:    http://localhost:8501" -ForegroundColor White
Write-Host "   Network:  http://192.168.48.226:8501" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the server: Press Ctrl+C" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check if port 8501 is already in use
$portInUse = netstat -an | Select-String ":8501.*LISTENING"
if ($portInUse) {
    Write-Host "⚠️  Port 8501 is already in use. Trying to kill existing process..." -ForegroundColor Yellow
    $process = Get-Process | Where-Object {$_.ProcessName -eq "streamlit"}
    if ($process) {
        Stop-Process -Name "streamlit" -Force -ErrorAction SilentlyContinue
        Start-Sleep 2
    }
}

try {
    # Start Streamlit
    streamlit run main.py --server.port 8501 --server.address localhost
} catch {
    Write-Host "❌ Error starting Streamlit: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try running these commands manually:" -ForegroundColor Yellow
    Write-Host "   cd GEN-AI-Heuristics" -ForegroundColor Cyan
    Write-Host "   streamlit run main.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
