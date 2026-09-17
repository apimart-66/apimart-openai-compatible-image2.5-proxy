# Rollback drill

Keep both routes configurable:

```bash
export OPENAI_BASE_URL="https://previous-provider.example/v1"
export OPENAI_API_KEY="..."
export OPENAI_MODEL="previous-model-id"
```

Before returning traffic, verify:

1. new requests use the previous route;
2. pending retries from the candidate route are cancelled or deduplicated;
3. tool calls and asynchronous jobs cannot execute twice;
4. monitoring and billing attribution identify the restored route;
5. the fixed smoke-test set passes.

Never store live keys in this repository or in command history.
