#!/bin/bash
# Integration Test: Docker Compose Stack

set -e

echo "🔧 Starting Docker Compose Stack for Integration Tests..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose exists
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

# Start services
echo -e "${YELLOW}📦 Building and starting services...${NC}"
cd deployment || exit 1
docker-compose up -d --build

echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check if core is running
echo -e "${YELLOW}🔍 Testing Core API...${NC}"
if curl -s http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}✅ Core API healthy${NC}"
else
    echo -e "${RED}❌ Core API not responding${NC}"
    docker-compose logs core
    exit 1
fi

# Check if Python AI is running
echo -e "${YELLOW}🔍 Testing Python AI Runtime...${NC}"
# Try to connect to gRPC port
if nc -z localhost 50051 2>/dev/null; then
    echo -e "${GREEN}✅ Python AI gRPC listening${NC}"
else
    echo -e "${RED}❌ Python AI gRPC not listening${NC}"
    docker-compose logs ai-runtime
    exit 1
fi

# Check PostgreSQL
echo -e "${YELLOW}🔍 Testing PostgreSQL...${NC}"
if docker exec elap-postgres pg_isready -U elap &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL healthy${NC}"
else
    echo -e "${RED}❌ PostgreSQL not responding${NC}"
    exit 1
fi

# Check Qdrant
echo -e "${YELLOW}🔍 Testing Qdrant...${NC}"
if curl -s http://localhost:6333/health > /dev/null; then
    echo -e "${GREEN}✅ Qdrant healthy${NC}"
else
    echo -e "${RED}❌ Qdrant not responding${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All services healthy!${NC}"

# Run REST API tests
echo -e "${YELLOW}🧪 Running REST API tests...${NC}"
cd .. || exit 1
./tests/integration_rest_api.sh

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
cd deployment || exit 1
docker-compose down

echo -e "${GREEN}✅ Integration tests completed!${NC}"
