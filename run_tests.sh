#!/bin/bash
# Script para ejecutar tests de Fase 2

set -e

echo "🧪 FASE 2 — Test Runner"
echo "======================="
echo ""

# Activate venv
source venv/bin/activate

# Run tests by category
echo "📊 Ejecutando tests..."
echo ""

# Agent tests
echo "1️⃣  Testing agents/..."
pytest tests/agents/ -v --tb=short 2>&1 | head -30

echo ""
echo "2️⃣  Testing memory/embeddings..."
pytest tests/memory/test_embeddings.py -v --tb=short -k "not ocr" 2>&1 | head -30

echo ""
echo "3️⃣  Testing memory/vector_db..."
pytest tests/memory/test_vector_db.py -v --tb=short 2>&1 | head -30

echo ""
echo "4️⃣  Testing tools/documents..."
pytest tests/tools/ -v --tb=short 2>&1 | head -40

echo ""
echo "5️⃣  Testing pipelines..."
pytest tests/pipelines/ -v --tb=short 2>&1 | head -30

echo ""
echo "✅ Tests completados"
