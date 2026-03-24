@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: =====================================================================
::  설비관리 시스템 - Docker 관리 도구
::  사용법: 프로젝트 루트 폴더에서 run.bat 더블클릭
:: =====================================================================

:MENU
cls
echo.
echo  ================================================================
echo    설비관리 시스템  ^|  Docker 관리 도구
echo  ================================================================
echo.

:: 현재 컨테이너 상태 출력
echo  [현재 컨테이너 상태]
for /f "tokens=*" %%s in ('docker compose ps --format "table {{.Name}}\t{{.Status}}" 2^>nul') do (
    echo    %%s
)
echo.
echo  ----------------------------------------------------------------
echo.
echo    1. 전체 배포          - 이미지 빌드 후 전체 컨테이너 시작
echo    2. 전체 업데이트      - 전체 이미지 재빌드 및 재시작
echo    3. 백엔드만 업데이트  - 백엔드(FastAPI)만 재빌드 및 재시작
echo    4. 프론트만 업데이트  - 프론트엔드(Vue)만 재빌드 및 재시작
echo    5. 전체 재시작        - 빌드 없이 컨테이너만 재시작
echo    6. 전체 중지          - 컨테이너 중지 및 제거
echo    7. 전체 로그 보기     - 전체 컨테이너 실시간 로그
echo    8. 백엔드 로그 보기   - 백엔드 컨테이너 실시간 로그
echo    9. 프론트 로그 보기   - 프론트엔드 컨테이너 실시간 로그
echo   10. 이미지 저장        - 폐쇄망 배포용 이미지 파일로 내보내기
echo   11. 이미지 불러오기    - 폐쇄망 배포용 이미지 파일 가져오기
echo    0. 종료
echo.
echo  ================================================================
set /p choice=  번호를 입력하세요:

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
if "%choice%"=="0"  goto EXIT
echo.
echo   [!] 올바르지 않은 입력입니다. 메뉴의 번호를 입력해주세요.
timeout /t 2 >nul
goto MENU


:: =====================================================================
:: [1] 전체 배포
::
::   하는 일:
::     - .env 파일 존재 여부 확인 (없으면 .env.example 에서 복사)
::     - Docker 이미지 빌드 (소스코드 → 이미지)
::     - 전체 컨테이너 시작 (DB / 백엔드 / 프론트엔드)
::     - 완료 후 접속 주소 안내
::
::   언제 사용:
::     - 프로젝트 최초 실행 시
::     - git clone 직후 처음 시작할 때
::     - [11] 이미지 불러오기 후 폐쇄망에서 시작할 때
:: =====================================================================
:DEPLOY
cls
echo.
echo  ================================================================
echo    [1] 전체 배포  -  이미지 빌드 후 전체 컨테이너 시작
echo  ================================================================
echo.
echo   실행 내용:
echo     1단계. .env 설정 파일 확인
echo     2단계. 전체 Docker 이미지 빌드 (소스코드 컴파일 포함)
echo     3단계. DB / 백엔드 / 프론트엔드 컨테이너 시작
echo.
echo   주의: 최초 빌드는 네트워크 환경에 따라 3~10분 소요될 수 있습니다.
echo.

if not exist ".env" (
    echo   [안내] .env 파일이 없어 .env.example 에서 복사합니다...
    copy ".env.example" ".env" >nul
    echo   [안내] .env 파일이 생성되었습니다. 필요 시 내용을 수정하세요.
    echo.
)

set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 1단계: 이미지 빌드 중... ----
docker compose build
if %errorlevel% neq 0 (
    echo.
    echo   [오류] 빌드에 실패했습니다. 위의 오류 메시지를 확인해주세요.
    goto BACK
)

echo.
echo  ---- 2단계: 컨테이너 시작 중... ----
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo   [오류] 컨테이너 시작에 실패했습니다.
    goto BACK
)

echo.
echo  ---- 3단계: 컨테이너 상태 확인 ----
docker compose ps
echo.
echo  ================================================================
echo    배포 완료!
echo.
echo    프론트엔드  :  http://localhost
echo    백엔드 API  :  http://localhost:8000
echo    API 문서    :  http://localhost:8000/docs
echo  ================================================================
goto BACK


:: =====================================================================
:: [2] 전체 업데이트
::
::   하는 일:
::     - 전체 Docker 이미지를 현재 소스코드 기준으로 재빌드
::     - 모든 컨테이너를 새 이미지로 재시작
::
::   언제 사용:
::     - git pull 후 백엔드·프론트엔드 코드가 모두 변경된 경우
::     - 한 번에 전체 변경사항을 반영하고 싶을 때
::     - [3] + [4] 를 한번에 실행하는 것과 동일
:: =====================================================================
:UPDATE_ALL
cls
echo.
echo  ================================================================
echo    [2] 전체 업데이트  -  전체 이미지 재빌드 및 재시작
echo  ================================================================
echo.
echo   실행 내용:
echo     1단계. 백엔드 + 프론트엔드 이미지 재빌드
echo     2단계. 모든 컨테이너 재시작
echo.
echo   팁: 백엔드 또는 프론트만 변경된 경우 [3] 또는 [4] 를 사용하면
echo       더 빠르게 업데이트할 수 있습니다.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 전체 이미지 재빌드 중... ----
docker compose build
echo.
echo  ---- 컨테이너 재시작 중... ----
docker compose up -d
echo.
echo  ---- 컨테이너 상태 확인 ----
docker compose ps
echo.
echo   [완료] 전체 업데이트가 적용되었습니다.
goto BACK


:: =====================================================================
:: [3] 백엔드만 업데이트
::
::   하는 일:
::     - 백엔드(FastAPI / Python) Docker 이미지만 재빌드
::     - 백엔드 컨테이너만 재시작
::     - DB 및 프론트엔드 컨테이너는 영향 없음
::
::   언제 사용:
::     - Python 코드 수정 후 (models, routes, services, schemas 등)
::     - 새 API 엔드포인트 추가 후
::     - requirements.txt 변경 후
:: =====================================================================
:UPDATE_BACK
cls
echo.
echo  ================================================================
echo    [3] 백엔드만 업데이트  -  FastAPI / Python
echo  ================================================================
echo.
echo   실행 내용:
echo     1단계. 백엔드 이미지만 재빌드
echo     2단계. 백엔드 컨테이너만 재시작
echo.
echo   DB와 프론트엔드 컨테이너는 영향을 받지 않습니다.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 백엔드 이미지 재빌드 중... ----
docker compose build asset-backend
echo.
echo  ---- 백엔드 컨테이너 재시작 중... ----
docker compose up -d asset-backend
echo.
echo  ---- 컨테이너 상태 확인 ----
docker compose ps
echo.
echo   [완료] 백엔드가 업데이트되었습니다.
goto BACK


:: =====================================================================
:: [4] 프론트만 업데이트
::
::   하는 일:
::     - 프론트엔드(Vue 3 / Vite) Docker 이미지만 재빌드
::     - 프론트엔드 컨테이너만 재시작
::     - DB 및 백엔드 컨테이너는 영향 없음
::
::   언제 사용:
::     - Vue 컴포넌트, 페이지, 스토어 수정 후
::     - JavaScript / CSS 코드 변경 후
::     - vite.config.js 또는 package.json 변경 후
:: =====================================================================
:UPDATE_FRONT
cls
echo.
echo  ================================================================
echo    [4] 프론트만 업데이트  -  Vue 3 / Vite
echo  ================================================================
echo.
echo   실행 내용:
echo     1단계. 프론트엔드 이미지만 재빌드
echo     2단계. 프론트엔드 컨테이너만 재시작
echo.
echo   DB와 백엔드 컨테이너는 영향을 받지 않습니다.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 프론트엔드 이미지 재빌드 중... ----
docker compose build asset-frontend
echo.
echo  ---- 프론트엔드 컨테이너 재시작 중... ----
docker compose up -d asset-frontend
echo.
echo  ---- 컨테이너 상태 확인 ----
docker compose ps
echo.
echo   [완료] 프론트엔드가 업데이트되었습니다.
goto BACK


:: =====================================================================
:: [5] 전체 재시작
::
::   하는 일:
::     - 이미지 재빌드 없이 실행 중인 모든 컨테이너를 재시작
::
::   언제 사용:
::     - 코드 변경은 없고 컨테이너가 멈추거나 오작동할 때
::     - DB 직접 수정 후 커넥션을 초기화하고 싶을 때
::     - 빠른 복구가 필요할 때 (빌드 시간 없음)
::
::   주의: 소스코드 변경사항은 반영되지 않습니다.
::         코드를 수정했다면 [2] 전체 업데이트를 사용하세요.
:: =====================================================================
:RESTART
cls
echo.
echo  ================================================================
echo    [5] 전체 재시작  -  빌드 없이 컨테이너만 재시작
echo  ================================================================
echo.
echo   실행 내용:
echo     - 이미지 재빌드 없이 모든 컨테이너를 재시작
echo.
echo   주의: 소스코드 변경사항은 반영되지 않습니다.
echo         코드를 수정했다면 [2] 전체 업데이트를 사용하세요.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 전체 컨테이너 재시작 중... ----
docker compose restart
echo.
echo  ---- 컨테이너 상태 확인 ----
docker compose ps
echo.
echo   [완료] 전체 컨테이너가 재시작되었습니다.
goto BACK


:: =====================================================================
:: [6] 전체 중지
::
::   하는 일:
::     - 실행 중인 모든 컨테이너를 중지하고 제거
::     - Docker 이미지와 DB 데이터 볼륨은 삭제되지 않음
::
::   언제 사용:
::     - 작업을 마치고 시스템을 종료할 때
::     - 시스템 점검 또는 마이그레이션 전
::     - 메모리 자원을 해제하고 싶을 때
::
::   주의: DB 데이터는 보존됩니다. 다시 시작하려면 [1] 전체 배포를 실행하세요.
:: =====================================================================
:STOP
cls
echo.
echo  ================================================================
echo    [6] 전체 중지  -  컨테이너 중지 및 제거
echo  ================================================================
echo.
echo   실행 내용:
echo     - 실행 중인 모든 컨테이너 중지 및 제거
echo     - Docker 이미지와 DB 데이터는 삭제되지 않음
echo.
echo   DB 데이터는 보존됩니다.
echo   다시 시작하려면 [1] 전체 배포를 실행하세요.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- 컨테이너 중지 중... ----
docker compose down
echo.
echo   [완료] 모든 컨테이너가 중지되었습니다. 데이터는 보존되었습니다.
goto BACK


:: =====================================================================
:: [7] 전체 로그 보기
::
::   하는 일:
::     - 모든 컨테이너의 실시간 로그를 통합해서 출력
::     - 최근 100줄부터 시작하여 새 로그를 계속 추적
::
::   사용법:
::     - API 요청/응답, 오류 등을 실시간으로 확인
::     - Ctrl+C 를 누르면 로그 보기를 중단하고 메인 메뉴로 돌아감
:: =====================================================================
:LOGS_ALL
cls
echo.
echo  ================================================================
echo    [7] 전체 로그 보기  -  Ctrl+C 를 누르면 메뉴로 돌아갑니다
echo  ================================================================
echo.
docker compose logs -f --tail=100
echo.
echo   [로그 종료]
goto BACK


:: =====================================================================
:: [8] 백엔드 로그 보기
::
::   하는 일:
::     - 백엔드(FastAPI) 컨테이너의 실시간 로그만 출력
::
::   사용법:
::     - API 오류, DB 쿼리 오류 등 백엔드 문제 디버깅 시 사용
::     - Ctrl+C 를 누르면 로그 보기를 중단하고 메인 메뉴로 돌아감
:: =====================================================================
:LOGS_BACK
cls
echo.
echo  ================================================================
echo    [8] 백엔드 로그 보기  -  Ctrl+C 를 누르면 메뉴로 돌아갑니다
echo  ================================================================
echo.
docker compose logs -f --tail=100 asset-backend
echo.
echo   [로그 종료]
goto BACK


:: =====================================================================
:: [9] 프론트 로그 보기
::
::   하는 일:
::     - 프론트엔드(Nginx/Vue) 컨테이너의 실시간 로그만 출력
::
::   사용법:
::     - 페이지 로드 오류, 프록시 오류 등 프론트 문제 디버깅 시 사용
::     - Ctrl+C 를 누르면 로그 보기를 중단하고 메인 메뉴로 돌아감
:: =====================================================================
:LOGS_FRONT
cls
echo.
echo  ================================================================
echo    [9] 프론트 로그 보기  -  Ctrl+C 를 누르면 메뉴로 돌아갑니다
echo  ================================================================
echo.
docker compose logs -f --tail=100 asset-frontend
echo.
echo   [로그 종료]
goto BACK


:: =====================================================================
:: [10] 이미지 저장  (폐쇄망 / 오프라인 배포용)
::
::   하는 일:
::     - 현재 빌드된 Docker 이미지 3개를 압축 파일로 저장
::     - ./docker-images/ 폴더에 .tar.gz 파일 3개 생성
::       (asset-frontend.tar.gz, asset-backend.tar.gz, postgres-16.tar.gz)
::
::   언제 사용:
::     - 인터넷이 없는 폐쇄망 서버에 배포할 준비를 할 때
::     - 개발 PC에서 빌드·테스트 완료 후 이미지를 내보낼 때
::
::   폐쇄망 배포 순서:
::     [개발 PC] [1] 전체 배포 → [10] 이미지 저장
::               → docker-images\ 폴더를 USB 등으로 복사
::     [폐쇄망 서버] [11] 이미지 불러오기 → [1] 전체 배포
:: =====================================================================
:SAVE
cls
echo.
echo  ================================================================
echo    [10] 이미지 저장  -  폐쇄망 배포용 이미지 파일 내보내기
echo  ================================================================
echo.
echo   저장되는 파일 (./docker-images/ 폴더):
echo     - asset-frontend.tar.gz   (Vue 3 + Nginx)
echo     - asset-backend.tar.gz    (FastAPI + Python)
echo     - postgres-16.tar.gz      (PostgreSQL 16)
echo.
echo   저장 완료 후 docker-images\ 폴더를 폐쇄망 서버로 복사한 뒤
echo   해당 서버에서 [11] 이미지 불러오기를 실행하세요.
echo.
echo   주의: 파일 크기 합산 500MB~1GB, 수 분 소요될 수 있습니다.
echo.
set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

if not exist "docker-images" mkdir docker-images

echo.
echo  ---- [1/3] 프론트엔드 이미지 저장 중... ----
docker save managing-facility-assets-asset-frontend | gzip > docker-images\asset-frontend.tar.gz
if %errorlevel% neq 0 echo   [경고] 프론트엔드 이미지를 찾을 수 없거나 저장에 실패했습니다.

echo  ---- [2/3] 백엔드 이미지 저장 중... ----
docker save managing-facility-assets-asset-backend | gzip > docker-images\asset-backend.tar.gz
if %errorlevel% neq 0 echo   [경고] 백엔드 이미지를 찾을 수 없거나 저장에 실패했습니다.

echo  ---- [3/3] PostgreSQL 이미지 저장 중... ----
docker save postgres:16-alpine | gzip > docker-images\postgres-16.tar.gz
if %errorlevel% neq 0 echo   [경고] PostgreSQL 이미지를 찾을 수 없거나 저장에 실패했습니다.

echo.
echo  ---- 저장된 파일 목록: ----
dir docker-images
echo.
echo   [완료] docker-images\ 폴더를 폐쇄망 서버로 복사한 뒤
echo          해당 서버에서 [11] 이미지 불러오기를 실행하세요.
goto BACK


:: =====================================================================
:: [11] 이미지 불러오기  (폐쇄망 / 오프라인 배포용)
::
::   하는 일:
::     - ./docker-images/ 폴더의 .tar.gz 파일에서 Docker 이미지 가져오기
::     - 불러오기 완료 후 [1] 전체 배포로 시스템 시작 가능
::
::   언제 사용:
::     - 인터넷이 없는 폐쇄망 서버에서 이미지를 설치할 때
::     - 개발 PC에서 복사해온 docker-images\ 폴더가 있을 때
::
::   사전 조건:
::     - 이 폴더 안에 docker-images\ 폴더와 .tar.gz 파일 3개가 있어야 함
::     - Docker Desktop (또는 Docker Engine) 이 실행 중이어야 함
::
::   폐쇄망 배포 순서:
::     1. docker-images\ 폴더를 이 프로젝트 폴더 안에 복사
::     2. [11] 이미지 불러오기 실행
::     3. [1] 전체 배포 실행
:: =====================================================================
:LOAD
cls
echo.
echo  ================================================================
echo    [11] 이미지 불러오기  -  폐쇄망 배포용 이미지 파일 가져오기
echo  ================================================================
echo.
echo   불러올 파일 (./docker-images/ 폴더):
echo     - asset-frontend.tar.gz
echo     - asset-backend.tar.gz
echo     - postgres-16.tar.gz
echo.
echo   불러오기 완료 후 [1] 전체 배포를 실행하면 시스템이 시작됩니다.
echo.

if not exist "docker-images" (
    echo   [오류] docker-images\ 폴더를 찾을 수 없습니다.
    echo.
    echo   개발 PC에서 [10] 이미지 저장을 실행한 뒤
    echo   docker-images\ 폴더를 이 프로젝트 폴더 안에 복사하세요.
    goto BACK
)

set /p confirm=  진행하시겠습니까? (Y/N):
if /i not "%confirm%"=="Y" goto BACK

echo.
echo  ---- [1/3] 프론트엔드 이미지 불러오는 중... ----
if exist "docker-images\asset-frontend.tar.gz" (
    docker load < docker-images\asset-frontend.tar.gz
) else (
    echo   [경고] asset-frontend.tar.gz 파일이 없습니다. 건너뜁니다.
)

echo  ---- [2/3] 백엔드 이미지 불러오는 중... ----
if exist "docker-images\asset-backend.tar.gz" (
    docker load < docker-images\asset-backend.tar.gz
) else (
    echo   [경고] asset-backend.tar.gz 파일이 없습니다. 건너뜁니다.
)

echo  ---- [3/3] PostgreSQL 이미지 불러오는 중... ----
if exist "docker-images\postgres-16.tar.gz" (
    docker load < docker-images\postgres-16.tar.gz
) else (
    echo   [경고] postgres-16.tar.gz 파일이 없습니다. 건너뜁니다.
)

echo.
echo   [완료] 이미지 불러오기가 완료되었습니다.
echo          이제 [1] 전체 배포를 실행하면 시스템이 시작됩니다.
goto BACK


:: =====================================================================
:BACK
echo.
echo  ----------------------------------------------------------------
pause
goto MENU

:EXIT
echo.
echo   종료합니다.
echo.
exit /b 0
