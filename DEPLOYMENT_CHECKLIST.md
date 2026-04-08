# 🚀 DEPLOYMENT CHECKLIST

Complete this checklist to deploy the AI Productivity Assistant to production.

---

## Phase 1: Prerequisites ✓

### Local Machine Setup
- [ ] Install gcloud CLI: https://cloud.google.com/sdk/docs/install
- [ ] Install Docker Desktop: https://www.docker.com/products/docker-desktop
- [ ] Install Git
- [ ] Install Node.js 20+: https://nodejs.org/
- [ ] Install Python 3.11+: https://www.python.org/
- [ ] Verify installations:
  ```bash
  gcloud --version
  docker --version
  git --version
  node --version
  python --version
  ```

### GCP Project Setup
- [ ] Create GCP Project: https://console.cloud.google.com
- [ ] Enable billing on the project
- [ ] Create Firebase Project (same or separate)
- [ ] Get GCP Project ID
- [ ] Get Firebase Project ID

### Google OAuth Setup
- [ ] Go to Google Cloud Console
- [ ] Create OAuth 2.0 Application
- [ ] Download credentials
- [ ] Copy **Client ID** to safe location
- [ ] Copy **Client Secret** to safe location

### Email Setup
- [ ] Setup Gmail account or email provider
- [ ] Enable 2FA on Gmail (if using Gmail)
- [ ] Generate App Password: https://myaccount.google.com/apppasswords
- [ ] Copy app password to safe location

---

## Phase 2: Local Testing ✓

### Setup Local Environment

- [ ] Clone repository:
  ```bash
  git clone <your-repo-url>
  cd ai-productivity-assistant
  ```

- [ ] Run setup script:
  ```bash
  # Linux/Mac
  chmod +x scripts/setup-local.sh
  ./scripts/setup-local.sh
  
  # Windows
  setup.bat
  ```

### Configure & Test Locally

- [ ] Edit `backend/.env`:
  ```
  GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
  GOOGLE_OAUTH_CLIENT_SECRET=<your-secret>
  NOTIFICATION_SENDER_EMAIL=<your-email>
  SMTP_USER=<your-email>
  SMTP_PASSWORD=<your-app-password>
  ```

- [ ] Start services:
  ```bash
  docker-compose up -d
  ```

- [ ] Verify services:
  ```bash
  curl http://localhost:8000/          # Should return 200
  curl http://localhost:8000/health    # Should return healthy
  curl http://localhost:8000/docs      # Should show docs
  ```

- [ ] Open frontend:
  ```bash
  open http://localhost:5173  # Should load dashboard
  ```

- [ ] Test API endpoints:
  ```bash
  curl http://localhost:8000/api/v1/setup/checklist | jq
  ```

### Local Validation

- [ ] All services responding
- [ ] No errors in logs
- [ ] Frontend loads without errors
- [ ] API documentation accessible

---

## Phase 3: GCP Project Setup ✓

### Authenticate with GCP

- [ ] Login to GCP:
  ```bash
  gcloud auth login
  ```

- [ ] Set your project:
  ```bash
  gcloud config set project <YOUR_PROJECT_ID>
  ```

- [ ] Verify authentication:
  ```bash
  gcloud auth list
  ```

### Enable Required APIs

- [ ] Enable APIs:
  ```bash
  gcloud services enable \
      run.googleapis.com \
      firestore.googleapis.com \
      cloudbuild.googleapis.com \
      artifactregistry.googleapis.com \
      cloudresourcemanager.googleapis.com \
      container.googleapis.com \
      secretmanager.googleapis.com
  ```

- [ ] Verify APIs enabled:
  ```bash
  gcloud services list --enabled | grep run
  ```

### Create Firestore Database

- [ ] Create Firestore database:
  ```bash
  gcloud firestore databases create \
      --database="(default)" \
      --location="asia-south1"
  ```

  Or use existing database (no action needed)

---

## Phase 4: Configure Secrets ✓

### Create Secret Manager Secrets

In Cloud Console or via CLI:

- [ ] Create GOOGLE_OAUTH_CLIENT_SECRET:
  ```bash
  echo -n "<YOUR_SECRET>" | gcloud secrets create GOOGLE_OAUTH_CLIENT_SECRET \
      --data-file=- \
      --replication-policy="automatic"
  ```

- [ ] Create SMTP_PASSWORD:
  ```bash
  echo -n "<YOUR_APP_PASSWORD>" | gcloud secrets create SMTP_PASSWORD \
      --data-file=- \
      --replication-policy="automatic"
  ```

- [ ] Verify secrets created:
  ```bash
  gcloud secrets list
  ```

---

## Phase 5: Deployment ✓

### Option A: Automated Deployment (Recommended)

- [ ] Set environment variables:
  ```bash
  export GOOGLE_PROJECT_ID="your-project-id"
  export FIRESTORE_PROJECT_ID="your-firebase-project-id"
  export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
  export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
  export NOTIFICATION_SENDER_EMAIL="your-email@gmail.com"
  export SMTP_USER="your-email"
  export SMTP_PASSWORD="your-app-password"
  ```

- [ ] Run deployment script:
  ```bash
  # Linux/Mac
  chmod +x scripts/deploy.sh
  ./scripts/deploy.sh
  
  # Windows
  deploy.bat
  ```

- [ ] Script will automatically:
  - [ ] Validate all tools and environment variables
  - [ ] Enable required APIs
  - [ ] Create secrets
  - [ ] Build Docker images
  - [ ] Push to Container Registry
  - [ ] Deploy backend to Cloud Run
  - [ ] Deploy frontend to Cloud Run
  - [ ] Run validation checks

- [ ] Note the output URLs:
  - Backend URL: `https://ai-productivity-assistant-XXXX.run.app`
  - Frontend URL: `https://ai-productivity-assistant-frontend-XXXX.run.app`

### Option B: Manual Deployment (If Needed)

- [ ] Build backend image:
  ```bash
  docker build -t gcr.io/$GOOGLE_PROJECT_ID/ai-productivity-assistant:latest ./backend
  ```

- [ ] Push image:
  ```bash
  gcloud auth configure-docker
  docker push gcr.io/$GOOGLE_PROJECT_ID/ai-productivity-assistant:latest
  ```

- [ ] Deploy to Cloud Run:
  ```bash
  gcloud run deploy ai-productivity-assistant \
      --image=gcr.io/$GOOGLE_PROJECT_ID/ai-productivity-assistant:latest \
      --platform managed \
      --region=asia-south1 \
      --memory=512Mi \
      --timeout=300 \
      --allow-unauthenticated \
      [... environment variables and secrets ...]
  ```

---

## Phase 6: Post-Deployment Configuration ✓

### Update OAuth Redirect URI

- [ ] Get your backend URL:
  ```bash
  gcloud run services describe ai-productivity-assistant \
      --region=asia-south1 \
      --format='value(status.url)'
  ```

- [ ] Go to Google Cloud Console > APIs & Credentials
- [ ] Edit your OAuth application
- [ ] Update Authorized redirect URIs to:
  ```
  https://your-backend-url/api/v1/auth/google/callback
  ```

- [ ] Save changes

### Connect OAuth Providers

- [ ] Visit provider authorization endpoint:
  ```
  https://your-backend-url/api/v1/auth/providers
  ```

- [ ] Authorize each provider:
  - [ ] Gmail
  - [ ] Google Calendar
  - [ ] Google Tasks
  - [ ] Google Drive

- [ ] Verify connections in:
  ```
  https://your-backend-url/api/v1/setup/checklist
  ```

---

## Phase 7: Validation ✓

### Run Full Validation

- [ ] Execute validation script:
  ```bash
  chmod +x scripts/validate-deployment.sh
  ./scripts/validate-deployment.sh https://your-backend-url
  ```

- [ ] Script validates:
  - [ ] Backend connectivity
  - [ ] Health endpoints
  - [ ] Database access
  - [ ] OAuth configuration
  - [ ] SMTP readiness
  - [ ] All API endpoints
  - [ ] CORS headers
  - [ ] Performance metrics
  - [ ] Application version
  - [ ] Frontend accessibility
  - [ ] Metrics endpoint
  - [ ] Provider status

- [ ] All checks should pass (0 failed checks)

### Manual Validation

- [ ] Test root endpoint:
  ```bash
  curl https://your-backend-url/
  ```

- [ ] Test health:
  ```bash
  curl https://your-backend-url/health
  ```

- [ ] Test deep health:
  ```bash
  curl https://your-backend-url/health/deep | jq
  ```

- [ ] Test setup checklist:
  ```bash
  curl https://your-backend-url/api/v1/setup/checklist | jq
  ```

- [ ] Test API docs:
  ```bash
  open https://your-backend-url/docs
  ```

- [ ] Test frontend:
  ```bash
  open https://your-frontend-url
  ```

---

## Phase 8: Enable CI/CD (Optional but Recommended) ✓

### Setup GitHub Secrets

- [ ] Copy repository URL
- [ ] Go to GitHub
- [ ] Settings > Secrets and variables > Actions
- [ ] Add secrets:
  - [ ] `GCP_PROJECT_ID`
  - [ ] `FIRESTORE_PROJECT_ID`
  - [ ] `GOOGLE_OAUTH_CLIENT_ID`
  - [ ] `GOOGLE_OAUTH_CLIENT_SECRET`
  - [ ] `NOTIFICATION_SENDER_EMAIL`
  - [ ] `SMTP_USER`
  - [ ] `SMTP_PASSWORD`
  - [ ] `SMTP_HOST`
  - [ ] `SMTP_PORT`
  - [ ] `STORAGE_BACKEND` (set to: firestore)
  - [ ] `WIF_PROVIDER` (Workload Identity Provider, if using)
  - [ ] `WIF_SERVICE_ACCOUNT` (GitHub service account, if using)

### Test CI/CD (Optional)

- [ ] Make a test commit:
  ```bash
  git add .
  git commit -m "Test CI/CD"
  git push origin main
  ```

- [ ] Monitor GitHub Actions:
  - [ ] Go to repository > Actions tab
  - [ ] Watch deploy workflow
  - [ ] Verify all steps pass

---

## Phase 9: Post-Deployment Testing ✓

### Test Core Functionality

- [ ] Test daily digest:
  ```
  https://your-backend-url/api/v1/daily-digest
  ```

- [ ] Create a test task in Google Tasks
- [ ] Wait a few moments
- [ ] Refresh daily digest - should appear

- [ ] Check provider connections:
  ```
  https://your-backend-url/api/v1/google/auth-status
  ```

- [ ] Verify Drive integration:
  ```bash
  curl https://your-backend-url/api/v1/drive/files
  ```

### Test Email Notifications (Optional)

- [ ] Check notification configuration in setup checklist
- [ ] System may send test notification if configured
- [ ] Check email inbox for test message

---

## Phase 10: Monitoring Setup (Optional) ✓

### Enable Cloud Monitoring

- [ ] Go to Cloud Console > Monitoring
- [ ] Create uptime check for backend URL
- [ ] Create alert policy for errors
- [ ] Enable detailed logging

### Review Logs

- [ ] View backend logs:
  ```bash
  gcloud run logs read ai-productivity-assistant --limit=50
  ```

- [ ] View frontend logs:
  ```bash
  gcloud run logs read ai-productivity-assistant-frontend --limit=50
  ```

---

## ✅ FINAL CHECKLIST

Before considering deployment complete:

- [ ] Local setup and testing completed
- [ ] GCP project configured
- [ ] Secrets created in Secret Manager
- [ ] Deployment script executed successfully
- [ ] Backend and frontend deployed to Cloud Run
- [ ] OAuth redirect URI updated
- [ ] OAuth providers authorized
- [ ] All validation checks passing
- [ ] Health endpoints responding
- [ ] Frontend loads and displays dashboard
- [ ] API documentation accessible
- [ ] Logs show no errors
- [ ] GitHub Actions (if enabled) working

---

## 🎉 Deployment Complete!

Your AI Productivity Assistant is now live!

### Access Points

- **API**: https://your-backend-url
- **Dashboard**: https://your-frontend-url
- **API Docs**: https://your-backend-url/docs
- **Status**: https://your-backend-url/health/deep

### Next Steps

1. Test functionality with real data
2. Configure Cloud Monitoring and alerts
3. Setup backup strategy for Firestore
4. Customize dashboard if desired
5. Add team members to GCP project

### Support

- Check logs: `gcloud run logs read ai-productivity-assistant`
- View health: `https://your-backend-url/health/deep`
- Run validation: `./scripts/validate-deployment.sh`
- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Status**: ✅ DEPLOYMENT READY

**Last Updated**: January 8, 2024  
**Version**: 1.0.0
