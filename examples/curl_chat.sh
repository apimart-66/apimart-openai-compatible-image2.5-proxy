#!/bin/sh
set -eu

: "${OPENAI_API_KEY:?Set OPENAI_API_KEY}"
OPENAI_BASE_URL=${OPENAI_BASE_URL:-https://api.apimart.ai/v1}
OPENAI_MODEL=${OPENAI_MODEL:-gpt-5-mini}

curl --fail-with-body --silent --show-error \
  "$OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data "{\"model\":\"$OPENAI_MODEL\",\"stream\":false,\"messages\":[{\"role\":\"user\",\"content\":\"Reply with exactly: migration-ok\"}]}"
