#!/bin/bash

# Script untuk testing IoT Peternakan

echo "======================================"
echo "IoT Peternakan - Testing Script"
echo "======================================"
echo ""

SERVER_URL="http://localhost:5000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Test Health Check${NC}"
curl -s "$SERVER_URL/api/health" | jq .
echo ""

echo -e "${BLUE}2. Get Available Actions${NC}"
curl -s "$SERVER_URL/api/device/actions" | jq .
echo ""

echo -e "${BLUE}3. Get Latest Sensor Data${NC}"
curl -s "$SERVER_URL/api/sensor/latest" | jq .
echo ""

echo -e "${BLUE}4. Get Sensor History (limit 5)${NC}"
curl -s "$SERVER_URL/api/sensor/history?limit=5" | jq .
echo ""

echo -e "${BLUE}5. Get Notifications${NC}"
curl -s "$SERVER_URL/api/notifications?limit=5" | jq .
echo ""

echo -e "${GREEN}Testing Complete!${NC}"
