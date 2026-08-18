/* Client-side search for the WIEMIP docs.
   Index is built by docs/build_docs.py into /docs/search-index.json: one entry per
   h2/h3 section, so a hit lands on the heading rather than the top of the page.
   Fetched on first focus, not on load. */
(function () {
  "use strict";
  var box = document.getElementById("docs-search");
  var out = document.getElementById("docs-search-results");
  if (!box || !out) return;

  var index = null, loading = false, hits = [];

  function load() {
    if (index || loading) return;
    loading = true;
    fetch("/docs/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; render(); })
      .catch(function () { out.innerHTML = "<li class='docs-search-empty'>search index unavailable</li>"; out.hidden = false; });
  }

  function escape(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function render() {
    var query = box.value.trim().toLowerCase();
    if (!query) { out.hidden = true; out.innerHTML = ""; hits = []; return; }
    if (!index) { load(); return; }

    var terms = query.split(/\s+/);
    hits = index.map(function (entry) {
      var haystack = (entry.p + " " + entry.h + " " + entry.t).toLowerCase();
      for (var i = 0; i < terms.length; i++) {
        if (haystack.indexOf(terms[i]) === -1) return null;
      }
      // Heading matches beat body matches, so `.read()` finds its own section first.
      var score = 0;
      terms.forEach(function (t) {
        if (entry.h.toLowerCase().indexOf(t) > -1) score += 3;
        if (entry.p.toLowerCase().indexOf(t) > -1) score += 1;
      });
      return { entry: entry, score: score };
    }).filter(Boolean).sort(function (a, b) {
      return b.score - a.score;
    }).slice(0, 12).map(function (h) { return h.entry; });

    if (!hits.length) {
      out.innerHTML = "<li class='docs-search-empty'>no matches</li>";
      out.hidden = false;
      return;
    }
    out.innerHTML = hits.map(function (e) {
      return "<li><a href='" + e.u + e.a + "'>" +
             "<strong>" + escape(e.h) + "</strong>" +
             "<small>" + escape(e.p) + "</small></a></li>";
    }).join("");
    out.hidden = false;
  }

  box.addEventListener("input", render);
  box.addEventListener("focus", load);

  box.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && hits.length) {
      window.location.href = hits[0].u + hits[0].a;
    } else if (e.key === "Escape") {
      box.value = ""; render(); box.blur();
    }
  });

  // `/` focuses search, the convention on docs sites.
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== box) {
      e.preventDefault();
      box.focus();
    }
  });

  document.addEventListener("click", function (e) {
    if (!out.contains(e.target) && e.target !== box) out.hidden = true;
  });
})();
