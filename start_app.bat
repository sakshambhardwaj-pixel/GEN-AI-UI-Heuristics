@echo off
title UX Heuristic Evaluation Tool
echo ===================================
echo  UX Heuristic Evaluation Tool
echo ===================================
echo.
echo Starting the application...
echo.
echo The app will be available at:
echo   Local:    http://localhost:8501
echo   Network:  http://192.168.48.226:8501
echo.
echo To stop the server: Press Ctrl+C
echo ===================================
echo.

streamlit run main.py --server.port 8501 --server.address localhost

echo.
echo Application stopped.
pause
