(() => {
  const toggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');
  if (toggle && nav) {
    const close = () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('nav-open');
    };
    toggle.addEventListener('click', () => {
      const open = !nav.classList.contains('open');
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('nav-open', open);
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', close));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  }

  document.querySelectorAll('img[data-fallback]').forEach(img => {
    img.addEventListener('error', () => {
      const fallback = img.dataset.fallback;
      if (fallback && img.src !== fallback) img.src = fallback;
    }, { once: true });
  });

  document.querySelectorAll('[data-track]').forEach(link => {
    link.addEventListener('click', () => {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: 'offseason_cta',
        offseason_cta: link.dataset.track,
        page_language: document.documentElement.lang,
        page_path: location.pathname
      });
    });
  });

  document.querySelectorAll('[data-mail-form]').forEach(form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const d = new FormData(form);
      const subject = encodeURIComponent(d.get('subject') || 'Villa ALMALE — off-season enquiry');
      const lines = [];
      for (const [key, value] of d.entries()) {
        if (key !== 'subject' && String(value).trim()) {
          const label = key.replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
          lines.push(`${label}: ${value}`);
        }
      }
      location.href = `mailto:contact@villanuevoportil.com?subject=${subject}&body=${encodeURIComponent(lines.join('\n'))}`;
    });
  });
})();
