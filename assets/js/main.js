(() => {
  "use strict";

  // Small visual corrections applied after the main stylesheet.
  // Keeping them here allows rapid mobile QA fixes without invalidating the design system.
  const visualPatch = document.createElement("style");
  visualPatch.textContent = `
    .language-switcher button.active { background: #fff; color: var(--deep); }
    .site-header.scrolled .language-switcher button.active { background: var(--deep); color: #fff; }
    @media (max-width: 560px) {
      .scroll-cue { display: none; }
      .hero-stats { row-gap: 18px; }
      .hero-stats div { min-width: 50%; padding-inline: 14px; }
      .hero-stats div:nth-child(odd) { padding-left: 0; border-left: 0; }
      .hero-stats div:nth-child(even) { border-left: 1px solid rgba(255,255,255,.34); }
    }
  `;
  document.head.append(visualPatch);

  const translations = window.VILLA_TRANSLATIONS || {};
  const config = window.VILLA_CONFIG || {};
  const root = document.documentElement;
  const header = document.getElementById("site-header");
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("main-nav");
  const toast = document.getElementById("toast");
  function readStoredLanguage() {
    try { return localStorage.getItem("villa-language"); } catch (_) { return null; }
  }
  function storeLanguage(lang) {
    try { localStorage.setItem("villa-language", lang); } catch (_) { /* Storage may be unavailable in previews. */ }
  }
  let currentLang = readStoredLanguage() || "fr";

  function t(key) {
    return translations[currentLang]?.[key] ?? translations.fr?.[key] ?? key;
  }

  function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    storeLanguage(lang);
    root.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.dataset.i18n;
      if (translations[lang][key] !== undefined) element.textContent = translations[lang][key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const key = element.dataset.i18nPlaceholder;
      if (translations[lang][key] !== undefined) element.placeholder = translations[lang][key];
    });
    document.querySelectorAll("[data-lang]").forEach((button) => {
      const active = button.dataset.lang === lang;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    document.title = translations[lang].metaTitle;
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = translations[lang].metaDescription;
  }

  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.lang));
  });
  setLanguage(currentLang);

  function setHeaderState() {
    header?.classList.toggle("scrolled", window.scrollY > 35);
  }
  setHeaderState();
  window.addEventListener("scroll", setHeaderState, { passive: true });

  menuToggle?.addEventListener("click", () => {
    const open = !document.body.classList.contains("menu-open");
    document.body.classList.toggle("menu-open", open);
    menuToggle.setAttribute("aria-expanded", String(open));
  });
  nav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      document.body.classList.remove("menu-open");
      menuToggle?.setAttribute("aria-expanded", "false");
    });
  });

  const revealObserver = "IntersectionObserver" in window
    ? new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -35px" })
    : null;
  document.querySelectorAll(".reveal").forEach((element) => {
    if (revealObserver) revealObserver.observe(element);
    else element.classList.add("visible");
  });

  document.querySelectorAll("img[data-fallback]").forEach((image) => {
    image.addEventListener("error", () => {
      const fallback = image.dataset.fallback;
      if (fallback && image.src !== new URL(fallback, document.baseURI).href) {
        image.src = fallback;
      }
    }, { once: true });
  });

  const today = new Date();
  const todayIso = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  document.querySelectorAll('input[type="date"]').forEach((input) => { input.min = todayIso; });

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => toast.classList.remove("show"), 2800);
  }

  function datesAreValid(arrival, departure) {
    return arrival && departure && new Date(departure) > new Date(arrival);
  }

  const quickForm = document.getElementById("quick-form");
  const inquiryForm = document.getElementById("inquiry-form");
  quickForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(quickForm);
    const arrival = String(data.get("arrival") || "");
    const departure = String(data.get("departure") || "");
    if (!datesAreValid(arrival, departure)) {
      showToast(t("invalidDates"));
      return;
    }
    if (inquiryForm) {
      inquiryForm.elements.arrival.value = arrival;
      inquiryForm.elements.departure.value = departure;
      const guests = Number(data.get("guests") || 2);
      inquiryForm.elements.adults.value = String(Math.min(6, guests));
      inquiryForm.elements.children.value = String(Math.max(0, guests - 6));
    }
    document.getElementById("booking")?.scrollIntoView({ behavior: "smooth" });
  });

  inquiryForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(inquiryForm);
    const arrival = String(data.get("arrival") || "");
    const departure = String(data.get("departure") || "");
    if (!datesAreValid(arrival, departure)) {
      showToast(t("invalidDates"));
      return;
    }

    const adults = String(data.get("adults") || "");
    const children = String(data.get("children") || "0");
    const name = String(data.get("name") || "").trim();
    const email = String(data.get("email") || "").trim();
    const message = String(data.get("message") || "").trim();
    const lines = [
      t("emailGreeting"),
      "",
      `${t("emailDates")}: ${arrival} → ${departure}.`,
      `${t("emailGuests")}: ${adults} ${t("adults").toLowerCase()}, ${children} ${t("children").toLowerCase()}.`,
      `${t("emailFrom")}: ${name} — ${email}.`,
      "",
      message,
      "",
      t("emailClosing")
    ].filter((line, index, array) => line !== "" || array[index - 1] !== "");

    const recipient = config.inquiryEmail || "oloursel@hotmail.com";
    const mailto = `mailto:${encodeURIComponent(recipient)}?subject=${encodeURIComponent(t("emailSubject"))}&body=${encodeURIComponent(lines.join("\n"))}`;
    showToast(t("mailOpening"));
    window.setTimeout(() => { window.location.href = mailto; }, 200);
  });

  const lightbox = document.getElementById("lightbox");
  const lightboxImage = lightbox?.querySelector("figure img");
  const lightboxCaption = lightbox?.querySelector("figcaption");
  const galleryButtons = [...document.querySelectorAll("[data-gallery-index]")];
  let galleryIndex = 0;

  function galleryData() {
    return galleryButtons.map((button) => {
      const image = button.querySelector("img");
      return { src: image?.currentSrc || image?.src || "", alt: image?.alt || "", caption: button.querySelector("span")?.textContent || "" };
    });
  }
  function renderLightbox(index) {
    const items = galleryData();
    if (!items.length || !lightboxImage || !lightboxCaption) return;
    galleryIndex = (index + items.length) % items.length;
    lightboxImage.src = items[galleryIndex].src;
    lightboxImage.alt = items[galleryIndex].alt;
    lightboxCaption.textContent = items[galleryIndex].caption;
  }
  galleryButtons.forEach((button, index) => {
    button.addEventListener("click", () => {
      renderLightbox(index);
      if (typeof lightbox?.showModal === "function") lightbox.showModal();
    });
  });
  lightbox?.querySelector(".lightbox-close")?.addEventListener("click", () => lightbox.close());
  lightbox?.querySelector(".lightbox-prev")?.addEventListener("click", () => renderLightbox(galleryIndex - 1));
  lightbox?.querySelector(".lightbox-next")?.addEventListener("click", () => renderLightbox(galleryIndex + 1));
  lightbox?.addEventListener("click", (event) => { if (event.target === lightbox) lightbox.close(); });
  document.addEventListener("keydown", (event) => {
    if (!lightbox?.open) return;
    if (event.key === "ArrowLeft") renderLightbox(galleryIndex - 1);
    if (event.key === "ArrowRight") renderLightbox(galleryIndex + 1);
  });

  document.getElementById("year").textContent = String(new Date().getFullYear());
})();
