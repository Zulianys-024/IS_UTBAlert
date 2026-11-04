/* ==========================================================================
   Notificación temporal (toast)
   --------------------------------------------------------------------------
   La notificación se rellena desde un callback de Dash. Este script sólo
   controla su visibilidad: la muestra al recibir contenido nuevo y la oculta
   automáticamente a los 3 segundos (2.8 s + transición de salida).
   ========================================================================== */
(function () {
  "use strict";

  var TOAST_ID = "toast";
  var VISIBLE_MS = 2800;
  var timer = null;

  function show(el) {
    el.classList.add("show");
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(function () {
      el.classList.remove("show");
    }, VISIBLE_MS);
  }

  function watch(el) {
    new MutationObserver(function () {
      if ((el.textContent || "").trim()) {
        show(el);
      }
    }).observe(el, { childList: true, subtree: true, characterData: true });

    if ((el.textContent || "").trim()) {
      show(el);
    }
  }

  function init() {
    var el = document.getElementById(TOAST_ID);
    if (el) {
      watch(el);
      return;
    }
    // El layout de Dash se monta después de cargar los assets.
    var observer = new MutationObserver(function () {
      var toast = document.getElementById(TOAST_ID);
      if (toast) {
        observer.disconnect();
        watch(toast);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
