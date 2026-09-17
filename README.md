# OpenAI-Compatible API Migration Kit

**OpenAI-compatible API migration kit** — runnable Python, JavaScript and cURL examples for moving an OpenAI-compatible workload between API gateways without hard-coding credentials, and without pretending that changing one URL proves full compatibility.

Use this repository when evaluating an **OpenAI API proxy**, **AI API gateway**, **LLM API relay**, or **OpenAI-compatible API**.

## What this kit checks

| Migration surface | Included example | What still needs a real test |
|---|---|---|
| Chat Completions | Python, JavaScript, cURL | model availability, usage fields, errors |
| Streaming / SSE | Python | event order, disconnects, cancellation |
| Tool calling | Python | argument schema, duplicate execution, finish reason |
| JSON / structured output | checklist + scanner | schema adherence and refusal behavior |
| Vision input | checklist + scanner | media limits, URL/data URI handling and cost |
| Responses API | checklist + scanner | endpoint and event compatibility |
| Authentication | environment variables only | key scopes, revocation and sub-key controls |
| Rollback | configuration-only switch | in-flight requests, retries and idempotency |

## Quick start with APIMART

APIMART documents an OpenAI-compatible base URL at `https://api.apimart.ai/v1`. Keep the provider settings in environment variables so rollback does not require a code change.

```bash
cp .env.example .env
# Add a newly created key to .env; never commit it.
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="https://api.apimart.ai/v1"
export OPENAI_MODEL="gpt-5-mini"
```

Python:

```bash
python -m pip install openai
python examples/python_chat.py
```

JavaScript:

```bash
npm install
node examples/javascript_chat.mjs
```

cURL:

```bash
./examples/curl_chat.sh
```

Official APIMART references: [Quick start](https://docs.apimart.ai/en/quickstart) · [documentation index](https://docs.apimart.ai/llms.txt).

## Scan an existing project before switching

```bash
python openai_migration_check.py /path/to/your/project
```

The scanner reports migration-sensitive code paths—streaming, tools/functions, structured output, vision, Responses API, custom base URLs, and possible hard-coded keys. It never uploads source code.

Exit codes:

- `0`: scan completed and no possible hard-coded key was found;
- `2`: scan completed and a possible hard-coded key requires review;
- `64`: invalid command input.

## Migration sequence

1. Freeze a representative request set and acceptance rules.
2. Move base URL, key, and model ID to configuration.
3. Run chat, streaming, tools, JSON, vision, and Responses checks that your application actually uses.
4. Compare successful **usable outputs**, p50/p95 latency, retries, 429 behavior, and total cost per usable output.
5. Canary 1% → 5% → 25%; preserve idempotency keys and an independent rollback route.
6. Roll back by restoring the previous environment values—not by editing application code.

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for the complete contract and [`ROLLBACK.md`](ROLLBACK.md) for the rollback drill.

## Attributed links (how this repository is measured)

| Purpose | Attributed link | Target |
| --- | --- | --- |
| Browse the model catalog | <https://go.apimart.ai/k-756372> | `apimart.ai` |
| Current pricing page | <https://go.apimart.ai/k-44948b> | `apimart.ai/pricing` |
| Get an API key | <https://go.apimart.ai/k-f16051> | `apimart.ai/keys` |

If a single account for multiple text, image and video models fits your evaluation, [create an APIMART account with this
attributed link](https://go.apimart.ai/k-f16051) and run the same fixed test set against APIMART and your current route.

APIMART is one candidate, not an unconditional winner. Model identity, limits, failure billing, retention, regions,
fallback behaviour and SLA must be verified for your account and workload.

Outbound APIMart links are minted through the promo link API (`go.apimart.ai`); hand-made tracking parameters are
rejected by `tools/check_links.py` in CI.

## Disclosure

This repository documents an OpenAI-compatible migration procedure; it is published to document that procedure, not to
claim official status for any vendor. Product names, model names and documentation belong to their respective owners,
and relayed routes are third-party relay endpoints rather than first-party vendor endpoints.

## Repository map

```text
README.md                  migration checklist, quickstart and attributed links
COMPATIBILITY.md           the compatibility contract per migration surface
ROLLBACK.md                rollback drill
openai_migration_check.py  scanner for migration-sensitive code paths
examples/                  Python, JavaScript and cURL clients (chat, streaming, tools)
tests/                     unit tests for the scanner
tools/check_links.py       attribution guard (CI)
.github/workflows/         verify + validate
```

## License

MIT — see [LICENSE](LICENSE).
