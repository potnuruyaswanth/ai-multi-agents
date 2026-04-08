#!/bin/bash

################################################################
# AI Productivity Assistant - Local Development Setup
# This script sets up the local development environment
################################################################

set -e

# Color codes
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

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check Python installation
check_python() {
    print_header "Checking Python Installation"
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version)
        print_success "Python is installed: $python_version"
    else
        echo "Python is not installed. Please install Python 3.11 or higher."
        exit 1
    fi
}

# Setup backend virtual environment
setup_backend() {
    print_header "Setting Up Backend Environment"
    
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
    
    cd ..
}

# Setup frontend 
setup_frontend() {
    print_header "Setting Up Frontend Environment"
    
    cd frontend
    
    if command -v npm &> /dev/null; then
        npm install
        print_success "Frontend dependencies installed"
    else
        print_info "Node.js/npm not installed. Install from https://nodejs.org/"
    fi
    
    cd ..
}

# Create .env if not exists
setup_env() {
    print_header "Setting Up Environment Files"
    
    if [ ! -f backend/.env ]; then
        echo "Creating backend/.env..."
        cp backend/.env.example backend/.env
        print_success "Created backend/.env"
        print_info "Please edit backend/.env with your configuration"
    fi
    
    if [ ! -f frontend/.env ]; then
        echo "Creating frontend/.env..."
        echo "VITE_API_BASE=http://localhost:8000" > frontend/.env
        print_success "Created frontend/.env"
    fi
}

# Start services using docker-compose
start_docker() {
    print_header "Starting Services with Docker Compose"
    
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo "Starting services..."
        docker-compose up -d
        print_success "Services started"
        print_info "Backend: http://localhost:8000"
        print_info "Frontend: http://localhost:5173"
        print_info "API Docs: http://localhost:8000/docs"
    else
        print_info "Docker/Docker Compose not installed. Skipping Docker setup."
    fi
}

# Start services locally
start_local() {
    print_header "Starting Local Services"
    
    # Create scripts directory if not exists
    mkdir -p backend/logs
    
    # Start backend in background
    echo "Starting backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    uvicorn api.main:app --reload > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    print_success "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend in background 
    echo "Starting frontend..."
    cd frontend
    npm run dev > ../backend/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    print_success "Frontend started (PID: $FRONTEND_PID)"
    
    print_info "Backend: http://localhost:8000"
    print_info "Frontend: http://localhost:5173"
    print_info "Backend logs: backend/logs/backend.log"
    print_info "Frontend logs: backend/logs/frontend.log"
}

# Main menu
main() {
    print_header "AI Productivity Assistant - Local Setup"
    
    check_python
    setup_backend
    setup_frontend
    setup_env
    
    echo ""
    echo "How would you like to run the services?"
    echo "1) Using Docker Compose (recommended)"
    echo "2) Run locally (requires manual MongoDB)"
    echo "3) Just setup, don't start services"
    read -p "Choose an option (1-3): " choice
    
    case $choice in
        1)
            start_docker
            ;;
        2)
            print_info "Make sure MongoDB is running on localhost:27017"
            start_local
            ;;
        3)
            print_success "Setup complete! Run services manually when ready."
            ;;
        *)
            echo "Invalid option"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Setup complete!"
    echo -e "${BLUE}Documentation: See README.md for more information${NC}"
}

main "$@"
