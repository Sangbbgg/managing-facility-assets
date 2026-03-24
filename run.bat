@echo off

:MENU
cls
echo =====================================================
echo   Facility Asset Management - Docker Manager
echo =====================================================
echo.
echo   [1] Full Deploy        (build + start)
echo   [2] Update All
echo   [3] Update Backend only
echo   [4] Update Frontend only
echo   [5] Restart All
echo   [6] Stop All
echo   [7] Show Logs
echo   [8] Save Images        (for offline deploy)
echo   [9] Load Images        (for offline deploy)
echo   [0] Exit
echo.
echo =====================================================
set /p choice=  Select number:

if "%choice%"=="1" goto DEPLOY
if "%choice%"=="2" goto UPDATE_ALL
if "%choice%"=="3" goto UPDATE_BACK
if "%choice%"=="4" goto UPDATE_FRONT
if "%choice%"=="5" goto RESTART
if "%choice%"=="6" goto STOP
if "%choice%"=="7" goto LOGS
if "%choice%"=="8" goto SAVE
if "%choice%"=="9" goto LOAD
if "%choice%"=="0" goto EXIT
timeout /t 1 >nul
goto MENU

:DEPLOY
cls
echo [Deploy] Checking .env ...
if not exist ".env" (
    echo .env not found. Copying from .env.example ...
    copy ".env.example" ".env"
)
echo [1/3] Building images...
docker compose build
if %errorlevel% neq 0 ( echo [ERROR] Build failed & goto END )
echo [2/3] Starting containers...
docker compose up -d
if %errorlevel% neq 0 ( echo [ERROR] Start failed & goto END )
echo [3/3] Status check...
docker compose ps
echo.
echo  Frontend : http://localhost:80
echo  Backend  : http://localhost:8000
goto END

:UPDATE_ALL
cls
echo [Update All] Building and restarting...
docker compose build
docker compose up -d
docker compose ps
goto END

:UPDATE_BACK
cls
echo [Update Backend] Building and restarting...
docker compose build asset-backend
docker compose up -d asset-backend
docker compose ps
goto END

:UPDATE_FRONT
cls
echo [Update Frontend] Building and restarting...
docker compose build asset-frontend
docker compose up -d asset-frontend
docker compose ps
goto END

:RESTART
cls
echo [Restart] Restarting all containers...
docker compose restart
docker compose ps
goto END

:STOP
cls
echo [Stop] Stopping all containers...
docker compose down
echo Done. (Data volume is preserved)
goto END

:LOGS
cls
echo [Logs] Press Ctrl+C to exit...
docker compose logs -f --tail=100
goto MENU

:SAVE
cls
echo [Save Images] Saving to docker-images/ ...
if not exist "docker-images" mkdir docker-images
echo [1/3] Saving frontend...
docker save managing-facility-assets-asset-frontend | gzip > docker-images/asset-frontend.tar.gz
echo [2/3] Saving backend...
docker save managing-facility-assets-asset-backend | gzip > docker-images/asset-backend.tar.gz
echo [3/3] Saving postgres...
docker save postgres:16-alpine | gzip > docker-images/postgres-16.tar.gz
echo Done. Files saved to docker-images/
dir docker-images
goto END

:LOAD
cls
echo [Load Images] Loading from docker-images/ ...
if not exist "docker-images" (
    echo [ERROR] docker-images folder not found.
    goto END
)
echo [1/3] Loading frontend...
docker load < docker-images/asset-frontend.tar.gz
echo [2/3] Loading backend...
docker load < docker-images/asset-backend.tar.gz
echo [3/3] Loading postgres...
docker load < docker-images/postgres-16.tar.gz
echo Done. Now run [1] Full Deploy.
goto END

:EXIT
exit /b 0

:END
echo.
pause
goto MENU
