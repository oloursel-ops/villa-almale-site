/* Villa Almale — floating WhatsApp contact button */
(() => {
  'use strict';

  const WHATSAPP_URL = 'https://wa.me/33687174067?text=Bonjour%2C%20je%20souhaite%20obtenir%20des%20informations%20sur%20la%20disponibilit%C3%A9%20de%20Villa%20Almale.';

  const labels = {
    fr: 'Contacter Villa Almale sur WhatsApp',
    en: 'Contact Villa Almale on WhatsApp',
    es: 'Contactar con Villa Almale por WhatsApp'
  };

  const style = document.createElement('style');
  style.textContent = `
    .whatsapp-float {
      position: fixed;
      right: max(18px, env(safe-area-inset-right));
      bottom: max(18px, env(safe-area-inset-bottom));
      z-index: 90;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 56px;
      height: 56px;
      border: 1px solid rgba(255,255,255,.72);
      border-radius: 50%;
      background: #123f44;
      color: #fff;
      box-shadow: 0 10px 28px rgba(4,29,32,.28);
      transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
      -webkit-tap-highlight-color: transparent;
    }
    .whatsapp-float:hover,
    .whatsapp-float:focus-visible {
      transform: translateY(-2px);
      background: #0d3338;
      box-shadow: 0 14px 34px rgba(4,29,32,.34);
      outline: none;
    }
    .whatsapp-float svg {
      width: 27px;
      height: 27px;
      fill: currentColor;
    }
    @media (max-width: 600px) {
      .whatsapp-float {
        right: max(14px, env(safe-area-inset-right));
        bottom: max(14px, env(safe-area-inset-bottom));
        width: 52px;
        height: 52px;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      .whatsapp-float { transition: none; }
    }
  `;
  document.head.appendChild(style);

  const button = document.createElement('a');
  button.className = 'whatsapp-float';
  button.href = WHATSAPP_URL;
  button.target = '_blank';
  button.rel = 'noopener noreferrer';
  button.setAttribute('aria-label', labels.fr);
  button.title = labels.fr;
  button.innerHTML = `
    <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <path d="M19.11 17.2c-.26-.13-1.54-.76-1.78-.85-.24-.09-.41-.13-.59.13-.17.26-.67.85-.82 1.02-.15.17-.3.2-.56.07-.26-.13-1.09-.4-2.08-1.29-.77-.68-1.29-1.53-1.44-1.79-.15-.26-.02-.4.11-.53.12-.12.26-.3.39-.46.13-.15.17-.26.26-.43.09-.17.04-.33-.02-.46-.07-.13-.59-1.42-.8-1.94-.21-.51-.43-.44-.59-.45h-.5c-.17 0-.46.07-.69.33-.24.26-.91.89-.91 2.18 0 1.28.94 2.52 1.07 2.69.13.17 1.84 2.81 4.46 3.94.62.27 1.11.43 1.49.55.63.2 1.2.17 1.65.1.5-.07 1.54-.63 1.76-1.24.22-.61.22-1.13.15-1.24-.06-.11-.24-.17-.5-.3z"/>
      <path d="M16.04 3.2A12.55 12.55 0 0 0 5.18 22.03L3.2 28.8l6.94-1.82a12.56 12.56 0 1 0 5.9-23.78zm0 22.83c-2.05 0-4.05-.55-5.79-1.59l-.41-.24-4.12 1.08 1.1-4.01-.27-.42a10.27 10.27 0 1 1 9.49 5.18z"/>
    </svg>`;

  const updateLanguage = () => {
    const active = document.querySelector('.langs button.active');
    const lang = active?.dataset.lang || document.documentElement.lang || 'fr';
    const label = labels[lang] || labels.fr;
    button.setAttribute('aria-label', label);
    button.title = label;
  };

  const mount = () => {
    if (!document.querySelector('.whatsapp-float')) {
      document.body.appendChild(button);
    }
    updateLanguage();

    document.querySelectorAll('.langs button').forEach((languageButton) => {
      languageButton.addEventListener('click', () => setTimeout(updateLanguage, 0));
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
