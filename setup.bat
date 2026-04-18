@echo off
REM Quick setup script for OpenIssue (Windows)

echo Setting up OpenIssue...

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo WARNING: Edit .env with your GitHub OAuth credentials
)

REM Backend setup
cd backend
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

echo Installing backend dependencies...
.venv\Scripts\pip.exe install -r requirements.txt

cd ..

REM CLI setup
cd cli
echo Installing CLI tool...
pip install -e .

cd ..

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your GitHub OAuth credentials
echo 2. Start backend: cd backend ^&^& .venv\Scripts\python.exe run.py
echo 3. Start frontend: cd frontend ^&^& python -m http.server 3000
echo 4. Visit: http://localhost:3000

pause
