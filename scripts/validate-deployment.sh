#!/bin/bash

################################################################
# AI Productivity Assistant - Post-Deployment Validation
# Validates successful deployment and configuration
################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./validate-deployment.sh <backend-url>"
    echo "Example: ./validate-deployment.sh https://ai-productivity-assistant-xyz.run.app"
    exit 1
fi

BACKEND_URL=$1
FRONTEND_URL=${2:-"https://ai-productivity-assistant-frontend-xyz.run.app"}
FAILED_CHECKS=0

print_header "Validating Deployment"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Basic connectivity
print_header "Test 1: Basic Connectivity"
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/" | grep -q "200"; then
    print_success "Backend is responding"
else
    print_error "Backend is not responding"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Test 2: Health check
print_header "Test 2: Health Check"
HEALTH=$(curl -s "$BACKEND_URL/health")
if echo "$HEALTH" | grep -q '"status"'; then
    STATUS=$(echo "$HEALTH" | grep -o '"status":"[^"]*"' | head -1)
    print_success "Health check endpoint accessible: $STATUS"
else
    print_error "Health check failed"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Test 3: API Documentation
print_header "Test 3: API Documentation"
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" | grep -q "200"; then
    print_success "API documentation available at /docs"
else
    print_warning "API documentation not accessible"
fi

# Test 4: Deep Health Check
print_header "Test 4: System Requirements"
DEEP_HEALTH=$(curl -s "$BACKEND_URL/health/deep")

# Check database
if echo "$DEEP_HEALTH" | grep -q '"database"'; then
    DB_STATUS=$(echo "$DEEP_HEALTH" | grep -o '"database":{"status":"[^"]*"' | cut -d'"' -f6)
    if [ "$DB_STATUS" = "healthy" ] || [ "$DB_STATUS" = "configured" ]; then
        print_success "Database: $DB_STATUS"
    else
        print_warning "Database: $DB_STATUS"
    fi
fi

# Check OAuth
if echo "$DEEP_HEALTH" | grep -q '"oauth"'; then
    OAUTH_STATUS=$(echo "$DEEP_HEALTH" | grep -o '"oauth":{"status":"[^"]*"' | cut -d'"' -f6)
    if [ "$OAUTH_STATUS" = "configured" ]; then
        print_success "OAuth: $OAUTH_STATUS"
    else
        print_warning "OAuth: $OAUTH_STATUS (needs configuration)"
    fi
fi

# Check SMTP
if echo "$DEEP_HEALTH" | grep -q '"smtp"'; then
    SMTP_STATUS=$(echo "$DEEP_HEALTH" | grep -o '"smtp":{"status":"[^"]*"' | cut -d'"' -f6)
    if [ "$SMTP_STATUS" = "configured" ]; then
        print_success "SMTP: $SMTP_STATUS"
    else
        print_warning "SMTP: $SMTP_STATUS (needs configuration)"
    fi
fi

# Test 5: Setup Checklist
print_header "Test 5: Setup Checklist"
CHECKLIST=$(curl -s "$BACKEND_URL/api/v1/setup/checklist")

# Check OAuth client configured
if echo "$CHECKLIST" | grep -q '"oauth_client_configured":true'; then
    print_success "OAuth client configured"
else
    print_warning "OAuth client not fully configured"
fi

# Check storage backend
if echo "$CHECKLIST" | grep -q '"storage_backend":"firestore"'; then
    print_success "Storage backend: Firestore (Production)"
elif echo "$CHECKLIST" | grep -q '"storage_backend":"mongodb"'; then
    print_warning "Storage backend: MongoDB (Development)"
else
    print_error "Storage backend not properly configured"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# Check Firestore
if echo "$CHECKLIST" | grep -q '"firestore_ready":true'; then
    print_success "Firestore is ready"
else
    print_warning "Firestore may not be ready"
fi

# Check SMTP
if echo "$CHECKLIST" | grep -q '"smtp_ready":true'; then
    print_success "SMTP is ready"
else
    print_warning "SMTP may not be ready"
fi

# Test 6: Version Info
print_header "Test 6: Version Information"
VERSION=$(curl -s "$BACKEND_URL/version")
if echo "$VERSION" | grep -q '"version"'; then
    APP_VERSION=$(echo "$VERSION" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    ENV=$(echo "$VERSION" | grep -o '"environment":"[^"]*"' | cut -d'"' -f4)
    print_success "Application version: $APP_VERSION"
    print_success "Environment: $ENV"
else
    print_warning "Could not retrieve version information"
fi

# Test 7: API Endpoints
print_header "Test 7: Testing Key Endpoints"

# Test auth endpoints
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/auth/providers" | grep -q "200"; then
    print_success "Auth providers endpoint accessible"
else
    print_warning "Auth providers endpoint not responding"
fi

# Test Google routes
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/google/auth-status" | grep -q "200"; then
    print_success "Google auth status endpoint accessible"
else
    print_warning "Google auth status endpoint not responding"
fi

# Test daily digest
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/daily-digest" | grep -q "200\|401\|404"; then
    print_success "Daily digest endpoint accessible"
else
    print_warning "Daily digest endpoint not responding"
fi

# Test 8: Frontend Accessibility
print_header "Test 8: Frontend Accessibility"
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/" | grep -q "200"; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend not responding (may still be deploying)"
fi

# Test 9: CORS Configuration
print_header "Test 9: CORS Configuration"
CORS_RESPONSE=$(curl -s -i -X OPTIONS "$BACKEND_URL/api/v1/daily-digest" | grep -i "access-control-allow-origin" || echo "")
if [ ! -z "$CORS_RESPONSE" ]; then
    print_success "CORS is properly configured"
else
    print_warning "CORS headers not found (may be okay depending on setup)"
fi

# Test 10: Performance Check
print_header "Test 10: Performance Baseline"
RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$BACKEND_URL/")
print_success "Root endpoint response time: ${RESPONSE_TIME}s"

# Test 11: Metrics Endpoint
print_header "Test 11: Application Metrics"
METRICS=$(curl -s "$BACKEND_URL/metrics")
if echo "$METRICS" | grep -q '"total_users"'; then
    USER_COUNT=$(echo "$METRICS" | grep -o '"total_users":[0-9]*' | cut -d':' -f2)
    print_success "Metrics accessible - Total users: $USER_COUNT"
else
    print_warning "Metrics endpoint not responding"
fi

# Test 12: Provider Status
print_header "Test 12: OAuth Provider Status"
PROVIDERS=$(curl -s "$BACKEND_URL/api/v1/setup/checklist" | grep -o '"providers":{[^}]*}' | head -1)
if [ ! -z "$PROVIDERS" ]; then
    echo "OAuth Providers Status:"
    echo "$PROVIDERS" | sed 's/},{/}\n{/g'
else
    print_warning "Could not retrieve provider status"
fi

# Final Summary
print_header "Validation Summary"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════╗"
    echo "║  ✓ DEPLOYMENT VALIDATION PASSED   ║"
    echo "╚════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Your AI Productivity Assistant is successfully deployed!"
    echo ""
    echo "Next Steps:"
    echo "1. Visit the frontend: $FRONTEND_URL"
    echo "2. Authorize OAuth providers: $BACKEND_URL/api/v1/auth/providers"
    echo "3. Check setup status: $BACKEND_URL/api/v1/setup/checklist"
    echo "4. View API docs: $BACKEND_URL/docs"
    echo ""
else
    echo -e "${YELLOW}"
    echo "╔════════════════════════════════════╗"
    echo "║  ⚠ SOME CHECKS FAILED            ║"
    echo "╚════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Failed checks: $FAILED_CHECKS"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check backend logs: gcloud run logs read ai-productivity-assistant"
    echo "2. Check deep health: curl $BACKEND_URL/health/deep"
    echo "3. Review DEPLOYMENT.md for troubleshooting guide"
    echo ""
fi

# Generate detailed report
echo -e "${BLUE}Generating detailed validation report...${NC}"
cat > deployment-validation-report.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backend_url": "$BACKEND_URL",
  "frontend_url": "$FRONTEND_URL",
  "failed_checks": $FAILED_CHECKS,
  "validation_status": $([ $FAILED_CHECKS -eq 0 ] && echo '"PASSED"' || echo '"WARNING"'),
  "full_report": {
    "health": $HEALTH,
    "deep_health": $DEEP_HEALTH,
    "version": $VERSION,
    "checklist": $CHECKLIST,
    "metrics": $METRICS
  }
}
EOF

print_success "Detailed report saved to deployment-validation-report.json"
echo ""

exit $FAILED_CHECKS
