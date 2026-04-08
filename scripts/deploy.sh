#!/bin/bash

################################################################
# AI Productivity Assistant - Complete Production Deployment
# This script handles end-to-end deployment to GCP Cloud Run
################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="ai-productivity-assistant"
REGION="asia-south1"
MEMORY="512Mi"
TIMEOUT="300"

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if required tools are installed
check_tools() {
    print_header "Checking Required Tools"
    
    local missing_tools=()
    
    for tool in gcloud docker; do
        if ! command -v $tool &> /dev/null; then
            missing_tools+=($tool)
        else
            version=$($tool --version | head -n1)
            print_success "$tool: $version"
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing tools: ${missing_tools[@]}"
        echo "Please install missing tools and try again."
        exit 1
    fi
}

# Validate environment variables
validate_env() {
    print_header "Validating Required Environment Variables"
    
    local required_vars=(
        "GOOGLE_PROJECT_ID"
        "GOOGLE_OAUTH_CLIENT_ID"
        "GOOGLE_OAUTH_CLIENT_SECRET"
        "FIRESTORE_PROJECT_ID"
        "NOTIFICATION_SENDER_EMAIL"
        "SMTP_USER"
        "SMTP_PASSWORD"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=($var)
        else
            print_success "$var is set"
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing environment variables: ${missing_vars[@]}"
        echo "Please set these variables before proceeding."
        exit 1
    fi
}

# Setup GCP
setup_gcp() {
    print_header "Setting Up GCP Project"
    
    # Set the project
    gcloud config set project $GOOGLE_PROJECT_ID
    print_success "Set GCP project to $GOOGLE_PROJECT_ID"
    
    # Enable required APIs
    echo "Enabling required APIs..."
    apis=(
        "run.googleapis.com"
        "firestore.googleapis.com"
        "cloudbuild.googleapis.com"
        "artifactregistry.googleapis.com"
        "cloudresourcemanager.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        gcloud services enable $api --quiet 2>/dev/null && print_success "Enabled $api" || print_warning "Could not enable $api (may already be enabled)"
    done
}

# Create Secret Manager secrets
setup_secrets() {
    print_header "Setting Up Secret Manager"
    
    # Create GOOGLE_OAUTH_CLIENT_SECRET
    if gcloud secrets describe GOOGLE_OAUTH_CLIENT_SECRET &>/dev/null; then
        print_warning "Secret GOOGLE_OAUTH_CLIENT_SECRET already exists, creating new version"
        echo -n "$GOOGLE_OAUTH_CLIENT_SECRET" | gcloud secrets versions add GOOGLE_OAUTH_CLIENT_SECRET --data-file=- --quiet
    else
        echo -n "$GOOGLE_OAUTH_CLIENT_SECRET" | gcloud secrets create GOOGLE_OAUTH_CLIENT_SECRET --data-file=- --replication-policy="automatic" --quiet
        print_success "Created secret GOOGLE_OAUTH_CLIENT_SECRET"
    fi
    
    # Create SMTP_PASSWORD
    if gcloud secrets describe SMTP_PASSWORD &>/dev/null; then
        print_warning "Secret SMTP_PASSWORD already exists, creating new version"
        echo -n "$SMTP_PASSWORD" | gcloud secrets versions add SMTP_PASSWORD --data-file=- --quiet
    else
        echo -n "$SMTP_PASSWORD" | gcloud secrets create SMTP_PASSWORD --data-file=- --replication-policy="automatic" --quiet
        print_success "Created secret SMTP_PASSWORD"
    fi
}

# Build and push Docker image
build_image() {
    print_header "Building and Pushing Docker Image"
    
    # Get the current timestamp for image tagging
    IMAGE_TAG=$(date +%s)
    IMAGE_NAME="gcr.io/$GOOGLE_PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG"
    IMAGE_LATEST="gcr.io/$GOOGLE_PROJECT_ID/$SERVICE_NAME:latest"
    
    echo "Building image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME -t $IMAGE_LATEST ./backend
    
    # Push to Google Container Registry
    echo "Pushing image to Container Registry..."
    docker push $IMAGE_NAME
    docker push $IMAGE_LATEST
    
    print_success "Image pushed successfully"
    echo $IMAGE_NAME
}

# Deploy to Cloud Run
deploy_cloud_run() {
    print_header "Deploying to Cloud Run"
    
    local IMAGE_NAME=$1
    
    # Get current Cloud Run URL if service exists
    CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    
    if [ -z "$CLOUD_RUN_URL" ]; then
        CLOUD_RUN_URL="https://$SERVICE_NAME-REGION.run.app"
    fi
    
    OAUTH_REDIRECT_URI="$CLOUD_RUN_URL/api/v1/auth/google/callback"
    
    echo "Deploying to Cloud Run..."
    echo "Service Name: $SERVICE_NAME"
    echo "Region: $REGION"
    echo "OAuth Redirect URI: $OAUTH_REDIRECT_URI"
    
    gcloud run deploy $SERVICE_NAME \
        --image=$IMAGE_NAME \
        --platform managed \
        --region=$REGION \
        --memory=$MEMORY \
        --timeout=$TIMEOUT \
        --allow-unauthenticated \
        --set-env-vars="\
APP_NAME=AI Productivity Assistant,\
API_PREFIX=/api/v1,\
STORAGE_BACKEND=firestore,\
FIRESTORE_PROJECT_ID=$FIRESTORE_PROJECT_ID,\
FIRESTORE_DATABASE_ID=(default),\
GOOGLE_PROJECT_ID=$GOOGLE_PROJECT_ID,\
GOOGLE_LOCATION=$REGION,\
GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID,\
GOOGLE_OAUTH_REDIRECT_URI=$OAUTH_REDIRECT_URI,\
NOTIFICATION_SENDER_EMAIL=$NOTIFICATION_SENDER_EMAIL,\
SMTP_HOST=smtp.gmail.com,\
SMTP_PORT=587,\
SMTP_USER=$SMTP_USER" \
        --set-secrets="\
GOOGLE_OAUTH_CLIENT_SECRET=GOOGLE_OAUTH_CLIENT_SECRET:latest,\
SMTP_PASSWORD=SMTP_PASSWORD:latest" \
        --quiet
    
    print_success "Cloud Run deployment successful"
    
    # Get the actual service URL
    CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
    print_success "Service URL: $CLOUD_RUN_URL"
    
    echo $CLOUD_RUN_URL
}

# Setup Firestore (if needed)
setup_firestore() {
    if [ "$FIRESTORE_PROJECT_ID" != "$GOOGLE_PROJECT_ID" ]; then
        print_header "Setting Up Firestore Cross-Project Access"
        
        # Get Cloud Run service account
        SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Cloud Run" --format='value(email)' | head -n1)
        
        if [ -z "$SERVICE_ACCOUNT" ]; then
            SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || echo "")
        fi
        
        if [ ! -z "$SERVICE_ACCOUNT" ]; then
            echo "Granting Firestore access to $SERVICE_ACCOUNT..."
            gcloud projects add-iam-policy-binding $FIRESTORE_PROJECT_ID \
                --member="serviceAccount:$SERVICE_ACCOUNT" \
                --role="roles/datastore.user" \
                --quiet 2>/dev/null || print_warning "Could not grant Firestore permissions (check if service account email is correct)"
        fi
    fi
}

# Run validation checks
validate_deployment() {
    print_header "Validating Deployment"
    
    local CLOUD_RUN_URL=$1
    
    # Check if service is running
    echo "Checking service health..."
    sleep 5
    
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$CLOUD_RUN_URL/")
    if [ "$HEALTH_CHECK" = "200" ]; then
        print_success "Service is healthy (HTTP $HEALTH_CHECK)"
    else
        print_warning "Service health check returned HTTP $HEALTH_CHECK"
    fi
    
    # Check setup endpoint
    echo "Checking setup checklist..."
    SETUP_CHECK=$(curl -s "$CLOUD_RUN_URL/api/v1/setup/checklist" | head -c 200)
    if [ ! -z "$SETUP_CHECK" ]; then
        print_success "Setup endpoint is responding"
        echo "Setup response (partial): $SETUP_CHECK..."
    else
        print_warning "Setup endpoint not responding"
    fi
}

# Deploy frontend
deploy_frontend() {
    print_header "Deploying Frontend to Cloud Run"
    
    local BACKEND_URL=$1
    
    # Build frontend Docker image
    echo "Building frontend image..."
    FRONTEND_IMAGE_NAME="gcr.io/$GOOGLE_PROJECT_ID/$SERVICE_NAME-frontend:latest"
    
    docker build -t $FRONTEND_IMAGE_NAME ./frontend
    docker push $FRONTEND_IMAGE_NAME
    
    print_success "Frontend image pushed"
    
    # Deploy frontend
    echo "Deploying frontend to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME-frontend" \
        --image=$FRONTEND_IMAGE_NAME \
        --platform managed \
        --region=$REGION \
        --memory=256Mi \
        --allow-unauthenticated \
        --set-env-vars="VITE_API_BASE=$BACKEND_URL" \
        --quiet
    
    FRONTEND_URL=$(gcloud run services describe "$SERVICE_NAME-frontend" --region=$REGION --format='value(status.url)')
    print_success "Frontend deployed at: $FRONTEND_URL"
    
    echo $FRONTEND_URL
}

# Print deployment summary
print_summary() {
    local BACKEND_URL=$1
    local FRONTEND_URL=$2
    
    print_header "Deployment Complete!"
    
    echo -e "${GREEN}Backend URL:${NC} $BACKEND_URL"
    echo -e "${GREEN}Frontend URL:${NC} $FRONTEND_URL"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update Google OAuth redirect URI in Google Cloud Console:"
    echo "   $BACKEND_URL/api/v1/auth/google/callback"
    echo ""
    echo "2. Connect Google providers by visiting:"
    echo "   $BACKEND_URL/api/v1/auth/providers"
    echo ""
    echo "3. Check deployment status:"
    echo "   $BACKEND_URL/api/v1/setup/checklist"
    echo ""
    echo "4. View frontend:"
    echo "   $FRONTEND_URL"
}

# Main execution
main() {
    print_header "AI Productivity Assistant - Complete Deployment"
    
    # Load environment if .env exists
    if [ -f .env ]; then
        export $(cat .env | grep -v '#' | xargs)
        print_success "Loaded environment from .env"
    fi
    
    check_tools
    validate_env
    setup_gcp
    setup_secrets
    
    IMAGE_NAME=$(build_image)
    BACKEND_URL=$(deploy_cloud_run "$IMAGE_NAME")
    
    setup_firestore
    validate_deployment "$BACKEND_URL"
    
    # Optional: Deploy frontend
    read -p "Deploy frontend to Cloud Run? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        FRONTEND_URL=$(deploy_frontend "$BACKEND_URL")
        print_summary "$BACKEND_URL" "$FRONTEND_URL"
    else
        print_summary "$BACKEND_URL" "Skipped"
    fi
}

# Run main function
main "$@"
