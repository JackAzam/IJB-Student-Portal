@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. Follow README.md setup instructions first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
