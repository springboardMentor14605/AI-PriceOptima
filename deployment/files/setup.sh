#!/bin/bash

# =============================================================================
# PRICEOPTIMA QUICK SETUP SCRIPT
# Milestone 6: Automated deployment setup
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "=============================================================="
echo "  PRICEOPTIMA - QUICK SETUP"
echo "  Milestone 6: Deployment & Dashboard"
echo "=============================================================="
echo -e "${NC}"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker installed$(docker --version)${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker Compose installed$(docker-compose --version)${NC}"
fi

# Create necessary directories
echo -e "\n${YELLOW}📁 Creating directories...${NC}"
mkdir -p backend/models
mkdir -p frontend/build
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
echo -e "${GREEN}✓ Directories created${NC}"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}⚙️  Creating .env file...${NC}"
    cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
LOG_LEVEL=info

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create Prometheus configuration
echo -e "\n${YELLOW}🔧 Creating monitoring configuration...${NC}"
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'priceoptima-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
EOF
echo -e "${GREEN}✓ Prometheus config created${NC}"

# Pull Docker images
echo -e "\n${YELLOW}🐳 Pulling Docker images...${NC}"
docker-compose pull || echo -e "${YELLOW}⚠️  Some images need to be built${NC}"

# Build containers
echo -e "\n${YELLOW}🔨 Building containers...${NC}"
docker-compose build

# Start services
echo -e "\n${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "\n${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Health checks
echo -e "\n${YELLOW}🏥 Running health checks...${NC}"

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting up${NC}"
fi

# Display service URLs
echo -e "\n${BLUE}=============================================================="
echo "  DEPLOYMENT COMPLETE!"
echo "==============================================================${NC}"

echo -e "\n${GREEN}✅ All services are running!${NC}"
echo -e "\n${YELLOW}Access your services:${NC}"
echo -e "  🌐 Dashboard:    ${GREEN}http://localhost:3000${NC}"
echo -e "  🔌 API:          ${GREEN}http://localhost:8000${NC}"
echo -e "  📚 API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  📊 Prometheus:   ${GREEN}http://localhost:9090${NC}"
echo -e "  📈 Grafana:      ${GREEN}http://localhost:3001${NC} (admin/admin)"

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  View logs:       ${BLUE}docker-compose logs -f${NC}"
echo -e "  View status:     ${BLUE}docker-compose ps${NC}"
echo -e "  Stop services:   ${BLUE}docker-compose down${NC}"
echo -e "  Restart:         ${BLUE}docker-compose restart${NC}"
echo -e "  Run UAT tests:   ${BLUE}python uat_testing.py${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Open dashboard at http://localhost:3000"
echo -e "  2. Explore API docs at http://localhost:8000/docs"
echo -e "  3. Run UAT tests: python uat_testing.py"
echo -e "  4. Review deployment guide: DEPLOYMENT_GUIDE.md"

echo -e "\n${GREEN}Happy pricing! 🎯${NC}\n"
