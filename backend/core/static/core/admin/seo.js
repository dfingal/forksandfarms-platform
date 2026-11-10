/*
 * Admin "SEO" section helpers (core/admin.py SEOAdminMixin):
 *  - live character counters under the SEO title and meta description,
 *    turning amber when over Google's rough display limit;
 *  - keeps the Google-result preview in sync as you type, showing the
 *    automatic value whenever a field is blank;
 *  - shows a "hidden from search engines" note while noindex is ticked.
 *
 * Plain JavaScript, no dependencies. Does nothing on pages without the
 * SEO section.
 */
(function () {
  "use strict";

  function setUpCounter(input, limit, fallback, onChange) {
    var counter = document.createElement("div");
    counter.className = "seo-counter";
    counter.setAttribute("aria-live", "polite");
    input.insertAdjacentElement("afterend", counter);

    function update() {
      var typed = input.value.trim();
      var length = typed ? typed.length : fallback.length;
      var over = length > limit;
      var prefix = typed ? "" : "Blank — using the automatic text: ";
      counter.textContent =
        prefix + length + " / " + limit + " characters" + (over ? " — Google may cut this off" : "");
      counter.classList.toggle("seo-counter--over", over);
      onChange(typed || fallback);
    }

    input.addEventListener("input", update);
    update();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var preview = document.querySelector(".seo-preview");
    var titleInput = document.getElementById("id_seo_title");
    var descriptionInput = document.getElementById("id_meta_description");
    if (!preview || !titleInput || !descriptionInput) return;

    var previewTitle = preview.querySelector(".seo-preview__title");
    var previewDescription = preview.querySelector(".seo-preview__description");

    setUpCounter(
      titleInput,
      Number(preview.dataset.titleLimit),
      preview.dataset.fallbackTitle,
      function (text) {
        previewTitle.textContent = text;
      }
    );
    setUpCounter(
      descriptionInput,
      Number(preview.dataset.descriptionLimit),
      preview.dataset.fallbackDescription,
      function (text) {
        previewDescription.textContent = text;
      }
    );

    var noindexInput = document.getElementById("id_noindex");
    if (noindexInput) {
      var syncNoindex = function () {
        preview.classList.toggle("seo-preview--noindex", noindexInput.checked);
      };
      noindexInput.addEventListener("change", syncNoindex);
      syncNoindex();
    }
  });
})();
