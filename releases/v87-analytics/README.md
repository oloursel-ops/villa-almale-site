# Villa ALMALE — V8.7 Analytics / OwnerRez funnel

Date: 2026-08-09

## Objective

Extend the existing consent-gated GA4 measurement from the Villa ALMALE website into the OwnerRez direct-booking funnel, while preserving the site's explicit prior-consent policy for EU visitors.

GA4 Measurement ID: `G-K6CXR43Q9Y`

## Production audit before patch

The production files were downloaded directly from Infomaniak through the protected GitHub Actions production environment.

Confirmed:

- GA4 is enabled only after explicit audience-measurement consent.
- `analytics_storage` is denied before consent and granted only after acceptance.
- Google Signals and ad-personalisation signals remain disabled.
- Existing site events include booking-page views and booking-engine clicks.
- FR/EN/ES reservation pages all embed live OwnerRez Booking/Inquiry widgets.
- The OwnerRez-recommended GA cookie setting `SameSite=None;Secure` was absent.
- No OwnerRez cross-domain/linker configuration was present in the website analytics code.

Pre-patch production SHA-256 for `assets/js/audience.js`:

`6aca52bcd9ac4aa75d6508e29fd911850a027298205f5ea4a5d8f7a6c5892a29`

## V8.7 production change

Only `assets/js/audience.js` was changed.

Added, inside `loadAnalytics()` and therefore only after explicit analytics consent:

```js
window.gtag('set', {
  'cookie_flags': 'SameSite=None;Secure'
});
```

This is the setting recommended by OwnerRez for cross-domain GA continuity between an external website and OwnerRez widgets / booking forms.

No HTML page, OwnerRez widget, content, URL, SEO metadata, consent text, advertising setting, or booking configuration was changed.

Deployment used exact pre-patch fingerprint validation, a temporary remote-file byte check, rollback protection, a live post-upload byte comparison, and retained rollback evidence as a GitHub Actions artifact.

Post-patch production SHA-256 for `assets/js/audience.js`:

`18a37c304c98acb94fbd437c5ae662174edb05ad5085ad3d8df7f4a87b712a08`

A second independent production audit confirmed `SameSite=None;Secure` is present and that the consent gating, Google Signals setting, and FR/EN/ES OwnerRez widgets remain intact.

## Current funnel state

Website side:

1. Landing/page view — measured after consent.
2. Booking-page view — measured after consent.
3. Click toward booking engine — measured after consent (`click_booking_engine`; legacy `booking_click` references are normalised by the current code).
4. OwnerRez widget is present on all three booking pages.

OwnerRez-side GA events are **not yet enabled**.

OwnerRez documentation states that, once the same GA4 Measurement ID is entered under **Settings > Advanced Tools > Analytics Tracking**, OwnerRez can send widget/booking-funnel events including QuoteDisplayed, BookingStarted / GA4 `begin_checkout`, and booking-completion/e-commerce data.

## Privacy / consent blocker before enabling OwnerRez native GA4

The external Villa ALMALE site deliberately does not load GA4 until the visitor explicitly accepts audience measurement. OwnerRez's public analytics documentation describes its GA4 tracking and cross-domain behaviour, but does not document whether an embedded widget inherits the consent state of the parent external website or how Consent Mode is propagated.

Therefore the GA4 Measurement ID has **not** been enabled in OwnerRez yet, to avoid the possibility of OwnerRez firing the Villa ALMALE GA4 tag inside its widget or hosted checkout after a visitor has rejected analytics on the parent site.

A support question was sent to `help@ownerrez.com` on 2026-08-09 asking OwnerRez to confirm:

- whether widget / hosted checkout analytics respect the parent site's consent state;
- how to suppress OwnerRez GA4 for visitors who reject analytics while keeping booking functional;
- whether Consent Mode v2 or another consent signal is supported;
- which OwnerRez domains should be configured in GA4 cross-domain measurement.

## Pending actions

1. Await OwnerRez's answer on consent propagation.
2. Configure GA4 cross-domain domains in Google Analytics Admin (safe to prepare independently; final domain list to be confirmed with OwnerRez).
3. If consent handling is acceptable, enter `G-K6CXR43Q9Y` in OwnerRez Analytics Tracking.
4. Perform a controlled consent-accepted test: landing -> reservation -> quote -> checkout -> test/real booking, verifying client/session continuity and OwnerRez events.
5. Perform a consent-rejected test and verify that no Villa ALMALE GA4 requests are emitted from either the parent site or OwnerRez flow.
6. Only after those tests, mark `begin_checkout` and `purchase` as key funnel events and use them for campaign decisions.

## GitHub Actions evidence

- Audit workflow: `.github/workflows/audit-analytics-v87.yml`
- Guarded deployment workflow: `.github/workflows/deploy-analytics-v87.yml`
- First production audit: run `31333630737`
- V8.7 guarded deployment: run `31333727345`
- Post-deployment production audit: run `31333777081`
