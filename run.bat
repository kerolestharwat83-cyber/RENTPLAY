@echo off
echo ==========================================
echo    RENTPLAY v1.0 - Starting Server
echo ==========================================
echo.
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scriptsctivate.bat
if not exist "logs" mkdir logs
echo Installing requirements...
python -m pip install -r requirements.txt
echo Running migrations...
python manage.py migrate
echo Collecting static files...
python manage.py collectstatic --noinput
echo.
echo ==========================================
echo    Starting server at http://127.0.0.1:8000
echo    Login: admin / admin123
echo ==========================================
echo.
python manage.py runserver
pause
