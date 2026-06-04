@echo off
echo Starting CineMatch AI Pro...
call venv\Scripts\activate
python -m streamlit run app/streamlit_app.py
pause
