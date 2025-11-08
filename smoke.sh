#!/usr/bin/env bash
BASE="http://localhost:8000"

echo "== Health =="
curl -s $BASE/health

echo -e "\n== Analyze =="
curl -s -X POST "$BASE/api/v1/moderation/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"smoke","conversation_id":"test","message":"You are a horrible person"}'

echo -e "\n== Done =="

