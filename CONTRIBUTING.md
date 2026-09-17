# Contributing

Useful contributions:

1. A compatibility check for a migration surface this kit does not cover yet (audio, embeddings, batch, moderation).
2. A client example in another language that keeps the same environment-variable contract.
3. A rollback or canary pattern with the failure mode it prevents.

Before opening a pull request:

```bash
python -m unittest discover -s tests -v
python openai_migration_check.py .
python tools/check_links.py
```

Rules: never commit credentials, keep every APIMart link attributed through its `go.apimart.ai` short link, and do not
claim full compatibility for a surface you have not actually exercised.
