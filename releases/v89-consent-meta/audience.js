(() => {
  "use strict";

  const cfg = window.VILLA_ANALYTICS_CONFIG || {};
  const validMeasurementId = /^G-[A-Z0-9]+$/i.test(cfg.measurementId || "") && cfg.measurementId !== "G-REPLACE_ME";
  const analyticsAvailable = Boolean(cfg.enabled && validMeasurementId);
  // V8.9 introduces three explicit privacy choices. A new key deliberately
  // prompts existing visitors again because previous consent covered GA4 only,
  // not advertising measurement with Meta.
  const consentKey = 'villa_privacy_consent_v89';
  const metaPixelId = '813403868466271';
  const metaAvailable = /^\d{8,20}$/.test(metaPixelId);
  const maxAgeMs = (Number(cfg.consentValidityDays) || 180) * 86400000;
  const lang = (document.documentElement.lang || "en").toLowerCase().slice(0, 2);
  const copy = {
    fr: {
      title: "Vos choix de confidentialité",
      text: "Les fonctions indispensables du site restent actives. Vous pouvez autoriser uniquement la mesure d’audience avec Google Analytics, ou tous les cookies pour inclure la mesure publicitaire Meta. Aucun contenu de formulaire n’est transmis par nos balises.",
      reject: "Tout refuser",
      audience: "Mesure d’audience",
      acceptAll: "Tout accepter",
      manage: "Gérer mes cookies",
      details: "En savoir plus",
      inactive: "Le module de mesure d’audience est préparé mais pas encore activé."
    },
    es: {
      title: "Sus opciones de privacidad",
      text: "Las funciones indispensables del sitio permanecen activas. Puede autorizar solo la medición de audiencia con Google Analytics, o todas las cookies para incluir la medición publicitaria de Meta. Nuestras etiquetas no transmiten el contenido de los formularios.",
      reject: "Rechazar todo",
      audience: "Solo audiencia",
      acceptAll: "Aceptar todo",
      manage: "Gestionar mis cookies",
      details: "Más información",
      inactive: "El módulo de medición de audiencia está preparado, pero aún no está activado."
    },
    en: {
      title: "Your privacy choices",
      text: "Essential website functions remain active. You can allow audience measurement with Google Analytics only, or all cookies to include Meta advertising measurement. Our tags do not send form contents.",
      reject: "Reject all",
      audience: "Audience only",
      acceptAll: "Accept all",
      manage: "Manage my cookies",
      details: "Learn more",
      inactive: "The audience measurement module is prepared but not yet activated."
    },
    sv: {
      title: "Dina integritetsval",
      text: "Nödvändiga webbplatsfunktioner förblir aktiva. Du kan endast tillåta besöksmätning med Google Analytics, eller alla cookies för att även inkludera Metas annonsmätning. Våra taggar skickar inte innehåll från formulär.",
      reject: "Avvisa alla",
      audience: "Endast besöksmätning",
      acceptAll: "Godkänn alla",
      manage: "Hantera mina cookies",
      details: "Läs mer",
      inactive: "Modulen för besöksmätning är förberedd men ännu inte aktiverad."
    }
  }[lang] || {
    title: "Your privacy choices",
    text: "Essential website functions remain active. You can allow audience measurement with Google Analytics only, or all cookies to include Meta advertising measurement. Our tags do not send form contents.",
    reject: "Reject all",
    audience: "Audience only",
    acceptAll: "Accept all",
    manage: "Manage my cookies",
    details: "Learn more",
    inactive: "The audience measurement module is prepared but not yet activated."
  };

  let loaded = false;
  let metaLoaded = false;
  let scrollTracked = false;

  function getChoice() {
    try {
      const raw = localStorage.getItem(consentKey);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.choice || !parsed.timestamp || Date.now() - parsed.timestamp > maxAgeMs) {
        localStorage.removeItem(consentKey);
        return null;
      }
      return parsed.choice;
    } catch (_) {
      return null;
    }
  }

  function setChoice(choice) {
    try {
      localStorage.setItem(consentKey, JSON.stringify({choice, timestamp: Date.now()}));
    } catch (_) {}
  }

  function logConsentChoice(choice, previousChoice) {
    const allowed = ['rejected', 'audience', 'all'];
    if (!allowed.includes(choice)) return;
    const previous = allowed.includes(previousChoice) ? previousChoice : 'unset';
    try {
      const endpoint = `/assets/consent-choice-v88.txt?choice=${encodeURIComponent(choice)}&from=${encodeURIComponent(previous)}&ts=${Date.now()}`;
      fetch(endpoint, {
        method: 'GET',
        credentials: 'omit',
        cache: 'no-store',
        keepalive: true
      }).catch(() => {});
    } catch (_) {}
  }

  function deleteAnalyticsCookies() {
    const names = document.cookie.split(';').map(item => item.split('=')[0].trim());
    const domains = [location.hostname, `.${location.hostname.replace(/^www\./, '')}`];
    names.filter(name => name === '_ga' || name.startsWith('_ga_')).forEach(name => {
      document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`;
      domains.forEach(domain => {
        document.cookie = `${name}=; Max-Age=0; path=/; domain=${domain}; SameSite=Lax`;
      });
    });
  }

  function deleteMetaCookies() {
    const names = ['_fbp', '_fbc'];
    const domains = [location.hostname, `.${location.hostname.replace(/^www\./, '')}`];
    names.forEach(name => {
      document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`;
      domains.forEach(domain => {
        document.cookie = `${name}=; Max-Age=0; path=/; domain=${domain}; SameSite=Lax`;
      });
    });
  }

  function disableMeta({reload = false} = {}) {
    if (typeof window.fbq === 'function') {
      try { window.fbq('consent', 'revoke'); } catch (_) {}
    }
    deleteMetaCookies();
    if (reload) location.reload();
  }

  function disableAnalytics({reload = false} = {}) {
    if (validMeasurementId) window[`ga-disable-${cfg.measurementId}`] = true;
    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
    }
    deleteAnalyticsCookies();
    if (reload) location.reload();
  }

  function loadAnalytics() {
    if (loaded || !analyticsAvailable) return;
    if (validMeasurementId) window[`ga-disable-${cfg.measurementId}`] = false;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'denied',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      functionality_storage: 'granted',
      security_storage: 'granted'
    });
    window.gtag('consent', 'update', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    // Required by OwnerRez for GA4 session continuity between this site and embedded booking widgets.
    // This executes only after the visitor has explicitly accepted audience measurement.
    window.gtag('set', {
      'cookie_flags': 'SameSite=None;Secure'
    });
    window.gtag('js', new Date());
    window.gtag('config', cfg.measurementId, {
      cookie_expires: Number(cfg.cookieLifetimeSeconds) || 31536000,
      cookie_update: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      send_page_view: true,
      debug_mode: Boolean(cfg.debug)
    });
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(cfg.measurementId)}`;
    script.referrerPolicy = 'strict-origin-when-cross-origin';
    document.head.appendChild(script);

    const path = location.pathname;
    if (path.includes('/off-season/')) track('view_offseason_page', {page_path: path});
    if (path.includes('reservation')) track('view_booking_page', {page_path: path});
  }

  function loadMetaPixel() {
    if (metaLoaded || !metaAvailable) return;
    metaLoaded = true;
    !function(f,b,e,v,n,t,src){
      if(f.fbq)return;
      n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;
      n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];
      t=b.createElement(e);t.async=!0;t.src=v;
      src=b.getElementsByTagName(e)[0];src.parentNode.insertBefore(t,src);
    }(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('consent', 'grant');
    window.fbq('init', metaPixelId);
    window.fbq('track', 'PageView');
  }

  function track(name, params = {}) {
    if (!loaded || typeof window.gtag !== 'function') return;
    // Keep one canonical GA4 event name for every real click towards the
    // booking engine. Older pages still expose `booking_click` in their HTML.
    const eventName = name === 'booking_click' ? 'click_booking_engine' : name;
    window.gtag('event', eventName, params);
  }

  function policyHref() {
    return `/cookies.html?lang=${encodeURIComponent(lang)}`;
  }

  function ensureBannerStyle() {
    if (document.getElementById('audience-consent-v89-style')) return;
    const style = document.createElement('style');
    style.id = 'audience-consent-v89-style';
    style.textContent = `
      .audience-consent{position:fixed;z-index:9999;left:50%;bottom:18px;transform:translateX(-50%);width:min(760px,calc(100% - 24px));background:#fffdf8;color:#17363b;border:1px solid rgba(23,54,59,.18);border-radius:18px;box-shadow:0 18px 60px rgba(4,29,32,.22);padding:20px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      .audience-consent[hidden]{display:none}
      .audience-consent h2{font-family:Georgia,"Times New Roman",serif;font-size:1.35rem;font-weight:400;line-height:1.15;margin:0 0 8px}
      .audience-consent p{margin:0;color:#536d70;font-size:.94rem;line-height:1.5}
      .audience-consent a{text-decoration:underline;text-underline-offset:2px}
      .audience-status{display:block;margin-top:8px;font-size:.82rem;color:#637779}
      .audience-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:16px}
      .audience-button{min-height:46px;padding:10px 12px;border:1px solid #123f44;border-radius:999px;background:#fffdf8;color:#123f44;font:inherit;font-weight:750;cursor:pointer}
      .audience-button:hover,.audience-button:focus-visible{background:#123f44;color:#fff;outline:none}
      .audience-settings{font:inherit}
      @media(max-width:640px){.audience-consent{bottom:10px;padding:17px}.audience-actions{grid-template-columns:1fr}.audience-button{width:100%}}
    `;
    document.head.appendChild(style);
  }

  function applyChoice(choice, {reloadOnDowngrade = false} = {}) {
    const analyticsWasLoaded = loaded;
    const metaWasLoaded = metaLoaded;
    if (choice === 'all') {
      loadAnalytics();
      loadMetaPixel();
      return;
    }
    if (choice === 'audience') {
      loadAnalytics();
      disableMeta();
      if (reloadOnDowngrade && metaWasLoaded) location.reload();
      return;
    }
    disableAnalytics();
    disableMeta();
    if (reloadOnDowngrade && (analyticsWasLoaded || metaWasLoaded)) location.reload();
  }

  function createBanner() {
    let banner = document.getElementById('audience-consent');
    if (banner) return banner;
    ensureBannerStyle();
    banner = document.createElement('aside');
    banner.id = 'audience-consent';
    banner.className = 'audience-consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-modal', 'false');
    banner.setAttribute('aria-label', copy.manage);
    banner.innerHTML = `<div><h2>${copy.title}</h2><p>${copy.text} <a href="${policyHref()}">${copy.details}</a>.</p>${analyticsAvailable ? '' : `<span class="audience-status">${copy.inactive}</span>`}</div><div class="audience-actions"><button class="audience-button" type="button" data-consent="rejected">${copy.reject}</button><button class="audience-button" type="button" data-consent="audience">${copy.audience}</button><button class="audience-button" type="button" data-consent="all">${copy.acceptAll}</button></div>`;
    document.body.appendChild(banner);
    banner.querySelectorAll('[data-consent]').forEach(button => {
      button.addEventListener('click', () => {
        const choice = button.dataset.consent;
        const previousChoice = getChoice();
        setChoice(choice);
        logConsentChoice(choice, previousChoice);
        banner.hidden = true;
        applyChoice(choice, {reloadOnDowngrade: true});
      });
    });
    return banner;
  }

  function addSettingsControl() {
    const footer = document.querySelector('footer');
    if (!footer || footer.querySelector('[data-audience-settings]')) return;
    const wrap = document.createElement('span');
    wrap.className = 'audience-settings-wrap';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'audience-settings';
    button.dataset.audienceSettings = '';
    button.textContent = copy.manage;
    button.addEventListener('click', () => {
      const banner = createBanner();
      banner.hidden = false;
      banner.querySelector('button')?.focus();
    });
    wrap.appendChild(button);
    const target = footer.querySelector('.legal-links, .footer-links, nav') || footer;
    target.appendChild(wrap);
  }

  function classifyLink(link) {
    const explicit = link.dataset.analyticsEvent;
    if (explicit) return explicit;
    const href = (link.getAttribute('href') || '').toLowerCase();
    if (!href) return null;
    if (href.startsWith('mailto:')) return 'contact_click';
    if (href.includes('reservation') || href.includes('ownerrez')) return 'click_booking_engine';
    if (href.includes('golfnuevoportil') || href.includes('golfelrompido') || href.includes('islantillagolfresort') || href.includes('islacanela')) return 'golf_club_click';
    if (link.hasAttribute('hreflang') || link.closest('.languages,.langs,.lang-menu')) return 'language_select';
    if (href.includes('facebook.com') || href.includes('instagram.com')) return 'social_click';
    return null;
  }

  document.addEventListener('click', event => {
    const languageControl = event.target.closest('[data-lang]');
    if (languageControl && !languageControl.matches('a')) {
      track('language_select', {
        language: languageControl.dataset.lang || '',
        page_path: location.pathname
      });
    }

    const link = event.target.closest('a');
    if (!link) return;
    const name = classifyLink(link);
    if (!name) return;
    let destination = link.getAttribute('href') || '';
    try {
      const url = new URL(destination, location.href);
      destination = `${url.hostname}${url.pathname}`;
    } catch (_) {}
    track(name, {
      link_text: (link.textContent || '').trim().slice(0, 80),
      link_destination: destination.slice(0, 160),
      page_path: location.pathname
    });
  }, {passive: true});

  window.addEventListener('scroll', () => {
    if (scrollTracked) return;
    const max = document.documentElement.scrollHeight - innerHeight;
    if (max > 0 && scrollY / max >= 0.75) {
      scrollTracked = true;
      track('scroll_75', {page_path: location.pathname});
    }
  }, {passive: true});

  document.addEventListener('DOMContentLoaded', () => {
    // The banner remains available whenever either optional measurement module
    // can be used. Essential website functionality never depends on consent.
    if (!analyticsAvailable && !metaAvailable) return;
    addSettingsControl();
    const choice = getChoice();
    if (choice === 'all' || choice === 'audience' || choice === 'rejected') applyChoice(choice);
    else createBanner();
  });
})();
