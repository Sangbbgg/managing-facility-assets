@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: =====================================================================
::  Facility Asset Management System - Docker Management Tool
::  Usage: Double-click run.bat in the project root directory
:: =====================================================================

:MENU
cls
echo.
echo  ================================================================
echo    Facility Asset Management System  ^|  Docker Management Tool
echo  ================================================================
echo.

:: Show current container status
echo  [Current Container Status]
for /f "tokens=*" %%s in ('docker compose ps --format "table {{.Name}}\t{{.Status}}" 2^>nul') do (
    echo    %%s
)
echo.
echo  ----------------------------------------------------------------
echo.
echo    1. Full Deploy        - Build images and start all containers
echo    2. Full Update        - Rebuild all images and restart
echo    3. Backend Update     - Rebuild backend (FastAPI) only
echo    4. Frontend Update    - Rebuild frontend (Vue) only
echo    5. Restart All        - Restart running containers (no rebuild)
echo    6. Stop All           - Stop and remove all containers
echo    7. Logs (All)         - Live logs from all containers
echo    8. Logs (Backend)     - Live logs from backend container
echo    9. Logs (Frontend)    - Live logs from frontend container
echo   10. Save Images        - Export built images to files
echo   11. Load Images        - Import images from files
echo   12. Reset DB           - Delete all data and re-seed (DANGER)
echo    0. Exit
echo.
echo  ================================================================
set /p choice=  Enter number:

if "%choice%"=="1"  goto DEPLOY
if "%choice%"=="2"  goto UPDATE_ALL
if "%choice%"=="3"  goto UPDATE_BACK
if "%choice%"=="4"  goto UPDATE_FRONT
if "%choice%"=="5"  goto RESTART
if "%choice%"=="6"  goto STOP
if "%choice%"=="7"  goto LOGS_ALL
if "%choice%"=="8"  goto LOGS_BACK
if "%choice%"=="9"  goto LOGS_FRONT
if "%choice%"=="10" goto SAVE
if "%choice%"=="11" goto LOAD
if "%choice%"=="12" goto RESET_DB
if "%choice%"=="0"  goto EXIT
echo.
echo   [!] Invalid input. Please enter a valid menu number.
timeout /t 2 >nul
goto MENU


:: =====================================================================
:: [1] Full Deploy
::
::   What it does:
::     - Checks for .env file (copies .env.example if missing)
::     - Builds all Docker images from source
::     - Starts all containers (DB / Backend / Frontend)
::     - Prints access URLs when done
::
::   When to use:
::     - First-time project setup
::     - After git clone
::     - After running [11] Load Images on a new server
:: =====================================================================
:DEPLOY
cls
echo.
echo  ================================================================
echo    [1] Full Deploy  -  Build images and start all containers
echo  ================================================================
echo.
echo   Steps:
echo     Step 1. Check for .env file
echo     Step 2. Build all Docker images from source
echo     Step 3. Start DB / Backend / Frontend containers
echo.
echo   Note: First build may take 3-10 minutes depending on network speed.
echo.

if not exist ".env" (
    echo   [Info] .env not found. Copying from .env.example...
    copy ".env.example" ".env" >nul
    echo   [Info] .env created. Edit it if needed.
    echo.
)

set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Step 1: Building images... ----
set DOCKER_BUILDKIT=0
docker compose build
set DOCKER_BUILDKIT=
if %errorlevel% neq 0 (
    echo.
    echo   [Error] Build failed. Check the error log above.
    goto BACK
)

echo.
echo  ---- Step 2: Starting containers... ----
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo   [Error] Failed to start containers.
    goto BACK
)

echo.
echo  ---- Step 3: Container status ----
docker compose ps
echo.
echo  ================================================================
echo    Deploy complete!
echo.
echo    Frontend  :  http://localhost
echo    Backend   :  http://localhost:8000
echo    API Docs  :  http://localhost:8000/docs
echo  ================================================================
goto BACK


:: =====================================================================
:: [2] Full Update
::
::   What it does:
::     - Rebuilds all Docker images from latest source
::     - Restarts all containers with new images
::
::   When to use:
::     - After git pull when both backend and frontend changed
::     - Same as running [3] + [4] together
:: =====================================================================
:UPDATE_ALL
cls
echo.
echo  ================================================================
echo    [2] Full Update  -  Rebuild all images and restart
echo  ================================================================
echo.
echo   Steps:
echo     Step 1. Rebuild backend + frontend images
echo     Step 2. Restart all containers
echo.
echo   Tip: If only one side changed, use [3] or [4] for faster update.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Rebuilding all images... ----
set DOCKER_BUILDKIT=0
docker compose build
set DOCKER_BUILDKIT=
echo.
echo  ---- Restarting containers... ----
docker compose up -d
echo.
echo  ---- Container status ----
docker compose ps
echo.
echo   [Done] Full update complete.
goto BACK


:: =====================================================================
:: [3] Backend Update
::
::   What it does:
::     - Rebuilds backend (FastAPI / Python) Docker image
::     - Restarts backend container only
::     - DB and frontend containers are not affected
::
::   When to use:
::     - After modifying Python code (models, routes, services, schemas)
::     - After adding new API endpoints
::     - After changing requirements.txt
:: =====================================================================
:UPDATE_BACK
cls
echo.
echo  ================================================================
echo    [3] Backend Update  -  FastAPI / Python
echo  ================================================================
echo.
echo   Steps:
echo     Step 1. Rebuild backend image
echo     Step 2. Restart backend container
echo.
echo   DB and frontend containers are not affected.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Rebuilding backend image... ----
set DOCKER_BUILDKIT=0
docker compose build asset-backend
set DOCKER_BUILDKIT=
echo.
echo  ---- Restarting backend container... ----
docker compose up -d asset-backend
echo.
echo  ---- Container status ----
docker compose ps
echo.
echo   [Done] Backend updated.
goto BACK


:: =====================================================================
:: [4] Frontend Update
::
::   What it does:
::     - Rebuilds frontend (Vue 3 / Vite) Docker image
::     - Restarts frontend container only
::     - DB and backend containers are not affected
::
::   When to use:
::     - After modifying Vue components, pages, or styles
::     - After changing JavaScript / CSS
::     - After updating vite.config.js or package.json
:: =====================================================================
:UPDATE_FRONT
cls
echo.
echo  ================================================================
echo    [4] Frontend Update  -  Vue 3 / Vite
echo  ================================================================
echo.
echo   Steps:
echo     Step 1. Rebuild frontend image
echo     Step 2. Restart frontend container
echo.
echo   DB and backend containers are not affected.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Rebuilding frontend image... ----
set DOCKER_BUILDKIT=0
docker compose build asset-frontend
set DOCKER_BUILDKIT=
echo.
echo  ---- Restarting frontend container... ----
docker compose up -d asset-frontend
echo.
echo  ---- Container status ----
docker compose ps
echo.
echo   [Done] Frontend updated.
goto BACK


:: =====================================================================
:: [5] Restart All
::
::   What it does:
::     - Restarts all running containers without rebuilding images
::
::   When to use:
::     - Container crashed or misbehaving without code changes
::     - Want to reset DB connections
::     - Quick restart needed (saves build time)
::
::   Note: Source code changes are NOT applied.
::         Use [2] Full Update if you changed code.
:: =====================================================================
:RESTART
cls
echo.
echo  ================================================================
echo    [5] Restart All  -  Restart running containers (no rebuild)
echo  ================================================================
echo.
echo   - Restarts all currently running containers without rebuilding.
echo.
echo   Note: Source code changes are NOT applied.
echo         Use [2] Full Update if you changed code.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Restarting all containers... ----
docker compose restart
echo.
echo  ---- Container status ----
docker compose ps
echo.
echo   [Done] All containers restarted.
goto BACK


:: =====================================================================
:: [6] Stop All
::
::   What it does:
::     - Stops and removes all running containers
::     - Docker images and DB volumes are preserved
::
::   When to use:
::     - Shutting down after work
::     - System maintenance or upgrade
::     - Freeing up memory resources
::
::   Note: DB volume is kept. Run [1] Full Deploy to start again.
:: =====================================================================
:STOP
cls
echo.
echo  ================================================================
echo    [6] Stop All  -  Stop and remove all containers
echo  ================================================================
echo.
echo   - Stops and removes all running containers.
echo   - Docker images and DB volume are preserved.
echo.
echo   DB volume is kept. Run [1] Full Deploy to restart.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- Stopping containers... ----
docker compose down
echo.
echo   [Done] All containers stopped. Volume is preserved.
goto BACK


:: =====================================================================
:: [7] Logs (All)
::
::   What it does:
::     - Streams live logs from all containers combined
::     - Starts from last 100 lines
::
::   Note: Press Ctrl+C to stop and return to menu
:: =====================================================================
:LOGS_ALL
cls
echo.
echo  ================================================================
echo    [7] Logs (All)  -  Press Ctrl+C to stop and return to menu
echo  ================================================================
echo.
docker compose logs -f --tail=100
echo.
echo   [Log stream ended]
goto BACK


:: =====================================================================
:: [8] Logs (Backend)
::
::   What it does:
::     - Streams live logs from the backend (FastAPI) container
::
::   Note: Press Ctrl+C to stop and return to menu
:: =====================================================================
:LOGS_BACK
cls
echo.
echo  ================================================================
echo    [8] Logs (Backend)  -  Press Ctrl+C to stop and return to menu
echo  ================================================================
echo.
docker compose logs -f --tail=100 asset-backend
echo.
echo   [Log stream ended]
goto BACK


:: =====================================================================
:: [9] Logs (Frontend)
::
::   What it does:
::     - Streams live logs from the frontend (Nginx/Vue) container
::
::   Note: Press Ctrl+C to stop and return to menu
:: =====================================================================
:LOGS_FRONT
cls
echo.
echo  ================================================================
echo    [9] Logs (Frontend)  -  Press Ctrl+C to stop and return to menu
echo  ================================================================
echo.
docker compose logs -f --tail=100 asset-frontend
echo.
echo   [Log stream ended]
goto BACK


:: =====================================================================
:: [10] Save Images  (for offline / air-gapped deployment)
::
::   What it does:
::     - Saves all Docker images to ./docker-images/ as .tar files
::       (app images + base images needed for offline rebuild)
::
::   When to use:
::     - Preparing deployment to an air-gapped server
::     - After build and test on dev PC
::
::   Deployment workflow:
::     [Dev PC]    [1] Full Deploy -> [10] Save Images
::                 -> Copy docker-images\ folder via USB
::     [Target]    [11] Load Images -> [1] Full Deploy
:: =====================================================================
:SAVE
cls
echo.
echo  ================================================================
echo    [10] Save Images  -  Export built images to files
echo  ================================================================
echo.
echo   Output files (./docker-images/ folder):
echo     App images    : asset-frontend.tar, asset-backend.tar, postgres-16.tar
echo     Base images   : python-3.12-slim.tar, node-20-alpine.tar, nginx-alpine.tar
echo.
echo   After saving, copy docker-images\ to the target server
echo   and run [11] Load Images there.
echo.
echo   Note: Total size ~2-3GB (uncompressed). May take several minutes.
echo.
set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

if not exist "docker-images" mkdir docker-images

echo.
echo  ---- [1/6] Saving frontend image... ----
docker save -o docker-images\asset-frontend.tar managing-facility-assets-asset-frontend
if %errorlevel% neq 0 (echo   [Warning] Frontend image not found or save failed.) else (echo   [OK])

echo  ---- [2/6] Saving backend image... ----
docker save -o docker-images\asset-backend.tar managing-facility-assets-asset-backend
if %errorlevel% neq 0 (echo   [Warning] Backend image not found or save failed.) else (echo   [OK])

echo  ---- [3/6] Saving PostgreSQL image... ----
docker save -o docker-images\postgres-16.tar postgres:16-alpine
if %errorlevel% neq 0 (echo   [Warning] postgres:16-alpine not found or save failed.) else (echo   [OK])

echo  ---- [4/6] Saving Python base image (for offline rebuild)... ----
docker save -o docker-images\python-3.12-slim.tar python:3.12-slim
if %errorlevel% neq 0 (echo   [Warning] python:3.12-slim not found or save failed.) else (echo   [OK])

echo  ---- [5/6] Saving Node base image (for offline rebuild)... ----
docker save -o docker-images\node-20-alpine.tar node:20-alpine
if %errorlevel% neq 0 (echo   [Warning] node:20-alpine not found or save failed.) else (echo   [OK])

echo  ---- [6/6] Saving Nginx base image (for offline rebuild)... ----
docker save -o docker-images\nginx-alpine.tar nginx:alpine
if %errorlevel% neq 0 (echo   [Warning] nginx:alpine not found or save failed.) else (echo   [OK])

echo.
echo  ---- Saved files: ----
dir docker-images
echo.
echo   [Done] Copy docker-images\ to the target server,
echo          then run [11] Load Images on that server.
goto BACK


:: =====================================================================
:: [11] Load Images  (for offline / air-gapped deployment)
::
::   What it does:
::     - Loads Docker images from .tar files in ./docker-images/
::     - After loading, run [1] Full Deploy to start the system
::
::   Prerequisites:
::     - docker-images\ folder with .tar files must exist here
::     - Docker Desktop (or Docker Engine) must be running
::
::   Steps:
::     1. Place docker-images\ folder inside this project folder
::     2. Run [11] Load Images
::     3. Run [1] Full Deploy
:: =====================================================================
:LOAD
cls
echo.
echo  ================================================================
echo    [11] Load Images  -  Import images from files
echo  ================================================================
echo.
echo   Expected files (./docker-images/ folder):
echo     - asset-frontend.tar       (built app image)
echo     - asset-backend.tar        (built app image)
echo     - postgres-16.tar          (DB image)
echo     - python-3.12-slim.tar     (base image for offline build)
echo     - node-20-alpine.tar       (base image for offline build)
echo     - nginx-alpine.tar         (base image for offline build)
echo.
echo   After loading, run [1] Full Deploy to start the system.
echo.

if not exist "docker-images" (
    echo   [Error] docker-images\ folder not found.
    echo.
    echo   Run [10] Save Images on the source PC, then copy
    echo   the docker-images\ folder into this project folder.
    goto BACK
)

set /p confirm=  Proceed? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- [1/6] Loading frontend image... ----
if exist "docker-images\asset-frontend.tar" (
    docker load -i docker-images\asset-frontend.tar
) else (
    echo   [Warning] asset-frontend.tar not found. Skipping.
)

echo  ---- [2/6] Loading backend image... ----
if exist "docker-images\asset-backend.tar" (
    docker load -i docker-images\asset-backend.tar
) else (
    echo   [Warning] asset-backend.tar not found. Skipping.
)

echo  ---- [3/6] Loading PostgreSQL image... ----
if exist "docker-images\postgres-16.tar" (
    docker load -i docker-images\postgres-16.tar
) else (
    echo   [Warning] postgres-16.tar not found. Skipping.
)

echo  ---- [4/6] Loading Python base image... ----
if exist "docker-images\python-3.12-slim.tar" (
    docker load -i docker-images\python-3.12-slim.tar
) else (
    echo   [Warning] python-3.12-slim.tar not found. Skipping.
)

echo  ---- [5/6] Loading Node base image... ----
if exist "docker-images\node-20-alpine.tar" (
    docker load -i docker-images\node-20-alpine.tar
) else (
    echo   [Warning] node-20-alpine.tar not found. Skipping.
)

echo  ---- [6/6] Loading Nginx base image... ----
if exist "docker-images\nginx-alpine.tar" (
    docker load -i docker-images\nginx-alpine.tar
) else (
    echo   [Warning] nginx-alpine.tar not found. Skipping.
)

echo.
echo   [Done] Images loaded successfully.
echo          Now run [1] Full Deploy to start the system.
goto BACK


:: =====================================================================
:: [12] Reset DB
::
::   What it does:
::     - Truncates ALL tables (deletes all data, resets sequences)
::     - Rebuilds backend image (picks up latest seed.py changes)
::     - Restarts backend to re-run seed data
::
::   WARNING: ALL data will be permanently deleted.
::   Assets, groups, locations, layouts, etc. will all be erased.
::
::   When to use:
::     - Development / testing environment reset
::     - Start fresh with seed data only
:: =====================================================================
:RESET_DB
cls
echo.
echo  ================================================================
echo    [12] Reset DB  -  Delete ALL data and re-seed
echo  ================================================================
echo.
echo   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo   !! WARNING: This will permanently delete ALL database data. !!
echo   !! Assets, layouts, groups, locations - everything gone.    !!
echo   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo.
set /p confirm1=  Are you sure? Type YES to confirm:
if /i not "%confirm1%"=="YES" (
    echo.
    echo   [Cancelled] No changes made.
    goto BACK
)
echo.
set /p confirm2=  Type RESET to proceed:
if /i not "%confirm2%"=="RESET" (
    echo.
    echo   [Cancelled] No changes made.
    goto BACK
)

echo.
echo  ---- Truncating all tables... ----

:: Write SQL to temp file and copy into container
set SQLFILE=%TEMP%\db_reset_temp.sql
(
  echo SELECT format^('TRUNCATE TABLE "%%s" RESTART IDENTITY CASCADE', tablename^)
  echo FROM pg_tables WHERE schemaname = 'public';
  echo \gexec
) > "%SQLFILE%"

docker cp "%SQLFILE%" asset-db:/tmp/reset_db.sql
docker exec asset-db psql -U assetuser -d assetdb -f /tmp/reset_db.sql
if %errorlevel% neq 0 (
    echo.
    echo   [Error] Failed to truncate tables. Is asset-db running?
    goto BACK
)
echo   [Done] All tables truncated.

echo.
echo  ---- Rebuilding backend image (applying latest seed.py)... ----
set DOCKER_BUILDKIT=0
docker compose build asset-backend
set DOCKER_BUILDKIT=
if %errorlevel% neq 0 (
    echo.
    echo   [Error] Backend build failed. Check the error log above.
    goto BACK
)

echo.
echo  ---- Restarting backend to re-run seed data... ----
docker compose up -d asset-backend
echo.
echo  ---- Waiting for backend to be ready... ----
timeout /t 8 >nul
docker compose ps
echo.
echo   [Done] DB reset complete. Seed data has been re-applied.
goto BACK


:: =====================================================================
:BACK
echo.
echo  ----------------------------------------------------------------
pause
goto MENU

:EXIT
echo.
echo   Goodbye.
echo.
exit /b 0
