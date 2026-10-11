#!/bin/bash
echo "🚀 Starting Production Environment..."

# 1. LM Studio Server
echo "[1/4] Starting LM Studio..."
lms server start --port 1234 &
sleep 3

# 2. Health Check
echo "[2/4] Checking connectivity..."
curl -s http://localhost:1234/v1/models > /dev/null && echo "✓ LM Studio ready" || echo "✗ LM Studio not responding"

# 3. Run
echo "[3/4] Starting pipeline..."
python -m src.main --example --checkpoint

wait
