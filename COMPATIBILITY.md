# OpenAI-compatible migration contract

“OpenAI-compatible” is an entry-point claim, not proof that two routes behave the same. Record the following for every candidate and mark undocumented fields `unknown`.

## Request and response

- exact endpoint, model ID and model version;
- accepted message content parts and parameter defaults;
- streaming event order, `[DONE]`, disconnect and cancellation behavior;
- tool schema, tool call IDs, finish reasons and duplicate-execution protection;
- JSON schema adherence, refusal and truncated-output behavior;
- image URL, data URI, file, size and media limits;
- Responses API input/output items and event compatibility;
- usage fields, cached-token fields and error body shape.

## Operations

- RPM, TPM, concurrent requests, queueing and `Retry-After`;
- timeout, retry, fallback and circuit-breaker policy;
- idempotency behavior for generation and tool side effects;
- request/response retention, opt-out, regions and subprocessors;
- sub-keys, budgets, alerts, audit logs and revocation;
- billing for input, output, cache, media, retries and failed requests.

## Pass criteria

Define these before testing:

1. usable-output rate, separate from HTTP completion rate;
2. time-to-usable-output p50 and p95;
3. cost per usable output, including retries;
4. maximum accepted 429, timeout and fallback rates;
5. maximum rollback time and zero duplicate side effects.
