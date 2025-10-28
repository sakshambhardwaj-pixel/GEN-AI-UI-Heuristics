@echo off
echo Starting UX Heuristic Evaluation Tool...
echo.
echo The application will be available at: http://localhost:8501
echo To stop the server, press Ctrl+C
echo.
streamlit run main.py --server.port 8501 --server.address localhost
pause
