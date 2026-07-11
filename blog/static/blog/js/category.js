/* Category page interaktivligi
   - Kategoriya kartasini bosganda o'sha kategoriyaning blog ro'yxati ochiladi
   - "Orqaga" tugmasi kartalar gridiga qaytaradi
   - URL hash (#business) orqali to'g'ridan-to'g'ri ochish qo'llab-quvvatlanadi */
(function () {
  "use strict";

  var grid = document.querySelector(".category-grid");
  var listsWrap = document.querySelector(".category-lists");
  if (!grid || !listsWrap) return;

  var lists = listsWrap.querySelectorAll(".category-list");

  function showCategory(key) {
    var target = listsWrap.querySelector('.category-list[data-list="' + key + '"]');
    if (!target) return;

    lists.forEach(function (el) { el.classList.remove("is-active"); });
    target.classList.add("is-active");

    grid.style.display = "none";
    listsWrap.classList.add("is-active");

    if (history.replaceState) {
      history.replaceState(null, "", "#" + key);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function showGrid() {
    listsWrap.classList.remove("is-active");
    lists.forEach(function (el) { el.classList.remove("is-active"); });
    grid.style.display = "";

    if (history.replaceState) {
      history.replaceState(null, "", location.pathname);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Kartalarni ulash
  grid.querySelectorAll(".category-card").forEach(function (card) {
    card.addEventListener("click", function () {
      showCategory(card.getAttribute("data-category"));
    });
  });

  // "Orqaga" tugmalari
  listsWrap.querySelectorAll(".category-back").forEach(function (btn) {
    btn.addEventListener("click", showGrid);
  });

  // Sahifa hash bilan ochilsa (masalan boshqa sahifadan category.html#travel)
  var hash = (location.hash || "").replace("#", "");
  if (hash) showCategory(hash);
})();
