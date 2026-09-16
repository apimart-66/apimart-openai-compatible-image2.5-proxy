# OpenAI-Compatible Image API Proxy for image2.5 (GPT-Image-2.5)

Move an existing image pipeline onto an **OpenAI-compatible** endpoint without pretending the shapes are identical: what stays the same, what changes (async task IDs, capped `n`, `version` selection), and the checklist that catches the differences before production traffic does.

**Attributed entry points:** [Open GPT Image 2.5 on APIMart](https://go.apimart.ai/k-0b1178) · [Current pricing](https://go.apimart.ai/k-7d1dda) · [Get an API key](https://go.apimart.ai/k-19dd82)

## Contents

- [Model routes and IDs](#model-routes-and-ids)
- [Observed pricing](#observed-pricing)
- [What the output looks like](#what-the-output-looks-like)
- [Quickstart](#quickstart)
- [Request and response reference](#request-and-response-reference)
- [Migration checklist](#migration-checklist)
- [What a drop-in client looks like](#what-a-drop-in-client-looks-like)
- [FAQ](#faq)
- [Attributed links](#attributed-links-how-this-repository-is-measured)
- [Repository map](#repository-map)

## Compatibility is a spectrum, not a checkbox

Changing a base URL is a five-minute edit. Proving that a workload still behaves is the actual task. For image endpoints
the differences cluster in four places:

1. **Completion style.** A direct OpenAI-style images call returns images inline; the relayed image2.5 route returns a
   `task_id` and a `poll_url` because generation is asynchronous.
2. **Batch size.** `n` is capped at 4 per request on the relayed route.
3. **Version selection.** `gpt-image-2.5-ext` uses `version: "flare" | "sunburst"` instead of a separate model string.
4. **Error envelope.** Validation failures come back as an `error` object with `type` and `code`; treat its shape as part
   of the contract and map it into your own error taxonomy.

## Model routes and IDs

| Route | `model` value | Selector | Billing style | Best for |
| --- | --- | --- | --- | --- |
| Official (token) | `gpt-image-2.5-flare` | n/a | token usage, `quality` low → max | everyday generation, batch drafts |
| Official (token) | `gpt-image-2.5-sunburst` | n/a | token usage, `quality` low → max | editing precision, production assets |
| Relayed (per image) | `gpt-image-2.5-ext` | `version: "flare"` | per delivered image (`n` ≤ 4) | high-volume generation at a flat price |
| Relayed (per image) | `gpt-image-2.5-ext` | `version: "sunburst"` | per delivered image (`n` ≤ 4) | edits and reference-driven work at a flat price |

Both relayed variants accept `resolution` `1K` / `2K` / `4K`, ten aspect ratios plus `auto`, and up to 16 reference images in `image_urls`. The official route adds exact pixel dimensions and the `low / medium / high / xhigh / max` quality ladder.

- Family: **GPT Image 2.5** — the OpenAI image generation and editing series served through APIMart
- Model IDs: `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst` (official route); `gpt-image-2.5-ext` with `version: flare|sunburst` (per-image relay route)
- Base URL: `https://api.apimart.ai/v1` — OpenAI-compatible `POST /v1/images/generations`
- Async tasks: submit, then poll `GET /v1/tasks/{task_id}` until `status: completed`
- Output tiers: `1K`, `2K`, `4K`; up to 16 reference images for image-to-image; `n` ≤ 4
- Observed 1K price on the relayed route: **$0.0085 per delivered image** (checked 2026-09-16)

## Observed pricing

| version | 1K | 2K | 4K | billing unit |
| --- | --- | --- | --- | --- |
| `flare` | $0.0085 | $0.014 | $0.021 | per delivered image |
| `sunburst` | $0.0085 | $0.014 | check live pricing | per delivered image |

Per-image billing on the relayed route is charged for delivered images, and the task response reports the exact amount in `cost` / `credits_cost`, so the table above can be re-verified after a single paid call. The official `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` route is token-billed with a `low → medium → high → xhigh → max` quality ladder, which is why this repository keeps both the flat per-image expectation and the token-billed option side by side. Snapshot date: 2026-09-16.

## What the output looks like

Every render below came from a single `POST /v1/images/generations` call on the relayed route, at the aspect ratio shown.
| Output | Recipe | Use case | Version | Ratio | Prompt |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/02-rainy-tokyo-alley.jpg" width="220" alt="Cinematic night street generated with GPT Image 2.5"> | Cinematic night street | Cinematic still | `flare` | 16:9 | `Rain-slicked Tokyo alley at night, neon sign reflections on wet asphalt, a lone cyclist with an umbrella, cinematic 35mm film still, shallow depth of field` |
| <img src="assets/10-amber-serum-packshot.jpg" width="220" alt="Cosmetics packshot generated with GPT Image 2.5"> | Cosmetics packshot | Product / cosmetics | `sunburst` | 1:1 | `Cosmetics packshot of a frosted glass bottle with amber serum, water droplets on the surface, seamless pale pink backdrop, high detail commercial product photography` |
| <img src="assets/11-floating-ruin-keyart.jpg" width="220" alt="Game key art generated with GPT Image 2.5"> | Game key art | Game concept art | `sunburst` | 16:9 | `Fantasy game key art, an armored knight standing on a floating stone ruin above a sea of clouds, dramatic backlight, painterly detail, wide cinematic composition` |
| <img src="assets/09-monarch-wing-macro.jpg" width="220" alt="Macro nature detail generated with GPT Image 2.5"> | Macro nature detail | Nature macro | `sunburst` | 3:2 | `Macro photograph of a dew covered monarch butterfly wing, iridescent orange scales, deep black background, focus stacked detail, studio lighting` |

Every recipe ships with the exact JSON body in [`examples/`](examples).

## Quickstart

The relayed route is asynchronous: submit, then poll the task ID.

```bash
# text to image on the per-image route
IDEMPOTENCY_KEY="$(uuidgen)"
curl --request POST \
  --url https://api.apimart.ai/v1/images/generations \
  --header "Authorization: Bearer $APIMART_API_KEY" \
  --header 'Content-Type: application/json' \
  --header 'X-APIMart-Response-Version: 2026-07-27' \
  --header "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data '{
    "model": "gpt-image-2.5-ext",
    "version": "flare",
    "prompt": "A cozy reading nook beside a window on a rainy day, warm table lamp, cinematic lighting",
    "size": "1:1",
    "resolution": "1K",
    "n": 1
  }'
```

```python
import os, time, uuid, requests

BASE = "https://api.apimart.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {os.environ['APIMART_API_KEY']}",
    "Content-Type": "application/json",
    "X-APIMart-Response-Version": "2026-07-27",
    "Idempotency-Key": str(uuid.uuid4()),   # reuse on retry, not on a new image
}

def generate(prompt: str, version: str = "flare", resolution: str = "1K", size: str = "1:1") -> str:
    r = requests.post(f"{BASE}/images/generations", headers=HEADERS, timeout=60, json={
        "model": "gpt-image-2.5-ext", "version": version, "prompt": prompt,
        "size": size, "resolution": resolution, "n": 1,
    })
    r.raise_for_status()
    task_id = r.json()["data"]["id"]
    while True:
        t = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS, timeout=60).json()["data"]
        if t["status"] in ("completed", "failed"):
            return t
        time.sleep(5)
```

```javascript
const headers = {
  Authorization: `Bearer ${process.env.APIMART_API_KEY}`,
  "Content-Type": "application/json",
  "X-APIMart-Response-Version": "2026-07-27",
  "Idempotency-Key": crypto.randomUUID(),
};
const res = await fetch("https://api.apimart.ai/v1/images/generations", {
  method: "POST",
  headers,
  body: JSON.stringify({
    model: "gpt-image-2.5-ext", version: "flare", prompt: "A sky garden at dawn, architectural photography",
    size: "16:9", resolution: "1K", n: 1,
  }),
});
const { data } = await res.json();          // data.id === task id
// poll GET https://api.apimart.ai/v1/tasks/${data.id} until data.status === "completed"
```

Official (token-billed) route, for comparison — same path, no `version`, quality ladder instead:

```bash
curl --request POST --url https://api.apimart.ai/v1/images/generations \
  --header "Authorization: Bearer $APIMART_API_KEY" --header 'Content-Type: application/json' \
  --data '{"model":"gpt-image-2.5-sunburst","prompt":"Preserve the product label, replace the background with soft off-white, add a natural cast shadow","size":"1:1","resolution":"1k","quality":"high","n":1}'
```

Full field reference: [official route docs](https://docs.apimart.ai/en/api-reference/images/gpt-image-2.5/generation) and [ext route docs](https://docs.apimart.ai/en/api-reference/images/gpt-image-2.5-ext/generation). Get a key at [apimart.ai/keys](https://go.apimart.ai/k-19dd82).

## Request and response reference (ext route)

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `model` | string | required | `gpt-image-2.5-ext` |
| `version` | string | `flare` | `flare` or `sunburst` |
| `prompt` | string | required | must not be empty after trimming |
| `resolution` | string | `1K` | `1K`, `2K`, `4K` |
| `size` | string | `auto` | `auto` or 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 5:4, 4:5, 21:9 |
| `n` | integer | `1` | 1–4 per request on the relayed route |
| `image_urls` | string[] | — | up to 16 references, URL or data URL, no extra charge |

Submission returns `202` with `data.id` (the task ID) and `data.poll_url`; `GET /v1/tasks/{task_id}` then reports
`status` (`pending` → `processing` → `completed` / `failed`), `progress`, `cost`, `credits_cost` and, when finished,
`result.images[].url` with an `expires_at` timestamp. Download outputs before that timestamp — the URLs are temporary.

## Migration checklist

- [ ] Keep the base URL and the key in environment variables; never patch the URL inside business logic
- [ ] Send `Idempotency-Key` on every submit so retries cannot duplicate a billable image
- [ ] Replace inline-image assumptions with submit → poll → download
- [ ] Clamp `n` to 1–4 and fan out client-side for larger batches
- [ ] Store `model`, `version`, `resolution`, `size`, `cost` and the task ID with every saved asset
- [ ] Add a single-prompt smoke test to CI against the staging key
- [ ] Verify the download window: result URLs expire, so copy outputs into your own storage
- [ ] Re-test one paid request after any pinned response-version bump


## What a drop-in client looks like

```python
# One function, two routes: official (token) or relayed (per image).
def image2_5(prompt, *, route="ext", version="flare", resolution="1K", size="1:1", n=1):
    model = "gpt-image-2.5-ext" if route == "ext" else f"gpt-image-2.5-{version}"
    body = {"model": model, "prompt": prompt, "resolution": resolution, "size": size, "n": n}
    if route == "ext":
        body["version"] = version
    return submit(body)   # returns task_id; poll GET /v1/tasks/{task_id}
```



## FAQ

**Is the image2.5 endpoint a drop-in replacement for the OpenAI images API?**

The request path and JSON body are deliberately close, but the lifecycle is not identical: APIMart's relayed image2.5 route is asynchronous, `n` is capped at 4, and the variant is selected with `version`. Plan for a small adapter layer rather than a URL swap.

**Which base URL do I configure?**

`https://api.apimart.ai/v1` for both chat and image endpoints, with `Authorization: Bearer <key>`.

**How do I keep response parsing stable across API revisions?**

Pin `X-APIMart-Response-Version` on requests and keep envelope handling in one module so a revision is a single-file change.

**What breaks first in a migration?**

Assumptions about synchronous completion and about unbounded `n`. Both surface as timeouts or validation errors rather than wrong images, which is the good version of this failure.

## Related searches

- `image2.5 api`
- `image 2.5 api`
- `image2.5 api gateway`
- `image2-5 api`
- `gpt-image-2.5 api`
- `image2.5 api pricing`
- `ai api relay`
- `ai api gateway`
- `ai api aggregator`
- `apimart image2.5`
- `image2.5 api documentation`
- `openai compatible image api`
- `openai compatible`
- `image api proxy`
- `apimart`
- `image2 5`
- `api migration`

## Attributed links (how this repository is measured)

Every outbound link in this repository points at APIMart through a short link, so visits coming from this page are attributed instead of arriving as anonymous traffic.

| Purpose | Attributed link | Target |
| --- | --- | --- |
| Open GPT Image 2.5 on APIMart | <https://go.apimart.ai/k-0b1178> | `apimart.ai/model/gpt-image-2-5` |
| Current APIMart pricing | <https://go.apimart.ai/k-7d1dda> | `apimart.ai/pricing` |
| Get an API key on APIMart | <https://go.apimart.ai/k-19dd82> | `apimart.ai/keys` |

- [ ] Attribution target: the three `go.apimart.ai` short links above (302 with `utm_source=kol_sponsor&utm_medium=sponsor`); the endpoint docs at `docs.apimart.ai` are referenced without a short link because the link service only accepts the `apimart.ai` domain.
- [ ] Re-check the price on the pricing page before a production run: promotional routing can change.

## Disclosure

APIMart is the service described in this repository; this page is published to document it, not to claim official status. The `ext` route is a third-party relay endpoint billed per delivered image, while the `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` models are the token-billed route. Model names, prices and limits belong to their respective owners, and everything here is observation-dated (2026-09-16). Verify with a single paid request before scaling volume.


## Repository map

```text
apimart-openai-compatible-image2.5-proxy/
  PROMPTS.md           every recipe with its output
  README.md            overview, pricing, quickstart and FAQ
  examples/
    curl.sh            submit + poll with curl
    python_generate.py end-to-end Python client
    javascript.mjs     Node 18+ equivalent
  tools/check_links.py attribution + prompt-data validator
  .github/workflows/validate.yml  CI for the validator
  assets/              example renders (JPEG, resized for the README)
  LICENSE              MIT
```

## License

MIT — see [LICENSE](LICENSE). Model names and vendor documentation remain the property of their owners.
