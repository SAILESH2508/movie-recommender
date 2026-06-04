@echo off
taskkill /F /IM python.exe
timeout /t 2
call venv\Scripts\activate
start "CineSmart AI" python -m streamlit run app/streamlit_app.py
