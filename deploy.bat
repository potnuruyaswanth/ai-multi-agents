@echo off
REM ================================================================
REM AI Productivity Assistant - Deploy to GCP from Windows
REM ================================================================

setlocal enabledelayedexpansion

echo ========================================
echo AI Productivity Assistant - Deployment
echo ========================================
echo.

REM Check required tools
echo Checking required tools...

for %%X in (gcloud.cmd, docker.exe, git.exe) do (
    where %%X >nul 2>&1
    if errorlevel 1 (
        echo Error: %%X not found. Please install and add to PATH.
        exit /b 1
    )
)

echo✓ All required tools found

REM Get configuration from user
echo.
echo Please provide configuration values:
echo.
set /p GCP_PROJECT_ID="GCP Project ID: "
set /p FIRESTORE_PROJECT_ID="Firestore Project ID: "
set /p GOOGLE_OAUTH_CLIENT_ID="Google OAuth Client ID: "
set /p GOOGLE_OAUTH_CLIENT_SECRET="Google OAuth Client Secret: "
set /p NOTIFICATION_SENDER_EMAIL="Notification Email: "
set /p SMTP_USER="SMTP Username: "
set /p SMTP_PASSWORD="SMTP Password: "

REM Set GCP project
echo.
echo Setting GCP project...
call gcloud config set project %GCP_PROJECT_ID%

REM Enable APIs
echo Enabling required APIs...
call gcloud services enable ^
    run.googleapis.com ^
    firestore.googleapis.com ^
    cloudbuild.googleapis.com ^
    artifactregistry.googleapis.com ^
    cloudresourcemanager.googleapis.com ^
    container.googleapis.com ^
    secretmanager.googleapis.com

REM Create secrets
echo.
echo Creating Secret Manager secrets...

echo %GOOGLE_OAUTH_CLIENT_SECRET% | gcloud secrets create GOOGLE_OAUTH_CLIENT_SECRET --data-file=- --replication-policy="automatic" 2>nul || (
    echo %GOOGLE_OAUTH_CLIENT_SECRET% | gcloud secrets versions add GOOGLE_OAUTH_CLIENT_SECRET --data-file=-
)

echo %SMTP_PASSWORD% | gcloud secrets create SMTP_PASSWORD --data-file=- --replication-policy="automatic" 2>nul || (
    echo %SMTP_PASSWORD% | gcloud secrets versions add SMTP_PASSWORD --data-file=-
)

echo ✓ Secrets created

REM Build backend image
echo.
echo Building backend Docker image...
docker build -t gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant:latest ./backend
if errorlevel 1 (
    echo Error building image
    exit /b 1
)

REM Push image
echo Pushing image to Container Registry...
call gcloud auth configure-docker
docker push gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant:latest

REM Deploy to Cloud Run
echo.
echo Deploying backend to Cloud Run...
call gcloud run deploy ai-productivity-assistant ^
    --image=gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant:latest ^
    --platform managed ^
    --region=asia-south1 ^
    --memory=512Mi ^
    --timeout=300 ^
    --allow-unauthenticated ^
    --set-env-vars= ^
        APP_NAME="AI Productivity Assistant", ^
        API_PREFIX="/api/v1", ^
        STORAGE_BACKEND="firestore", ^
        FIRESTORE_PROJECT_ID=%FIRESTORE_PROJECT_ID%, ^
        GOOGLE_PROJECT_ID=%GCP_PROJECT_ID%, ^
        GOOGLE_LOCATION="asia-south1", ^
        GOOGLE_OAUTH_CLIENT_ID=%GOOGLE_OAUTH_CLIENT_ID%, ^
        NOTIFICATION_SENDER_EMAIL=%NOTIFICATION_SENDER_EMAIL%, ^
        SMTP_HOST="smtp.gmail.com", ^
        SMTP_PORT="587", ^
        SMTP_USER=%SMTP_USER% ^
    --set-secrets= ^
        GOOGLE_OAUTH_CLIENT_SECRET=GOOGLE_OAUTH_CLIENT_SECRET:latest, ^
        SMTP_PASSWORD=SMTP_PASSWORD:latest

REM Get backend URL
echo.
echo Getting backend URL...
for /f "delims=" %%A in ('gcloud run services describe ai-productivity-assistant --region=asia-south1 --format="value(status.url)"') do (
    set "BACKEND_URL=%%A"
)

echo Backend URL: %BACKEND_URL%

REM Build and deploy frontend
echo.
echo Building frontend Docker image...
docker build --build-arg VITE_API_BASE=%BACKEND_URL% -t gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant-frontend:latest ./frontend
docker push gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant-frontend:latest

echo Deploying frontend to Cloud Run...
call gcloud run deploy ai-productivity-assistant-frontend ^
    --image=gcr.io/%GCP_PROJECT_ID%/ai-productivity-assistant-frontend:latest ^
    --platform managed ^
    --region=asia-south1 ^
    --memory=256Mi ^
    --allow-unauthenticated ^
    --set-env-vars=VITE_API_BASE=%BACKEND_URL%

REM Get frontend URL
for /f "delims=" %%A in ('gcloud run services describe ai-productivity-assistant-frontend --region=asia-south1 --format="value(status.url)"') do (
    set "FRONTEND_URL=%%A"
)

REM Display results
echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Backend URL: %BACKEND_URL%
echo Frontend URL: %FRONTEND_URL%
echo.
echo Next Steps:
echo 1. Update Google OAuth redirect URI to:
echo    %BACKEND_URL%/api/v1/auth/google/callback
echo.
echo 2. Authorize providers at:
echo    %BACKEND_URL%/api/v1/auth/providers
echo.
echo 3. Check status at:
echo    %BACKEND_URL%/api/v1/setup/checklist
echo.
pause
