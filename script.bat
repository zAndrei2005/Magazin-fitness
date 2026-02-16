@echo off
setlocal enabledelayedexpansion

REM === Setări bază de date (din settings.py) ===
set DB_NAME=ProiectDjango
set DB_USER=andrei
set DB_PASS=24Decembrie2005

REM === Folderul unde salvezi backup-urile (relativ la manage.py) ===
set BACKUP_FOLDER=backups

REM === Creează folderul dacă nu există ===
if not exist "%BACKUP_FOLDER%" (
    mkdir "%BACKUP_FOLDER%"
)

REM === Generare timestamp pentru numele fișierului ===
for /f "tokens=1-5 delims=/:. " %%a in ("%date% %time%") do (
    set DATETIME=%%a_%%b_%%c_%%d_%%e
)

REM === Numele complet al fișierului de backup ===
set BACKUP_FILE=%BACKUP_FOLDER%\backup_%DATETIME%.sql

echo ===============================================
echo    Creare backup PostgreSQL...
echo ===============================================

REM === Setăm parola pentru pg_dump (ca variabilă de mediu) ===
set PGPASSWORD=%DB_PASS%

REM === Apelează pg_dump (verifică versiunea/locația!) ===
"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U %DB_USER% -d %DB_NAME% -F p -f "%BACKUP_FILE%"

echo ===============================================
echo  Backup realizat cu succes: %BACKUP_FILE%
echo ===============================================

pause
