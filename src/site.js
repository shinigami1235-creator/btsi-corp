(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- header state ----------------------------------------------------- */
  var head = document.querySelector(".site-head");
  function headState() { if (head) head.classList.toggle("stuck", window.scrollY > 40); }
  headState();

  /* --- mobile menu ------------------------------------------------------ */
  var burger = document.querySelector(".burger");
  var nav = document.getElementById("sitenav");

  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A" && window.innerWidth <= 1080) {
        nav.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
      }
    });
  }

  document.querySelectorAll(".has-menu").forEach(function (menu) {
    var btn = menu.querySelector(".nav-top");
    if (!btn) return;
    btn.addEventListener("click", function (ev) {
      ev.stopPropagation();
      var open = menu.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  document.addEventListener("click", function (ev) {
    document.querySelectorAll(".has-menu.open").forEach(function (menu) {
      if (!menu.contains(ev.target)) {
        menu.classList.remove("open");
        var b = menu.querySelector(".nav-top");
        if (b) b.setAttribute("aria-expanded", "false");
      }
    });
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    document.querySelectorAll(".has-menu.open").forEach(function (m) { m.classList.remove("open"); });
    if (nav) nav.classList.remove("open");
    if (burger) burger.setAttribute("aria-expanded", "false");
  });

  /* --- hero slider and parallax ----------------------------------------- */
  var bg = document.querySelector(".hero-bg");
  var slides = bg ? [].slice.call(bg.querySelectorAll(".slide")) : [];

  /* Photographs past the first carry their source in data-src, so the first
     paint pays for one rather than three. */
  function hydrate(el) {
    if (!el) return;
    var imgs = el.matches && el.matches("img[data-src]")
      ? [el] : [].slice.call(el.querySelectorAll("img[data-src]"));
    imgs.forEach(function (im) {
      if (im.dataset.srcset) im.srcset = im.dataset.srcset;
      im.src = im.dataset.src;
      im.removeAttribute("data-src");
      im.removeAttribute("data-srcset");
    });
  }

  /* The hero slides come in once the page has finished loading. */
  function hydrateHero() { slides.forEach(hydrate); }
  if (document.readyState === "complete") setTimeout(hydrateHero, 200);
  else window.addEventListener("load", function () { setTimeout(hydrateHero, 200); });

  /* The gallery waits until it is nearly on screen. */
  var gal = document.querySelector(".gal");
  if (gal) {
    if (!("IntersectionObserver" in window)) {
      window.addEventListener("load", function () { hydrate(gal); });
    } else {
      var gio = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        gio.disconnect();
        hydrate(gal);
      }, { rootMargin: "300px 0px" });
      gio.observe(gal);
    }
  }
  var dotsBox = document.querySelector(".hero-dots");
  var hi = 0, heroTimer = null, HERO_MS = 7000;

  if (slides.length > 1 && dotsBox) {
    slides.forEach(function (s, n) {
      var b = document.createElement("button");
      b.className = "dot" + (n === 0 ? " on" : "");
      b.type = "button";
      b.setAttribute("aria-label", "Slide " + (n + 1));
      b.innerHTML = "<span></span>";
      b.addEventListener("click", function () { heroGo(n); });
      dotsBox.appendChild(b);
    });
  }
  var heroDots = dotsBox ? [].slice.call(dotsBox.children) : [];

  function heroGo(n) {
    if (!slides.length) return;
    hi = (n + slides.length) % slides.length;
    hydrate(slides[hi]);
    hydrate(slides[(hi + 1) % slides.length]);
    slides.forEach(function (s, k) { s.classList.toggle("on", k === hi); });
    heroDots.forEach(function (d, k) {
      d.classList.remove("on");
      if (k === hi) { void d.offsetWidth; d.classList.add("on"); }
    });
    heroRestart();
  }
  function heroRestart() {
    if (reduce || slides.length < 2) return;
    clearInterval(heroTimer);
    heroTimer = setInterval(function () { heroGo(hi + 1); }, HERO_MS);
  }
  heroRestart();

  var px = 0, py = 0, sy = 0, raf = null;
  function applyParallax() {
    slides.forEach(function (s) {
      var im = s.querySelector("img");
      if (im) im.style.transform = "translate3d(" + px + "px," + (sy * 0.2 + py) + "px,0) scale(1.12)";
    });
    raf = null;
  }
  function queueParallax() { if (!raf && !reduce && slides.length) raf = requestAnimationFrame(applyParallax); }

  window.addEventListener("scroll", function () {
    headState();
    sy = Math.min(window.scrollY, window.innerHeight);
    queueParallax();
  }, { passive: true });

  window.addEventListener("pointermove", function (ev) {
    if (window.scrollY > window.innerHeight || window.innerWidth < 1080) return;
    px = (ev.clientX / window.innerWidth - 0.5) * -26;
    py = (ev.clientY / window.innerHeight - 0.5) * -16;
    queueParallax();
  }, { passive: true });

  /* --- ticker ----------------------------------------------------------- */
  var track = document.querySelector(".tick-track");
  if (track && !reduce) track.innerHTML += track.innerHTML;

  /* --- gallery slider --------------------------------------------------- */
  var view = document.querySelector(".gal-view");
  if (view) {
    var count = view.children.length;
    var gi = 0, gTimer = null;
    var gn = document.querySelector(".gal-i b");
    var gbar = document.querySelector(".gal-bar b");
    var gnext = document.querySelector(".gal-next");
    var gprev = document.querySelector(".gal-prev");

    var galGo = function (n) {
      gi = (n + count) % count;
      view.style.transform = "translateX(" + (-gi * 100) + "%)";
      if (gn) gn.textContent = (gi + 1 < 10 ? "0" : "") + (gi + 1);
      if (gbar) gbar.style.transform = "scaleX(" + ((gi + 1) / count) + ")";
      if (!reduce) {
        clearInterval(gTimer);
        gTimer = setInterval(function () { galGo(gi + 1); }, 6500);
      }
    };
    if (gnext) gnext.addEventListener("click", function () { galGo(gi + 1); });
    if (gprev) gprev.addEventListener("click", function () { galGo(gi - 1); });
    galGo(0);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearInterval(gTimer); else galGo(gi);
    });
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) clearInterval(heroTimer); else heroRestart();
  });

  /* --- scroll reveal ---------------------------------------------------- */
  var reveal = document.querySelectorAll(".r");
  if (reveal.length) {
    if (reduce || !("IntersectionObserver" in window)) {
      reveal.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          en.target.classList.add("in");
          io.unobserve(en.target);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
      reveal.forEach(function (el) { io.observe(el); });
    }
  }

  /* --- testimonials ----------------------------------------------------- */
  var quotes = [].slice.call(document.querySelectorAll(".quote"));
  var qdots = [].slice.call(document.querySelectorAll(".q-dot"));
  if (quotes.length > 1) {
    var qi = 0, qTimer = null;
    var qGo = function (n) {
      qi = (n + quotes.length) % quotes.length;
      quotes.forEach(function (q, k) { q.classList.toggle("on", k === qi); });
      qdots.forEach(function (d, k) { d.classList.toggle("on", k === qi); });
      if (!reduce) {
        clearInterval(qTimer);
        qTimer = setInterval(function () { qGo(qi + 1); }, 9000);
      }
    };
    qdots.forEach(function (d, k) { d.addEventListener("click", function () { qGo(k); }); });
    qGo(0);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearInterval(qTimer); else qGo(qi);
    });
  }

  /* --- find ------------------------------------------------------------- */
  var find = document.querySelector(".find");
  if (find) {
    var input = find.querySelector("input");
    var clear = find.querySelector(".find-clear");
    var countEl = find.querySelector(".find-count");
    var out = find.querySelector(".find-results");
    var scope = find.dataset.scope;
    var root = find.dataset.root || "/";
    var NONE = find.dataset.none || "";
    var PENDING = find.dataset.pending || "";
    var cards = [].slice.call(document.querySelectorAll(".card[data-find]"));
    var blocks = [].slice.call(document.querySelectorAll(".cat-block"));
    var index = null, loading = false, pending = "";

    var terms = function (q) {
      return q.toLowerCase().split(/\s+/).filter(Boolean);
    };
    var hits = function (hay, ts) {
      for (var i = 0; i < ts.length; i++) if (hay.indexOf(ts[i]) === -1) return false;
      return true;
    };
    var plural = function (n) { return n === 1 ? "1 product" : n + " products"; };

    /* scope "page": hide the cards that do not match, and any category block
       left with nothing in it. */
    function filterPage(q) {
      var ts = terms(q), shown = 0;
      cards.forEach(function (c) {
        var ok = !ts.length || hits(c.dataset.find, ts);
        c.classList.toggle("is-out", !ok);
        if (ok) shown++;
      });
      blocks.forEach(function (b) {
        var any = b.querySelector(".card:not(.is-out)");
        b.classList.toggle("is-empty", !any);
      });
      countEl.textContent = ts.length ? (shown ? plural(shown) : NONE) : "";
    }

    /* scope "all": one fetch of the index, then render matches as cards. */
    function render(rows, ts) {
      out.innerHTML = "";
      rows.forEach(function (r) {
        var a = document.createElement("a");
        a.className = "card";
        a.href = root + "products/" + r.s + "/";
        var media = document.createElement("span");
        media.className = "card-media is-placeholder";
        var img = document.createElement("img");
        img.className = "ph-mark"; img.src = root + "assets/site/logo-mark.png";
        img.width = 160; img.height = 160; img.alt = ""; img.loading = "lazy";
        var ph = document.createElement("span");
        ph.className = "ph-text"; ph.textContent = PENDING;
        media.appendChild(img); media.appendChild(ph);
        var body = document.createElement("span");
        body.className = "card-body";
        if (r.b) {
          var chip = document.createElement("span");
          chip.className = "chip"; chip.textContent = r.b;
          body.appendChild(chip);
        }
        var t = document.createElement("span");
        t.className = "card-title"; t.textContent = r.t;
        var l = document.createElement("span");
        l.className = "card-line"; l.textContent = r.l;
        body.appendChild(t); body.appendChild(l);
        a.appendChild(media); a.appendChild(body);
        out.appendChild(a);
      });
      out.hidden = !rows.length;
      countEl.textContent = ts.length ? (rows.length ? plural(rows.length) : NONE) : "";
    }

    function searchAll(q) {
      var ts = terms(q);
      if (!ts.length) { out.hidden = true; out.innerHTML = ""; countEl.textContent = ""; return; }
      if (!index) {
        pending = q;
        if (loading) return;
        loading = true;
        countEl.textContent = "";
        fetch(find.dataset.index).then(function (r) { return r.json(); }).then(function (rows) {
          index = rows; loading = false;
          if (pending) searchAll(pending);
        }).catch(function () {
          loading = false;
          countEl.textContent = NONE;
        });
        return;
      }
      var ts2 = terms(q);
      render(index.filter(function (r) {
        return hits((r.t + " " + r.b + " " + r.c.join(" ")).toLowerCase(), ts2);
      }).slice(0, 60), ts2);
    }

    var run = function () {
      var q = input.value.trim();
      clear.hidden = !q;
      if (scope === "all") searchAll(q); else filterPage(q);
    };
    var timer = null;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(run, 110);
    });
    input.addEventListener("search", run);
    clear.addEventListener("click", function () { input.value = ""; run(); input.focus(); });
    find.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && input.value) { input.value = ""; run(); }
    });
  }

  /* --- counters --------------------------------------------------------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    var nio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        nio.unobserve(en.target);
        var el = en.target, end = parseInt(el.dataset.count, 10);
        if (reduce || isNaN(end)) { el.textContent = el.dataset.count; return; }
        var t0 = performance.now();
        (function step(now) {
          var p = Math.min((now - t0) / 1300, 1);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { nio.observe(el); });
  }
})();
