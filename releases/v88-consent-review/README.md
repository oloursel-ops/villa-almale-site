# Villa ALMALE — V8.8 consent-choice counter + Airbnb review count

Date: 2026-08-10

## Changes deployed

### Explicit consent-choice measurement

`assets/js/audience.js` now sends a minimal same-origin request when a visitor explicitly chooses the analytics-consent banner:

- `choice=accepted` or `choice=rejected`
- `from=unset` for an initial decision, or the previous saved choice when a visitor changes/reconfirms it
- a timestamp used only to avoid cache coalescing

The request is made to `/assets/consent-choice-v88.txt` with `credentials: 'omit'`, `cache: 'no-store'` and `keepalive: true`.

No Google Analytics call is added for rejected consent, no third-party endpoint is used, and no additional visitor identifier or cookie is introduced by this patch. Normal web-server access logs continue to contain their standard request metadata.

For initial-choice analysis, count only requests where `from=unset`:

- `choice=accepted&from=unset` = explicit initial acceptance
- `choice=rejected&from=unset` = explicit initial refusal
- landing-page arrivals without either initial-choice request = no explicit interaction during the observed visit, subject to normal log/session matching limits

Measurement begins only after this deployment; it is not retrospective.

Existing V8.7 consent gating remains unchanged: GA4 still loads only after explicit acceptance. Existing `SameSite=None;Secure`, `analytics_storage` handling and disabled Google Signals remain intact.

### Airbnb review count

Only the displayed count was updated from one to two reviews. No additional review quotation, citation, card or reorganisation was added.

Updated public pages:

- `/` → `2 avis` and FR/EN/ES dynamic review-count strings
- `/en/` → `2 reviews`
- `/es/` → `2 opiniones`
- `/off-season/` → `2 reviews`
- `/off-season/fr/` → `2 avis`
- `/off-season/es/` → `2 opiniones`
- `/off-season/sv/` → `2 omdömen`

The existing quoted Airbnb review remains unchanged.

## Production evidence

- Pre-deployment production audit: GitHub Actions run `31436303392` — success.
- Guarded deployment: run `31436775237`.
  - exact pre-patch SHA validation: success
  - upload: success
  - byte-for-byte remote verification: success
  - its first public smoke test returned a false negative because it tested explicit `/index.html` routing; no rollback occurred because the deployed bytes were verified successfully.
- Canonical public verification: run `31436938699` — success for `/`, `/en/`, `/es/`, `/off-season/`, `/off-season/fr/`, `/off-season/es/`, `/off-season/sv/`, the consent-choice endpoint and the patched `audience.js`.

A pre-patch rollback artifact was retained from the guarded deployment run.
