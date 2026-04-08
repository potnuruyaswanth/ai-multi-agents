# Production Deployment Guide

## Complete End-to-End Deployment for AI Productivity Assistant

This guide covers deploying the AI Productivity Assistant to Google Cloud Platform using Cloud Run, Firestore, and Secret Manager.

---

## Prerequisites

### Required Tools
- `gcloud` CLI (Google Cloud SDK)
- `docker` and `docker-compose`
- `git`
- Node.js 20+ and npm
- Python 3.11+

### GCP Resources
- GCP Project with billing enabled
- Firebase Project for Firestore (can be same as main project)
- Google OAuth Application configured
- Service account with appropriate permissions

### Configuration Values
Gather these before starting:
- GCP Project ID
- Firebase Project ID (for Firestore)
- Google OAuth Client ID and Secret
- SMTP credentials (e.g., Gmail app password)
- Sender email address

---

## Phase 1: Prepare Local Environment

### 1.1 Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ai-productivity-assistant

# Run local setup script
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

### 1.2 Configure Environment Variables

```bash
# Edit backend configuration
nano backend/.env

# Required values:
# APP_NAME=AI Productivity Assistant
# STORAGE_BACKEND=mongodb (for local) or firestore (for production)
# GOOGLE_OAUTH_CLIENT_ID=your-client-id
# GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
# NOTIFICATION_SENDER_EMAIL=your-email@gmail.com
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
```

### 1.3 Run Locally

#### Using Docker Compose (Recommended)
```bash
docker-compose up -d

# Verify services
curl http://localhost:8000/  # Backend
curl http://localhost:5173/   # Frontend
```

#### Using Manual Setup
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn api.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### 1.4 Test Locally

```bash
# API Documentation
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# Setup checklist
curl http://localhost:8000/api/v1/setup/checklist

# Frontend
open http://localhost:5173
```

---

## Phase 2: Prepare for GCP Deployment

### 2.1 Create GCP Project and Enable APIs

```bash
# Set variables
export GCP_PROJECT_ID="your-project-id"
export REGION="asia-south1"

# Set current project
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    cloudresourcemanager.googleapis.com \
    container.googleapis.com \
    secretmanager.googleapis.com
```

### 2.2 Create Secret Manager Secrets

```bash
# OAuth Client Secret
echo -n "your-oauth-secret" | gcloud secrets create GOOGLE_OAUTH_CLIENT_SECRET \
    --data-file=- \
    --replication-policy="automatic"

# SMTP Password
echo -n "your-app-password" | gcloud secrets create SMTP_PASSWORD \
    --data-file=- \
    --replication-policy="automatic"
```

### 2.3 Create Service Account (Optional but Recommended)

```bash
# Create service account
gcloud iam service-accounts create ai-assistant-sa \
    --display-name="AI Productivity Assistant Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:ai-assistant-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:ai-assistant-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 2.4 Configure Firestore

```bash
# Create Firestore database if not exists
gcloud firestore databases create \
    --database="(default)" \
    --location="$REGION"

# Or use existing database - no action needed
```

---

## Phase 3: Automated Deployment

### 3.1 Using Deployment Script (Recommended)

```bash
# Set environment variables
export GOOGLE_PROJECT_ID="your-project-id"
export FIRESTORE_PROJECT_ID="your-firebase-project-id"
export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
export NOTIFICATION_SENDER_EMAIL="your-email@gmail.com"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# Make script executable and run
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The script will:
1. Validate all required tools and environment variables
2. Setup GCP project and enable APIs
3. Create Secret Manager secrets
4. Build and push Docker images
5. Deploy backend to Cloud Run
6. Deploy frontend to Cloud Run
7. Configure OAuth redirect URIs
8. Run validation checks

### 3.2 Manual Deployment (Step by Step)

```bash
# Build backend image
docker build -t gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest ./backend
docker tag gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest \
           gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:$(date +%s)

# Push to Google Container Registry
gcloud auth configure-docker
docker push gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest

# Deploy to Cloud Run
gcloud run deploy ai-productivity-assistant \
    --image=gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest \
    --platform managed \
    --region=$REGION \
    --memory=512Mi \
    --timeout=300 \
    --allow-unauthenticated \
    --set-env-vars="\
APP_NAME=AI Productivity Assistant,\
API_PREFIX=/api/v1,\
STORAGE_BACKEND=firestore,\
FIRESTORE_PROJECT_ID=$FIRESTORE_PROJECT_ID,\
GOOGLE_PROJECT_ID=$GCP_PROJECT_ID,\
GOOGLE_LOCATION=$REGION,\
GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID,\
NOTIFICATION_SENDER_EMAIL=$NOTIFICATION_SENDER_EMAIL,\
SMTP_HOST=smtp.gmail.com,\
SMTP_PORT=587,\
SMTP_USER=$SMTP_USER" \
    --set-secrets="\
GOOGLE_OAUTH_CLIENT_SECRET=GOOGLE_OAUTH_CLIENT_SECRET:latest,\
SMTP_PASSWORD=SMTP_PASSWORD:latest"

# Repeat for frontend
docker build -t gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant-frontend:latest ./frontend
docker push gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant-frontend:latest

# Get backend URL
BACKEND_URL=$(gcloud run services describe ai-productivity-assistant --region=$REGION --format='value(status.url)')

gcloud run deploy ai-productivity-assistant-frontend \
    --image=gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant-frontend:latest \
    --platform managed \
    --region=$REGION \
    --memory=256Mi \
    --allow-unauthenticated \
    --set-env-vars="VITE_API_BASE=$BACKEND_URL"
```

---

## Phase 4: Post-Deployment Configuration

### 4.1 Update Google OAuth Redirect URI

```bash
# Get the actual service URL
BACKEND_URL=$(gcloud run services describe ai-productivity-assistant --region=$REGION --format='value(status.url)')

echo "Go to: https://console.developers.google.com/apis/credentials"
echo "Update OAuth application redirect URIs to:"
echo "$BACKEND_URL/api/v1/auth/google/callback"
```

### 4.2 Verify Deployment

```bash
# Health check
curl $BACKEND_URL/health

# Deep health check
curl $BACKEND_URL/health/deep

# Setup checklist
curl $BACKEND_URL/api/v1/setup/checklist

# View API documentation
open $BACKEND_URL/docs

# Access frontend
echo "Frontend: https://ai-productivity-assistant-frontend-REGION.run.app"
```

### 4.3 Connect OAuth Providers

1. Visit the setup endpoint:
   ```
   $BACKEND_URL/api/v1/setup/checklist
   ```

2. Authorize each provider through the OAuth URLs provided:
   - Gmail
   - Google Calendar
   - Google Tasks
   - Google Drive

3. Verify all providers are connected:
   ```bash
   curl $BACKEND_URL/api/v1/setup/checklist | grep -A 20 "providers"
   ```

---

## Phase 5: Enable CI/CD with GitHub Actions

### 5.1 Setup Workload Identity (Recommended Security)

```bash
# Create Workload Identity Provider
gcloud iam workload-identity-pools create "github-pool" \
    --project=$GCP_PROJECT_ID \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Create workload identity provider key
WORKLOAD_IDENTITY_PROVIDER=$(gcloud iam workload-identity-pools describe "github-pool" \
    --project=$GCP_PROJECT_ID \
    --location="global" \
    --format='value(name)')

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project=$GCP_PROJECT_ID \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,assertion.aud=assertion.aud" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# Create service account for GitHub
gcloud iam service-accounts create github-actions-sa \
    --display-name="GitHub Actions Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### 5.2 Configure GitHub Secrets

```
Repository Settings > Secrets and variables > Actions

Required secrets:
- GCP_PROJECT_ID: Your GCP project ID
- FIRESTORE_PROJECT_ID: Your Firebase project ID
- GOOGLE_OAUTH_CLIENT_ID: OAuth client ID
- GOOGLE_OAUTH_CLIENT_SECRET: OAuth client secret
- NOTIFICATION_SENDER_EMAIL: Sender email
- SMTP_USER: SMTP username
- SMTP_PASSWORD: SMTP password
- SMTP_HOST: SMTP host (default: smtp.gmail.com)
- SMTP_PORT: SMTP port (default: 587)
- STORAGE_BACKEND: "firestore" for production
- WIF_PROVIDER: Workload Identity Provider resource name
- WIF_SERVICE_ACCOUNT: GitHub Actions service account email
```

### 5.3 Push and Deploy

```bash
git add .
git commit -m "Enable CI/CD deployment"
git push origin main

# Monitor deployment in GitHub Actions tab
# Access deployed services:
# Backend: $BACKEND_URL
# Frontend: https://ai-productivity-assistant-frontend-$REGION.run.app
```

---

## Phase 6: Monitoring and Maintenance

### 6.1 View Logs

```bash
# Backend logs
gcloud run logs read ai-productivity-assistant --region=$REGION --limit=50

# Frontend logs
gcloud run logs read ai-productivity-assistant-frontend --region=$REGION --limit=50

# Real-time logs
gcloud run logs read ai-productivity-assistant --region=$REGION --follow
```

### 6.2 Monitor Performance

```bash
# Check Cloud Run metrics
gcloud run describe ai-productivity-assistant --region=$REGION

# View metrics in Console:
# https://console.cloud.google.com/run/detail/$REGION/ai-productivity-assistant/metrics
```

### 6.3 Update Services

```bash
# After code changes, redeploy:
./scripts/deploy.sh

# Or manually rebuild and redeploy:
docker build -t gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest ./backend
docker push gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest

gcloud run deploy ai-productivity-assistant \
    --image=gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant:latest \
    --region=$REGION \
    --update-env-vars SOME_VAR=new_value
```

### 6.4 Backup Firestore Data

```bash
# Export Firestore data
gcloud firestore export gs://$BACKUP_BUCKET/backup-$(date +%Y%m%d-%H%M%S)

# Restore if needed
gcloud firestore import gs://$BACKUP_BUCKET/backup-20240101-120000
```

---

## Troubleshooting

### Issue: Cloud Run service deployment fails

```bash
# Check build logs
gcloud builds log -s <BUILD_ID> --limit=50

# Verify image exists and is correct
docker images | grep ai-productivity-assistant

# Check secrets exist
gcloud secrets list
```

### Issue: OAuth not working

```bash
# Verify OAuth configuration
curl $BACKEND_URL/api/v1/setup/checklist | jq '.oauth'

# Check redirect URI is correct
# Ensure it matches Google OAuth settings exactly
```

### Issue: Firestore connection failing

```bash
# Verify Firestore is accessible
gcloud firestore databases list

# Check service account has correct permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID
```

### Issue: SMTP email not sending

```bash
# Verify SMTP configuration
curl $BACKEND_URL/health/deep | jq '.components.smtp'

# Test SMTP credentials manually
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
server.quit()
print('SMTP OK')
"
```

---

## Cleanup

### Remove All Resources

```bash
# Delete Cloud Run services
gcloud run services delete ai-productivity-assistant --region=$REGION
gcloud run services delete ai-productivity-assistant-frontend --region=$REGION

# Delete container images
gcloud container images delete gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant --quiet
gcloud container images delete gcr.io/$GCP_PROJECT_ID/ai-productivity-assistant-frontend --quiet

# Delete secrets
gcloud secrets delete GOOGLE_OAUTH_CLIENT_SECRET --quiet
gcloud secrets delete SMTP_PASSWORD --quiet

# Delete service account
gcloud iam service-accounts delete ai-assistant-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com
```

---

## Performance Tuning

### Cloud Run Memory/CPU Configuration

```bash
# Increase memory if experiencing timeouts
gcloud run deploy ai-productivity-assistant \
    --region=$REGION \
    --memory=1Gi \
    --cpu=2
```

### Firestore Indexes

Firestore automatically creates indexes for common queries. To manage:

```bash
# View existing indexes
gcloud firestore indexes list

# Create composite index if needed (for complex queries)
# This is typically done through Cloud Console
```

### Database Connection Pooling

The application uses connection pooling. Adjust in `database/repository.py` if needed:

```python
# MongoDB connection pool (default: 10-50)
# Firestore manages connection on its own
```

---

## Security Best Practices

1. **Rotate Secrets Regularly**
   ```bash
   # Create new secret version
   echo -n "new-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=-
   ```

2. **Enable VPC Service Controls**
   - See: https://cloud.google.com/vpc-service-controls

3. **Set up Firewall Rules**
   - Restrict Cloud Run to specific IPs if needed
   - Use Cloud Armor for DDoS protection

4. **Enable Audit Logging**
   ```bash
   gcloud logging sinks create ai-assistant-audit \
       bigquery.googleapis.com/projects/$GCP_PROJECT_ID/datasets/audit_logs \
       --log-filter='resource.type="cloud_run_revision"'
   ```

5. **Use HTTPS Only**
   - Cloud Run provides HTTPS by default
   - Enforce in application code

---

## Next Steps

After successful deployment:
1. Test all OAuth provider connections
2. Send test notifications via SMTP
3. Create sample tasks/events for daily digest
4. Monitor logs and metrics
5. Set up Cloud Monitoring alerts
6. Configure custom domain (optional)

For additional support, check:
- Backend logs: `gcloud run logs read ai-productivity-assistant`
- API documentation: `$BACKEND_URL/docs`
- Status page: `$BACKEND_URL/health/deep`
