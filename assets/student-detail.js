/* ==========================================================================
   Detalle del estudiante · accesibilidad
   --------------------------------------------------------------------------
   La tabla del directorio es un dash_table.DataTable, así que sus celdas no
   son enfocables por defecto. Este script:

     1. Convierte la celda del código (columna "estudiante") en un elemento
        enfocable con role="link" y activación por Enter/Espacio.
     2. Da al modal el comportamiento esperado: Escape para cerrar, clic en
        el fondo para cerrar y foco atrapado mientras está abierto.

   No crea elementos visuales nuevos ni modifica estilos.
   ========================================================================== */
(function () {
  "use strict";

  var MODAL_ID = "student-detail-modal";
  var CARD_ID = "student-detail-body";
  var CLOSE_ID = "close-student-detail";
  var CODE_SELECTOR = '#students-table td[data-dash-column="estudiante"]';
  var FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]),' +
    ' select:not([disabled]), [tabindex]:not([tabindex="-1"])';

  var wasOpen = false;
  var previousFocus = null;

  function modal() {
    return document.getElementById(MODAL_ID);
  }

  function isOpen() {
    var el = modal();
    return !!el && el.className.indexOf("hidden") === -1;
  }

  function requestClose() {
    var button = document.getElementById(CLOSE_ID);
    if (button) {
      button.click();
    }
  }

  /* --- 1. Código del estudiante enfocable ------------------------------- */
  function enhanceCodes() {
    var cells = document.querySelectorAll(CODE_SELECTOR);
    for (var i = 0; i < cells.length; i++) {
      var cell = cells[i];
      if (cell.getAttribute("data-a11y-ready") === "1") {
        continue;
      }
      cell.setAttribute("data-a11y-ready", "1");
      cell.setAttribute("tabindex", "0");
      cell.setAttribute("role", "link");
    }
  }

  /* --- 2. Foco atrapado dentro del modal -------------------------------- */
  function focusableItems() {
    var card = document.getElementById(CARD_ID);
    if (!card) {
      return [];
    }
    return Array.prototype.filter.call(card.querySelectorAll(FOCUSABLE), function (node) {
      return node.offsetParent !== null;
    });
  }

  function trapFocus(event) {
    var card = document.getElementById(CARD_ID);
    if (!card) {
      return;
    }
    var items = focusableItems();
    if (!items.length) {
      return;
    }
    var first = items[0];
    var last = items[items.length - 1];
    var active = document.activeElement;
    if (active === card || !card.contains(active)) {
      event.preventDefault();
      (event.shiftKey ? last : first).focus();
      return;
    }
    if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && active === first) {
      event.preventDefault();
      last.focus();
    }
  }

  /* --- 3. Sincronización con el estado del modal ------------------------ */
  function syncModal() {
    var open = isOpen();
    if (open === wasOpen) {
      return;
    }
    wasOpen = open;
    if (open) {
      previousFocus = document.activeElement;
      var card = document.getElementById(CARD_ID);
      if (card) {
        card.focus();
      }
    } else if (previousFocus && document.contains(previousFocus)) {
      var origin = previousFocus.closest ? previousFocus.closest(CODE_SELECTOR) : null;
      (origin || previousFocus).focus();
      previousFocus = null;
    }
  }

  function refresh() {
    enhanceCodes();
    syncModal();
  }

  /* --- 4. Eventos ------------------------------------------------------- */
  document.addEventListener(
    "keydown",
    function (event) {
      if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") {
        var target = event.target;
        var cell = target && target.closest ? target.closest(CODE_SELECTOR) : null;
        if (cell) {
          event.preventDefault();
          cell.click();
          return;
        }
      }
      if (!isOpen()) {
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        requestClose();
        return;
      }
      if (event.key === "Tab") {
        trapFocus(event);
      }
    },
    true
  );

  document.addEventListener("click", function (event) {
    var el = modal();
    if (el && isOpen() && event.target === el) {
      requestClose();
    }
  });

  new MutationObserver(refresh).observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["class"],
  });

  refresh();
})();
