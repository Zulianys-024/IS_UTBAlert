/* Mostrar/ocultar contraseña del login sin pasar por el servidor.
 * Solo cambia el atributo type del input: nunca lee, guarda ni envía el valor.
 */
(function () {
  "use strict";

  var EYE_OPEN =
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" ' +
    'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
    'stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    '<path d="M2.2 12S5.8 5.8 12 5.8 21.8 12 21.8 12 18.2 18.2 12 18.2 2.2 12 2.2 12Z"/>' +
    '<circle cx="12" cy="12" r="3.1"/></svg>';

  var EYE_OFF =
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" ' +
    'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
    'stroke-linejoin="round" aria-hidden="true" focusable="false">' +
    '<path d="M3 3l18 18"/>' +
    '<path d="M10.4 6.1A10.6 10.6 0 0 1 12 6c6.2 0 9.8 6 9.8 6a17.9 17.9 0 0 1-3.3 3.9' +
    'M6.6 7.9A18.4 18.4 0 0 0 2.2 12s3.6 6 9.8 6a9.9 9.9 0 0 0 3.4-.6"/></svg>';

  function getButton() {
    return document.getElementById("login-toggle-pass");
  }

  function getInput() {
    return document.getElementById("login-pass");
  }

  function isVisible(input) {
    return input.type === "text";
  }

  function paint(button, visible) {
    var state = visible ? "on" : "off";
    var icon = button.querySelector(".login-eye-svg");
    if (!icon) {
      icon = document.createElement("span");
      icon.className = "login-eye-svg";
      icon.setAttribute("aria-hidden", "true");
      button.appendChild(icon);
    }
    /* Evita reescribir el SVG si ya está en el estado correcto (sin bucles). */
    if (icon.dataset.state !== state || !icon.firstElementChild) {
      icon.innerHTML = visible ? EYE_OFF : EYE_OPEN;
      icon.dataset.state = state;
    }
    button.classList.toggle("visible", visible);
    button.setAttribute("aria-pressed", visible ? "true" : "false");
    var label = visible ? button.dataset.labelHide : button.dataset.labelShow;
    if (label) {
      button.setAttribute("aria-label", label);
      button.setAttribute("title", label);
    }
  }

  function hide(button, input) {
    if (input.type !== "password") {
      input.type = "password";
    }
    paint(button, false);
  }

  function toggle(button, input) {
    var visible = !isVisible(input);
    var start = null;
    var end = null;
    var direction = null;
    try {
      start = input.selectionStart;
      end = input.selectionEnd;
      direction = input.selectionDirection;
    } catch (error) {
      /* el navegador puede no exponer la selección; se ignora */
    }

    input.type = visible ? "text" : "password";
    paint(button, visible);

    try {
      input.focus({ preventScroll: true });
    } catch (error) {
      input.focus();
    }
    if (start !== null && end !== null) {
      try {
        input.setSelectionRange(start, end, direction || "none");
      } catch (error) {
        /* setSelectionRange no disponible; se ignora */
      }
    }
  }

  function sync() {
    var button = getButton();
    var input = getInput();
    if (!button || !input) {
      return;
    }

    if (button.dataset.eyeReady !== "1") {
      button.dataset.eyeReady = "1";

      button.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        toggle(button, input);
      });

      /* Al enviar con Enter se vuelve a ocultar antes del login. */
      input.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.isComposing) {
          hide(button, input);
        }
      });
    }

    /* La contraseña siempre arranca oculta y el ícono refleja el estado real. */
    paint(button, isVisible(input));
  }

  /* Al pulsar "Ingresar" se oculta antes de que Dash procese el login. */
  document.addEventListener(
    "click",
    function (event) {
      var target = event.target;
      if (!target || !target.closest || !target.closest("#login-button")) {
        return;
      }
      var button = getButton();
      var input = getInput();
      if (button && input) {
        hide(button, input);
      }
    },
    true
  );

  /* Dash puede volver a montar el login (re-render, cambio de idioma, logout). */
  var scheduled = false;
  function scheduleSync() {
    if (scheduled) {
      return;
    }
    scheduled = true;
    window.requestAnimationFrame(function () {
      scheduled = false;
      sync();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleSync);
  } else {
    scheduleSync();
  }

  if (typeof MutationObserver !== "undefined") {
    new MutationObserver(scheduleSync).observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  }
})();
