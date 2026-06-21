/** Instant auth-page language switch (login / register dropdown). */
(function () {
  const locales = window.AUTH_LOCALES;
  if (!locales) return;

  function applyAuthLang(lang) {
    const t = locales[lang] || locales.en;
    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const key = el.getAttribute("data-i18n");
      if (t[key]) el.textContent = t[key];
    });

    const titleKey = window.AUTH_TITLE_KEY || "app_title";
    const titleEl = document.getElementById("i18n-page-title");
    if (titleEl && t[titleKey]) {
      titleEl.textContent = t[titleKey];
      document.title = t[titleKey];
    }

    const sel = document.querySelector("select[name='lang']");
    if (sel) {
      const optEn = sel.querySelector("option[value='en']");
      const optSw = sel.querySelector("option[value='sw']");
      if (optEn) optEn.textContent = t.lang_en;
      if (optSw) optSw.textContent = t.lang_sw;
      sel.value = lang;
    }
  }

  const sel = document.querySelector("select[name='lang']");
  if (sel) {
    sel.addEventListener("change", function () {
      applyAuthLang(sel.value);
    });
    applyAuthLang(sel.value || "en");
  }
})();
