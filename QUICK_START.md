# Quick Start Guide

Get the AI Productivity Assistant running in minutes!

## 🚀 30-Minute Setup (Local Development)

### 1. Clone & Install (5 min)

**Linux/Mac:**
```bash
git clone <your-repo>
cd ai-productivity-assistant
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

**Windows:**
```cmd
git clone <your-repo>
cd ai-productivity-assistant
setup.bat
```

### 2. Configure (5 min)

Edit `backend/.env`:
```
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-secret
NOTIFICATION_SENDER_EMAIL=your-email@gmail.com
SMTP_USER=your-email
SMTP_PASSWORD=your-app-password
```

### 3. Run (20 min)

Choose one:

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual (requires MongoDB on 27017)**
- Terminal 1: `cd backend && source venv/bin/activate && uvicorn api.main:app --reload`
- Terminal 2: `cd frontend && npm run dev`

### 4. Access

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## ☁️ Production Deployment (GCP Cloud Run)

### 1. Prepare (5 min)

```bash
# Set your configuration
export GOOGLE_PROJECT_ID="your-project-id"
export FIRESTORE_PROJECT_ID="your-firebase-project"
export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-secret"
export NOTIFICATION_SENDER_EMAIL="your-email@gmail.com"
export SMTP_USER="your-email"
export SMTP_PASSWORD="your-app-password"
```

### 2. Deploy (15 min)

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### 3. Verify

The script will automatically:
- Build Docker images
- Push to Google Container Registry
- Deploy to Cloud Run
- Setup secrets in Secret Manager
- Configure OAuth
- Run validation tests

**Output will include:**
- Backend URL: `https://ai-productivity-assistant-XXXX.run.app`
- Frontend URL: `https://ai-productivity-assistant-frontend-XXXX.run.app`

### 4. Post-Deploy (5 min)

1. Update Google OAuth redirect URI:
   ```
   https://your-backend-url/api/v1/auth/google/callback
   ```

2. Authorize OAuth providers:
   ```
   https://your-backend-url/api/v1/auth/providers
   ```

3. Verify deployment:
   ```bash
   ./scripts/validate-deployment.sh https://your-backend-url
   ```

---

## 📁 Essential Files to Edit

| File | Purpose |
|------|---------|
| `backend/.env` | Backend configuration & credentials |
| `frontend/.env` | Frontend API endpoint |
| `backend/Dockerfile` | Backend container (production) |
| `frontend/Dockerfile` | Frontend container (production) |

---

## 🔑 Required Google Credentials

### OAuth Application

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 Application
3. Add redirect URI: `http://localhost:8000/api/v1/auth/google/callback` (local) or production URL
4. Copy **Client ID** and **Client Secret**

### Gmail App Password

1. Enable 2-Factor Authentication on your Google account
2. Generate "App password" at [myaccount.google.com](https://myaccount.google.com/apppasswords)
3. Use as SMTP_PASSWORD

---

## ✅ Validation Checklist

- [ ] Backend responds to `curl http://localhost:8000/`
- [ ] Frontend loads at `http://localhost:5173`
- [ ] API docs available at `http://localhost:8000/docs`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] OAuth credentials configured in `.env`
- [ ] SMTP credentials working
- [ ] All Google APIs enabled in GCP Console

---

## 🆘 Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

### Docker Connection Failed
```bash
# Start Docker Desktop first, then retry
docker-compose up -d
```

### OAuth Not Working
- Check `.env` has correct CLIENT_ID and CLIENT_SECRET
- Verify redirect URI matches in Google Console
- Ensure domain is reachable

### Database Connection Error
- For local: Ensure MongoDB is running on `localhost:27017`
- For Cloud Run: Check Firestore project ID is correct

---

## 📞 Getting Help

1. **Health Endpoints**: `curl http://localhost:8000/health/deep`
2. **Setup Checklist**: `curl http://localhost:8000/api/v1/setup/checklist`
3. **Logs**: `gcloud run logs read ai-productivity-assistant`
4. **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎯 What's Next

After successful deployment:

1. **Connect Google Services**
   - Visit OAuth providers endpoint
   - Authorize Gmail, Calendar, Tasks, Drive

2. **Test Functionality**
   - Create sample tasks/events
   - Check daily digest
   - Send test email notifications

3. **Customize Dashboard**
   - Modify panels in `frontend/src/pages/DashboardPage.jsx`
   - Add custom agents in `backend/agents/`

4. **Monitor & Scale**
   - Check Cloud Run metrics
   - Enable auto-scaling
   - Set up monitoring alerts

---

**It's that simple! You're now running a production-ready multi-agent AI system! 🎉**
