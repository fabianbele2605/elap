#!/bin/bash
# Integration Test: REST API Endpoints

BASE_URL="http://localhost:3000"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🧪 Testing REST API Endpoints"

# Get JWT token
echo "📝 Getting JWT token..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\"}")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get JWT token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Got JWT: ${TOKEN:0:20}..."

# Test 1: Create Agent
echo ""
echo "🔹 Test 1: Create Agent"
AGENT_RESPONSE=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"TestAgent","role":"Tester","description":"Integration test agent"}')

AGENT_ID=$(echo "$AGENT_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$AGENT_ID" ]; then
    echo "❌ Failed to create agent"
    echo "Response: $AGENT_RESPONSE"
    exit 1
fi

echo "✅ Agent created: $AGENT_ID"

# Test 2: List Agents
echo ""
echo "🔹 Test 2: List Agents"
AGENTS_LIST=$(curl -s -X GET "$BASE_URL/agents" \
  -H "Authorization: Bearer $TOKEN")

if echo "$AGENTS_LIST" | grep -q "$AGENT_ID"; then
    echo "✅ Agent found in list"
else
    echo "❌ Agent not found in list"
    exit 1
fi

# Test 3: Get Agent Info
echo ""
echo "🔹 Test 3: Get Agent Info"
AGENT_INFO=$(curl -s -X GET "$BASE_URL/agents/$AGENT_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$AGENT_INFO" | grep -q "TestAgent"; then
    echo "✅ Agent info retrieved"
else
    echo "❌ Failed to get agent info"
    exit 1
fi

# Test 4: Get Agent Status
echo ""
echo "🔹 Test 4: Get Agent Status"
STATUS=$(curl -s -X GET "$BASE_URL/agents/$AGENT_ID/status" \
  -H "Authorization: Bearer $TOKEN")

if echo "$STATUS" | grep -q "idle\|running"; then
    echo "✅ Agent status retrieved"
else
    echo "❌ Failed to get agent status"
    exit 1
fi

# Test 5: Delete Agent
echo ""
echo "🔹 Test 5: Delete Agent"
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/agents/$AGENT_ID" \
  -H "Authorization: Bearer $TOKEN")

if [ "$(echo $?)" -eq 0 ]; then
    echo "✅ Agent deleted successfully"
else
    echo "❌ Failed to delete agent"
    exit 1
fi

echo ""
echo "✅ All REST API tests passed!"
