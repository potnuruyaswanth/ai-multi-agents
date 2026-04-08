# AI Productivity Assistant - Multi-Agent System

A production-ready AI productivity assistant built with multi-agent architecture, Google Workspace integration, and cloud-native deployment.

**Status**: ✅ Production Ready | 🚀 Cloud Deployment Ready | 🔒 Enterprise Security

---

## 🎯 Project Overview

The AI Productivity Assistant is a comprehensive multi-agent system designed to manage productivity tasks with artificial intelligence. It integrates with Google Workspace services (Gmail, Calendar, Tasks, Drive) and provides real-time notifications, daily digests, and intelligent task orchestration.

### Key Features

- ✅ **Multi-Agent Orchestration**: Coordinated agents for email, tasks, calendar, notifications, and chatbot
- ✅ **Google Workspace Integration**: Gmail, Calendar, Tasks, Drive APIs with OAuth 2.0
- ✅ **Daily Digest**: Summarized view of tasks, events, and reminders
- ✅ **Smart Drive Integration**: Automatic detection and suggestion of resumes/portfolios
- ✅ **Email Notifications**: SMTP-based notifications with configurable scheduling
- ✅ **Dual Storage Backends**: MongoDB for development, Firestore for production
- ✅ **Cloud Native**: Deploy to Google Cloud Run with one command
- ✅ **CI/CD Ready**: GitHub Actions workflows included
- ✅ **Production Monitoring**: Health checks, metrics, and comprehensive logging

### Tech Stack

**Backend**: FastAPI (Python 3.11+) | **Frontend**: React 18 + Vite | **Databases**: MongoDB, Firestore | **Cloud**: GCP Cloud Run

---

## 📋 Prerequisites

### Required Tools
- **gcloud** CLI (Google Cloud SDK)
- **docker** & **docker-compose**
- **git**, **Node.js 20+**, **Python 3.11+**

### GCP Resources Required
- GCP Project with billing enabled
- Firebase Project (for Firestore)
- Google OAuth Application credentials
- SMTP credentials (Gmail app password recommended)

---

## 🚀 Getting Started

### Option 1: Local Development (Fastest)

```bash
# Clone repository
git clone <your-repo-url>
cd ai-productivity-assistant

# Run setup script
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# Choose: Docker Compose or Manual setup

# Docker Compose (Recommended)
docker-compose up -d

# Access services:
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

**Setup time**: 5-10 minutes

### Option 2: Production Deployment (GCP Cloud Run)

```bash
# Prepare configuration
export GOOGLE_PROJECT_ID="your-project-id"
export FIRESTORE_PROJECT_ID="your-firebase-project-id"
export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
export NOTIFICATION_SENDER_EMAIL="your-email@gmail.com"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# Run deployment
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Validates, builds, deploys, and configures everything automatically
```

**Setup time**: 15-20 minutes

---

## 📁 Project Structure

```
ai-productivity-assistant/
├── backend/                          # FastAPI backend
│   ├── agents/                       # Multi-agent system
│   │   ├── orchestrator_agent/       # Coordinates all agents
│   │   ├── email_agent/              # Gmail integration
│   │   ├── task_agent/               # Task management
│   │   ├── calendar_agent/           # Calendar management
│   │   ├── notification_agent/       # Email notifications
│   │   ├── chatbot_agent/            # AI chatbot
│   │   └── form_agent/               # Form autofill
│   ├── api/                          # API routes
│   │   ├── main.py                   # FastAPI app setup
│   │   ├── auth_routes.py            # OAuth routes
│   │   ├── google_routes.py          # Google Workspace routes
│   │   ├── health_routes.py          # Health check endpoints
│   │   ├── setup_routes.py           # Deployment checklist
│   │   └── routes.py                 # Main API routes
│   ├── integrations/                 # External service clients
│   │   ├── gmail_service.py          # Gmail API client
│   │   ├── calendar_service.py       # Calendar API client
│   │   ├── tasks_service.py          # Tasks API client
│   │   ├── drive_service.py          # Drive API client
│   │   └── google_oauth.py           # OAuth management
│   ├── database/                     # Data persistence
│   │   ├── repository.py             # MongoDB/Firestore abstraction
│   │   ├── models.py                 # Pydantic data models
│   │   └── schemas.py                # Database schemas
│   ├── config/                       # Configuration
│   │   └── settings.py               # Environment-based settings
│   ├── Dockerfile                    # Production Docker image
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Runtime configuration
├── frontend/                         # React + Vite frontend
│   ├── src/
│   │   ├── components/               # Reusable React components
│   │   ├── pages/                    # Page components
│   │   │   └── DashboardPage.jsx     # Main dashboard
│   │   └── styles.css                # Global styles
│   ├── Dockerfile                    # Production image
│   ├── Dockerfile.dev                # Development image
│   ├── vite.config.js                # Vite configuration
│   ├── package.json                  # npm dependencies
│   └── .env                          # Frontend configuration
├── scripts/                          # Deployment and setup scripts
│   ├── deploy.sh                     # Complete GCP deployment
│   ├── setup-local.sh                # Local setup
│   └── validate-deployment.sh        # Post-deployment validation
├── .github/workflows/                # GitHub Actions CI/CD
│   ├── deploy.yml                    # Auto-deploy on push
│   └── tests.yml                     # Tests and quality checks
├── docker-compose.yml                # Local development stack
├── DEPLOYMENT.md                     # Complete deployment guide
└── README.md                         # This file
```

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Application
APP_NAME=AI Productivity Assistant
API_PREFIX=/api/v1

# Storage Backend
STORAGE_BACKEND=firestore              # or 'mongodb' for dev
FIRESTORE_PROJECT_ID=your-firebase-project
FIRESTORE_DATABASE_ID=(default)

# MongoDB (local development)
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_productivity_assistant

# Google Cloud
GOOGLE_PROJECT_ID=your-gcp-project
GOOGLE_LOCATION=asia-south1

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Notifications
NOTIFICATION_SENDER_EMAIL=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
VITE_API_BASE=http://localhost:8000              # or Cloud Run URL
```

---

## 🎓 API Documentation

### Health & Monitoring Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Deep health check (database, OAuth, SMTP)
curl http://localhost:8000/health/deep

# Application version
curl http://localhost:8000/version

# Application metrics
curl http://localhost:8000/metrics

# Setup checklist (deployment readiness)
curl http://localhost:8000/api/v1/setup/checklist

# Interactive docs: http://localhost:8000/docs
```

### Key API Routes

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/google/callback` | GET | OAuth callback handler |
| `/api/v1/auth/providers` | GET | List available providers |
| `/api/v1/google/auth-status` | GET | Check provider connection status |
| `/api/v1/daily-digest` | GET | Get daily task/event summary |
| `/api/v1/gmail/sync` | POST | Sync Gmail messages |
| `/api/v1/calendar/events` | GET | Fetch calendar events |
| `/api/v1/tasks/sync` | POST | Sync tasks |
| `/api/v1/drive/files` | GET | List Drive resources |

---

## 📊 Daily Digest

The daily digest endpoint provides a consolidated view of the user's productivity:

```bash
curl http://localhost:8000/api/v1/daily-digest | jq

# Response includes:
# - Task count and top 10 tasks
# - Event count and top 10 events  
# - Reminder count and details
# - Timestamp
```

---

## 🔐 Deployment Security

### Local Development

```bash
# Use MongoDB (no external dependencies)
STORAGE_BACKEND=mongodb
MONGO_URI=mongodb://localhost:27017
```

### Production (GCP)

```bash
# Use Firestore with Secret Manager
STORAGE_BACKEND=firestore
FIRESTORE_PROJECT_ID=your-firebase-project

# Secrets stored in GCP Secret Manager:
- GOOGLE_OAUTH_CLIENT_SECRET
- SMTP_PASSWORD
```

**Security Features**:
- ✅ OAuth 2.0 for all Google integrations
- ✅ HTTPS-only communication (Cloud Run enforced)
- ✅ Secrets in Secret Manager, not in plaintext
- ✅ Service account-based authentication
- ✅ Cross-project IAM for Firestore access
- ✅ CORS properly configured
- ✅ Health checks for system validation

---

## 🚀 Deployment Options

### Option A: Full Automated Deployment

```bash
# One-command deployment with all validation
./scripts/deploy.sh

# Deploys:
# 1. Backend to Cloud Run (512Mi, asia-south1)
# 2. Frontend to Cloud Run (256Mi)
# 3. Configures OAuth, secrets, IAM
# 4. Validates all endpoints
```

### Option B: Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions covering:
- Local environment setup
- GCP project preparation
- Secret Manager configuration
- Manual Cloud Run deployment
- Post-deployment validation
- GitHub Actions CI/CD setup
- Monitoring and maintenance

### Option C: GitHub Actions (CI/CD)

Push to main branch - GitHub Actions automatically:
- Runs tests
- Builds Docker images
- Pushes to Container Registry
- Deploys to Cloud Run
- Validates endpoints

---

## ✅ Validation & Testing

### Post-Deployment Validation

```bash
# Run comprehensive validation
./scripts/validate-deployment.sh https://your-cloud-run-url

# Checks:
# ✓ Service connectivity
# ✓ Health endpoints
# ✓ Database access
# ✓ OAuth configuration
# ✓ SMTP readiness
# ✓ All API endpoints
# ✓ CORS headers
# ✓ Performance metrics
```

### Running Tests Locally

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests
pytest -v --cov=.

# Frontend
cd frontend
npm run build
```

---

## 📈 Monitoring & Logging

### View Logs

```bash
# Real-time backend logs
gcloud run logs read ai-productivity-assistant --follow

# Frontend logs
gcloud run logs read ai-productivity-assistant-frontend --follow

# Last 50 lines
gcloud run logs read ai-productivity-assistant --limit=50
```

### Metrics

```bash
# View Cloud Run metrics
gcloud run describe ai-productivity-assistant --region=asia-south1

# Or in Cloud Console:
# https://console.cloud.google.com/run/stats
```

---

## 🔄 Update & Maintenance

### Update Code & Re-deploy

```bash
git add .
git commit -m "Updated features"
git push origin main

# GitHub Actions automatically handles deployment
# Or manually redeploy:
./scripts/deploy.sh
```

### Backup Firestore

```bash
# Export data
gcloud firestore export gs://your-bucket/backup-$(date +%Y%m%d)

# Restore data
gcloud firestore import gs://your-bucket/backup-20240101
```

---

## 🐛 Troubleshooting

### Issue: Service not responding

```bash
# Check logs
gcloud run logs read ai-productivity-assistant --limit=20

# Check health
curl https://your-service-url/health/deep | jq
```

### Issue: OAuth not working

```bash
# Verify configuration
curl https://your-service-url/api/v1/setup/checklist | jq '.oauth'

# Update redirect URI in Google Cloud Console
```

### Issue: SMTP email not sending

```bash
# Check SMTP configuration
curl https://your-service-url/health/deep | jq '.components.smtp'

# Verify Gmail app password
```

See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) for comprehensive troubleshooting guide.

---

## 📚 Architecture Details

### Multi-Agent System

```
┌─────────────┐
│ Orchestrator│
├─────────────┤
├─ Email Agent      → Gmail API
├─ Task Agent       → Tasks API
├─ Calendar Agent   → Calendar API
├─ Notification     → SMTP
├─ Chatbot Agent    → LLM
└─ Form Agent       → Autofill
```

### Data Flow

```
User Input → Orchestrator → Sub-agents → Integrations → Response
    ↓
Database (MongoDB/Firestore) → State Management
    ↓
Notifications → SMTP → Email
```

### Storage Abstraction

```
Repository Pattern
├─ MongoDB (Development)
│  └─ Local testing & development
└─ Firestore (Production)
   └─ GCP-managed, scalable, zero-ops
```

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally with `docker-compose up`
3. Run tests: `pytest backend/` and `npm run build frontend/`
4. Push and create a Pull Request
5. GitHub Actions will validate automatically

---

## 📄 License

[Specify your license here]

---

## 📞 Support

For issues and questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
2. Review API docs: `/docs` endpoint
3. Check logs: `gcloud run logs read ai-productivity-assistant`
4. View system health: `/health/deep` endpoint

---

## 🎉 Next Steps After Deployment

1. **Connect OAuth Providers**
   - Visit: `https://your-backend-url/api/v1/auth/providers`
   - Authorize each provider (Gmail, Calendar, Tasks, Drive)

2. **Test Daily Digest**
   - Create sample tasks and events
   - Visit: `https://your-backend-url/api/v1/daily-digest`

3. **Setup Monitoring**
   - Configure Cloud Monitoring alerts
   - Enable Cloud Logging

4. **Custom Domain (Optional)**
   - Map custom domain to Cloud Run service
   - Update OAuth redirect URIs accordingly

---

**Built with ❤️ using FastAPI, React, and Google Cloud Platform**

```bash
cd backend
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn api.main:app --reload --port 8000
```

API will be available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/process-email`
- `http://localhost:8000/api/v1/tasks`
- `http://localhost:8000/api/v1/events`
- `http://localhost:8000/api/v1/chat`
- `http://localhost:8000/api/v1/form/autofill-preview`
- `http://localhost:8000/api/v1/auth/google/gmail/url`
- `http://localhost:8000/api/v1/auth/google/calendar/url`
- `http://localhost:8000/api/v1/auth/google/callback`
- `http://localhost:8000/api/v1/google/gmail/messages`
- `http://localhost:8000/api/v1/google/status`
- `http://localhost:8000/api/v1/google/gmail/sync`
- `http://localhost:8000/api/v1/google/calendar/event`
- `http://localhost:8000/api/v1/google/calendar/events`
- `http://localhost:8000/api/v1/google/tasks/lists`
- `http://localhost:8000/api/v1/google/tasks/items`
- `http://localhost:8000/api/v1/google/tasks/sync`
- `http://localhost:8000/api/v1/google/reminders/run`
- `http://localhost:8000/api/v1/google/drive/files`
- `http://localhost:8000/api/v1/google/drive/resources`
- `http://localhost:8000/api/v1/daily-digest`
- `http://localhost:8000/api/v1/setup/checklist`

## Frontend Setup (Local)

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

## API Examples

### Process email

```bash
curl -X POST http://localhost:8000/api/v1/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "mail-001",
    "subject": "Apply for internship at ABC",
    "sender": "you@example.com",
    "body": "Please apply before 2026-04-10 17:00 https://forms.example.com/apply"
  }'
```

### Chat query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my tasks tomorrow?"}'
```

## GCP Cloud Shell / Cloud Run Deployment

### 1. Prepare project

```bash
git clone <your-repo-url>
cd ai-productivity-assistant/backend
cp .env.example .env
gcloud config set project ai-multi-agent-system
```

### 2. Enable APIs

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Also ensure these are enabled in the same project:

- Gmail API
- Google Calendar API
- Google Tasks API
- Google Drive API
- Firestore API

### 2b. Configure Google OAuth

Create OAuth client credentials in Google Cloud and set the redirect URI to:

- `http://localhost:8000/api/v1/auth/google/callback`

Then configure one of these options in `backend/.env`:

- `GOOGLE_OAUTH_CLIENT_CONFIG_PATH`
- or `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

For Cloud Run, update `GOOGLE_OAUTH_REDIRECT_URI` to your deployed callback URL.

### 2c. Choose the storage backend

- Set `STORAGE_BACKEND=mongodb` to use MongoDB.
- Set `STORAGE_BACKEND=firestore` to use Firestore.
- If Firestore is selected, set `FIRESTORE_PROJECT_ID` and optionally `FIRESTORE_CREDENTIALS_PATH` when not using default Cloud credentials.

For this project setup, use Firestore/Firebase with:

- `STORAGE_BACKEND=firestore`
- `FIRESTORE_PROJECT_ID=ai-mulit-agent-system-firebase`

### 3. Build and deploy FastAPI backend

```bash
gcloud run deploy ai-productivity-assistant-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated
```

### 4. ADK + A2A deployment option

```bash
pip install google-adk a2a-sdk google-genai
adk deploy cloud_run --a2a
```

### 5. Frontend deployment (Vercel)

Deploy `frontend` folder with build command `npm run build` and output directory `dist`.

## Agent Cards (A2A)

Every agent includes:

- `agent.py` (ADK tool implementation)
- `agent.json` (Agent Card)

Cards are located under `backend/agents/*/agent.json`.

## Notes for Real Integrations

The current codebase includes production-ready architecture and local mock logic for classification/extraction.
To go fully live:

- Replace email parsing stubs with Gmail API message polling/webhooks.
- Replace local event writes with Google Calendar API writes. The current code already creates Google Calendar events when OAuth credentials are connected.
- Replace notification persistence with SMTP/Gmail API send.
- OAuth wiring is implemented; add Secret Manager or encrypted storage for production token hardening.
- Add Firestore option if required by the evaluator.
