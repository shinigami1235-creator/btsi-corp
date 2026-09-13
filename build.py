# -*- coding: utf-8 -*-
"""Static site generator for 8BTSI Corp.

Reads one file per product, manufacturer and testimonial from data/, the shape
of the equipment section from taxonomy.json, and our own authored copy from
content.py, and writes a complete static site to dist/.

A product is added by writing a file in data/products, which the website editor
at /admin/ does for you. Nothing in here changes.
"""
import hashlib
import html
import json
import os
import re
import shutil
import urllib.parse

import content as C

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
ASSETS_SRC = os.path.join(ROOT, "assets")


def stamp(name):
    """Eight characters of the file's own hash, hung off the end of its address.

    The address changes whenever the file does, so a browser or a CDN holding
    the old one has nothing to serve: it has never seen this address before.
    Without it a stylesheet edit can sit behind a week-old cached copy, and no
    amount of reloading the page will shift it."""
    path = os.path.join(ROOT, "src", name)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return "?v=" + hashlib.sha1(f.read()).hexdigest()[:8]

# ---------------------------------------------------------------- deployment
# TARGET decides where the build expects to be served from.
#   "pages"   GitHub Pages project page at <GH_USER>.github.io/<REPO>/.
#             Every path gets the repo prefix and the pages carry noindex, so
#             the preview cannot compete with btsi.com.ph in search results.
#   "domain"  The real thing at btsi.com.ph, served from the root.
TARGET = "pages"

GH_USER = "shinigami1235-creator"
REPO = "btsi-corp"

if TARGET == "pages":
    BASE = "/" + REPO
    SITE_URL = "https://%s.github.io/%s" % (GH_USER, REPO)
    NOINDEX = True
else:
    BASE = ""
    SITE_URL = "https://btsi.com.ph"
    NOINDEX = False

# GitHub Pages runs no server code, so the Netlify form is off and the quote
# section is the phone number and the two email addresses instead. Set this
# back to True only on a host that can accept a POST.
FORMS = False

# Editorial photography for the home page. Three Unsplash photographs, served
# from the Unsplash CDN with sizing in the query string. To host them yourself,
# download each one, save it under assets/site/, and change "src" to
# "/assets/site/<file>.jpg". Nothing else in the build refers to them.
UNSPLASH = "https://images.unsplash.com/%s?auto=format&fit=crop&w=1920&q=70"
UNSPLASH_W = (640, 960, 1280, 1920)


def photo_srcset(photo_id):
    """Four widths so a phone fetches a phone-sized file.

    The hero and the gallery ask for the same widths and the same sizes, so the
    browser reuses one download for both rather than fetching each photograph
    twice.
    """
    base = "https://images.unsplash.com/%s?auto=format&fit=crop&q=70&w=%d"
    return ", ".join("%s %dw" % (base % (photo_id, w), w) for w in UNSPLASH_W)

SCENES = [
    {
        "key": "transmitter",
        "id": "photo-1533664488202-6af66d26c44a",
        "src": UNSPLASH % "photo-1533664488202-6af66d26c44a",
        "credit": "Mario Caruso, https://unsplash.com/photos/0C9VmZUqcT8",
        "alt": "Broadcast transmission masts silhouetted against the sky at sunset",
        "label": "Transmitter site",
        "head": "From a 20W exciter to a 50kW AM plant.",
        "body": "Elenos FM transmitters, Continental Lensa AM transmitters, the remote "
                "control and changeover units that keep an unattended site running, and "
                "Aldena antennas to radiate the result.",
    },
    {
        "key": "studio",
        "id": "photo-1767474833531-c1be2788064a",
        "src": UNSPLASH % "photo-1767474833531-c1be2788064a",
        "credit": "Jacob Hodgson, https://unsplash.com/photos/Zwl5xuwGVUU",
        "alt": "A broadcast audio mixing console with its channel buttons lit",
        "label": "Studio",
        "head": "A studio built on audio over IP.",
        "body": "Axia consoles and xNodes carry the audio on the network, Omnia processors "
                "shape what goes to the transmitter, Telos systems put callers on air, "
                "Yellowtec mounts the microphones and Vicoustic panels treat the room.",
    },
    {
        "key": "playout",
        "id": "photo-1768222935380-0a3a76fbb42e",
        "src": UNSPLASH % "photo-1768222935380-0a3a76fbb42e",
        "credit": "Gabriel Weyand, https://unsplash.com/photos/X8uonmU2Ssw",
        "alt": "A television gallery monitor showing a multiview of several camera feeds",
        "label": "Playout and headend",
        "head": "Automation that runs a channel without someone watching the clock.",
        "body": "PlayBox covers television playout, ingest, on-screen graphics, ad insertion "
                "and archive, while WinMedia handles radio playout, music scheduling and "
                "traffic.",
    },
]

ARROW = ('<svg width="15" height="11" viewBox="0 0 15 11" aria-hidden="true">'
         '<path d="M9.5 1l4.5 4.5L9.5 10M14 5.5H0" fill="none" stroke="currentColor" '
         'stroke-width="1.6"/></svg>')

def load_json(name):
    """Both files are UTF-8. Say so, because Python on Windows defaults to
    cp1252 and falls over on the first accented character."""
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


CSS_V = stamp("style.css")
JS_V = stamp("site.js")

def load_records(folder):
    """Every .json file in data/<folder>/, keyed by its filename.

    The filename is the slug, which is the address the page gets, so renaming a
    file moves a page and deleting one removes it. Nothing else decides."""
    d = os.path.join(ROOT, "data", folder)
    out = {}
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                out[fn[:-5]] = json.load(f)
    return out


PRODUCTS = load_records("products")
BRANDS = load_records("brands")
TESTIMONIALS = [t for _, t in sorted(load_records("testimonials").items())]

# taxonomy.json is the shape of the site: which categories hang off which of
# the five pillars, and in what order. It says nothing about which products are
# in them, because each product carries its own brand and categories. One
# product, one file, one place to change it.
tax = load_json("taxonomy.json")

PILLAR_OF_CAT = {}
for p, d in tax["pillars"].items():
    for c in d["categories"]:
        PILLAR_OF_CAT[c] = p

BRAND_OF = {s: p.get("brand", "") for s, p in PRODUCTS.items() if p.get("brand")}
CATS_OF = {s: list(p.get("categories") or []) for s, p in PRODUCTS.items()}


def _by_title(slugs):
    return sorted(slugs, key=lambda s: PRODUCTS[s]["title"].lower())


# Membership, worked out from the products rather than kept alongside them.
# Every brand and every category keeps its key even when nothing is in it yet,
# so a brand with no products still counts as a brand and reports zero.
tax["brands"] = {b: [] for b in BRANDS}
for s, b in BRAND_OF.items():
    tax["brands"].setdefault(b, []).append(s)
tax["categories"] = {c: [] for c in PILLAR_OF_CAT}
for s, cats in CATS_OF.items():
    for c in cats:
        tax["categories"].setdefault(c, []).append(s)

# Alphabetical within a brand and within a category. A new product lands where
# it belongs on its own; nobody has to decide where in a list to put it.
for group in (tax["brands"], tax["categories"]):
    for k in group:
        group[k] = _by_title(group[k])

# ------------------------------------------------------------- body cleaning
QUOTE_BOILERPLATE = re.compile(
    r"×?\s*Request A Quote.*$", re.S | re.I)
GALLERY_BOILERPLATE = re.compile(
    r"Click on the (left or right arrow button|image).*?(\.pdf|another image)\.?", re.S | re.I)


def _words(s):
    return set(re.findall(r"[a-z0-9.]+", s.lower()))


def dedash(s):
    """Take em and en dashes out of manufacturer prose.

    A dash between two spaces becomes a comma when it interrupts a clause and a
    full stop when the next word starts a new sentence. Product names keep the
    dash they were given, so this runs on body text only.
    """
    s = re.sub(r"\s*[–—]\s*(?=[A-Z][a-z]{2,}\s)", ". ", s)
    s = re.sub(r"\s*[–—]\s*", ", ", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"\s+([,.])", r"\1", s)
    return straighten(s)


def straighten(s):
    """Curly quotes and ellipsis characters out, plain ones in."""
    return (s.replace("‘", "'").replace("’", "'")
             .replace("“", '"').replace("”", '"')
             .replace("…", "..."))


def clean_body(raw, title="", excerpt=""):
    """Split the manufacturer's description into lead paragraphs, features and FAQ."""
    t = QUOTE_BOILERPLATE.sub("", raw or "")
    t = GALLERY_BOILERPLATE.sub("", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()

    faq = []
    m = re.search(r"\bFAQs?:\s*", t)
    if m:
        faq_text = t[m.end():]
        t = t[:m.start()].strip()
        faq = [x.strip() for x in faq_text.split("\n") if x.strip()]

    features = []
    m = re.search(r"\b(Features|Highlights|Benefits|Key Features)\s*:?\s*\n", t)
    if m:
        feat_text = t[m.end():]
        t = t[:m.start()].strip()
        features = [x.strip(" •-") for x in feat_text.split("\n") if x.strip()]

    paras = [p.strip() for p in t.split("\n") if p.strip()]

    # The old theme repeated the product name as the first line of the body.
    tw = _words(title)
    while paras:
        p0 = paras[0]
        if len(p0) < 90 and tw and len(_words(p0) & tw) / max(1, len(_words(p0))) > 0.7:
            paras.pop(0)
            continue
        break

    # Anything under four words is a layout scrap rather than a sentence.
    paras = [p for p in paras if len(p.split()) >= 4]

    # A one-line FAQ is the old site's link label with the link stripped off it.
    faq = [f for f in faq if len(f) >= 60]

    paras = [dedash(p) for p in paras]
    features = [dedash(f) for f in features]
    faq = [dedash(f) for f in faq]
    return paras, features, faq


def clean_title(t):
    """Take dashes out of the manufacturer's product names.

    A dash between two figures is a range and becomes "to". Every other dash is
    a separator between the model and what it does, so it becomes a space.
    """
    t = re.sub(r"(\d[\w.]*)\s*[–—]\s*(?=\d)", r"\1 to ", t)
    t = re.sub(r"\s*[–—]\s*", " ", t)
    t = t.replace(" & ", " and ")
    return straighten(re.sub(r"\s+", " ", t).strip())


# Excerpts are shown as page ledes and meta descriptions, so they get the same
# dash treatment as the body.
for _p in PRODUCTS.values():
    _p["excerpt"] = dedash(re.sub(r"\s+", " ", _p["excerpt"]).strip())
    _p["title"] = clean_title(_p["title"])


def brand_logo(slug):
    """The manufacturer's logo, from the record or named after the brand."""
    return _stored_or_convention(
        BRANDS.get(slug, {}).get("logo"), "brands", slug, ("jpg", "png", "webp"))


def featured_image(slug):
    for ext in ("jpg", "png"):
        if os.path.exists(os.path.join(ASSETS_SRC, "featured", "%s.%s" % (slug, ext))):
            return "/assets/featured/%s.%s" % (slug, ext)
    return None


def site_image(name):
    p = os.path.join(ASSETS_SRC, "site", name)
    return ("/assets/site/" + name) if os.path.exists(p) else None


def asset_path(value):
    """Normalise a path stored by the editor.

    Sveltia writes whatever public_folder says, which carries the /btsi-corp
    prefix so its own thumbnails resolve. rebase() adds that prefix again at
    the end of the build, and the prefix disappears entirely the day the site
    moves to btsi.com.ph. So the stored value is reduced to a plain site path
    here and the prefix is applied in exactly one place."""
    v = (value or "").strip()
    if not v:
        return ""
    if BASE and v.startswith(BASE + "/"):
        v = v[len(BASE):]
    return v if v.startswith("/") else "/" + v


def _stored_or_convention(value, folder, slug, exts):
    v = asset_path(value)
    if v and os.path.exists(os.path.join(ROOT, v.lstrip("/"))):
        return v
    for ext in exts:
        if os.path.exists(os.path.join(ASSETS_SRC, folder, "%s.%s" % (slug, ext))):
            return "/assets/%s/%s.%s" % (folder, slug, ext)
    return None


def product_image(slug):
    """The photograph on the record, or one named after the slug, or nothing."""
    return _stored_or_convention(
        PRODUCTS.get(slug, {}).get("photo"), "products", slug,
        ("jpg", "jpeg", "png", "webp"))


# ------------------------------------------------------------------ helpers
def e(s):
    return html.escape(s or "", quote=True)


def slug_title(slug):
    return C.CATEGORY_TITLES.get(slug, slug.replace("-", " ").title())


def brand_name(b):
    return BRANDS[b]["name"] if b in BRANDS else b.replace("-", " ").title()


def rebase(text):
    """Prefix every root-relative href, src and CSS url() with BASE.

    Absolute URLs start with a scheme and protocol-relative ones with a second
    slash, so the negative lookahead leaves both alone. The url() case covers
    background images written into a style attribute, which the href and src
    rule alone would walk straight past.
    """
    if not BASE:
        return text
    text = re.sub(r'(href|src|imagesrcset|srcset)="/(?!/)', r'\1="%s/' % BASE, text)
    text = re.sub(r'url\((["\']?)/(?!/)', r'url(\1%s/' % BASE, text)
    return text


def write(path, text):
    full = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if path.endswith(".html"):
        text = rebase(text)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


# ------------------------------------------------------------------- layout
def nav_html(active=""):
    pillar_links = "".join(
        '<a href="/equipment/%s/"><span>%s</span><small>%s</small></a>'
        % (s, e(d["title"]), e(C.PILLARS[s]["card"]))
        for s, d in tax["pillars"].items()
    )
    return """
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="logo" href="/" aria-label="8BTSI Corp home">
      <img class="logo-mark" src="/assets/site/logo-mark.png" alt="" width="160" height="160">
      <img class="logo-word" src="/assets/site/logo-word-light.png" alt="8BTSI Corp." width="543" height="88">
    </a>
    <button class="burger" aria-expanded="false" aria-controls="sitenav" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
    <nav id="sitenav" class="site-nav">
      <div class="has-menu">
        <button class="nav-top" aria-expanded="false">%(equipment)s<svg width="10" height="6" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>
        <div class="mega">%(pillars)s</div>
      </div>
      <a class="nav-top%(a_brands)s" href="/brands/">%(brands)s</a>
      <a class="nav-top%(a_services)s" href="/services/">%(services)s</a>
      <a class="nav-top%(a_company)s" href="/company/">%(company)s</a>
      <a class="nav-top" href="/company/#customers">%(customers)s</a>
      <a class="nav-top%(a_contact)s" href="/contact/">%(contact)s</a>
      <a class="btn btn-sm nav-cta" href="/contact/#quote">%(quote)s</a>
    </nav>
  </div>
</header>""" % {
        "pillars": pillar_links,
        "equipment": e(C.UI["nav_products"]),
        "brands": e(C.UI["nav_brands"]),
        "services": e(C.UI["nav_services"]),
        "company": e(C.UI["nav_company"]),
        "customers": e(C.UI["nav_customers"]),
        "contact": e(C.UI["nav_contact"]),
        "quote": e(C.UI["quote_button"]),
        "a_brands": " is-active" if active == "brands" else "",
        "a_services": " is-active" if active == "services" else "",
        "a_company": " is-active" if active == "company" else "",
        "a_contact": " is-active" if active == "contact" else "",
    }


def footer_html():
    co = C.COMPANY
    pillars = "".join('<li><a href="/equipment/%s/">%s</a></li>' % (s, e(d["title"]))
                      for s, d in tax["pillars"].items())
    brands = "".join('<li><a href="/brands/%s/">%s</a></li>' % (b, e(BRANDS[b]["name"]))
                     for b in sorted(BRANDS, key=lambda x: BRANDS[x]["name"]))
    return """
<footer class="site-foot">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo logo-light" href="/">
        <img class="logo-mark" src="/assets/site/logo-mark.png" alt="" width="160" height="160" loading="lazy">
        <img class="logo-word" src="/assets/site/logo-word-light.png" alt="8BTSI Corp." width="543" height="88" loading="lazy">
      </a>
      <p class="foot-tag">%(tagline)s</p>
      <address>
        %(a1)s<br>%(a2)s<br>%(a3)s
      </address>
      <ul class="foot-contact">
        <li><a href="tel:%(tel)s">%(phone)s</a></li>
        <li><a href="mailto:%(email)s">%(email)s</a></li>
        <li><a href="mailto:%(support)s">%(support)s</a></li>
        <li>%(hours)s</li>
      </ul>
      <ul class="foot-social">
        <li><a href="%(fb)s" rel="noopener">Facebook</a></li>
        <li><a href="%(li)s" rel="noopener">LinkedIn</a></li>
      </ul>
    </div>
    <div class="foot-col">
      <h2>Equipment</h2>
      <ul>%(pillars)s</ul>
    </div>
    <div class="foot-col">
      <h2>Brands</h2>
      <ul class="two-col">%(brands)s</ul>
    </div>
    <div class="foot-col">
      <h2>Company</h2>
      <ul>
        <li><a href="/company/">Our company</a></li>
        <li><a href="/services/">Services</a></li>
        <li><a href="/contact/">Contact us</a></li>
        <li><a href="/contact/#quote">Request a quote</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap foot-base">
    <p>&copy; %(year)s %(name)s</p>
    <p>Pasig City, Philippines</p>
  </div>
</footer>""" % {
        "tagline": e(co["tagline"]), "a1": e(co["address_line1"]),
        "a2": e(co["address_line2"]), "a3": e(co["address_line3"]),
        "tel": e(co["phone_link"]), "phone": e(co["phone_display"]),
        "email": e(co["email"]), "support": e(co["support_email"]),
        "hours": e(co["hours"]), "fb": e(co["facebook"]), "li": e(co["linkedin"]),
        "pillars": pillars, "brands": brands, "year": "2026", "name": e(co["name"]),
    }


def page(title, desc, body, path, active="", jsonld=None, og_type="website", preload=""):
    canonical = SITE_URL + "/" + path.replace("index.html", "")
    canonical = canonical.rstrip("/") + "/" if path != "index.html" else SITE_URL + "/"
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld)
    return """<!doctype html>
<html lang="en-PH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(robots)s<link rel="canonical" href="%(canonical)s">
<meta property="og:site_name" content="8BTSI Corp.">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="%(ogtype)s">
<meta property="og:url" content="%(canonical)s">
<meta name="theme-color" content="#113C93">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/style.css%(css_v)s">
<link rel="icon" href="/assets/site/icon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/assets/site/icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="/assets/site/icon-180.png">
<link rel="shortcut icon" href="/assets/site/favicon.ico">
%(preload)s%(ld)s
</head>
<body>
%(nav)s
<main id="main">
%(body)s
</main>
%(foot)s
<script src="/site.js%(js_v)s" defer></script>
</body>
</html>
""" % {
        "title": e(title), "desc": e(desc), "canonical": e(canonical),
        "robots": '<meta name="robots" content="noindex, nofollow">\n' if NOINDEX else "",
        "preload": preload,
        "ogtype": og_type, "ld": ld, "nav": nav_html(active),
        "body": body, "foot": footer_html(),
        "css_v": CSS_V, "js_v": JS_V,
    }


# ------------------------------------------------------------- components
def product_card(slug):
    p = PRODUCTS[slug]
    b = BRAND_OF.get(slug)
    img = product_image(slug)
    if img:
        media = '<img src="%s" alt="%s" loading="lazy" width="480" height="360">' % (e(img), e(p["title"]))
    else:
        media = ('<img class="ph-mark" src="/assets/site/logo-mark.png" alt="" '
                 'width="160" height="160" loading="lazy">'
                 '<span class="ph-text">%s</span>' % e(C.UI["image_pending"]))
    line = p["excerpt"].split(".")[0].strip()
    if len(line) > 96:
        line = line[:93].rsplit(" ", 1)[0] + "..."
    haystack = " ".join([p["title"], brand_name(b) if b else ""]
                        + [slug_title(c) for c in CATS_OF.get(slug, [])]).lower()
    return """<a class="card" href="/products/%s/" data-find="%s">
  <span class="card-media%s">%s</span>
  <span class="card-body">
    %s
    <span class="card-title">%s</span>
    <span class="card-line">%s</span>
  </span>
</a>""" % (
        e(slug), e(haystack), "" if img else " is-placeholder", media,
        ('<span class="chip">%s</span>' % e(brand_name(b))) if b else "",
        e(p["title"]), e(line),
    )


def grid(slugs, cls="grid"):
    return '<div class="%s">%s</div>' % (cls, "".join(product_card(s) for s in slugs))


def breadcrumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            parts.append('<a href="%s">%s</a>' % (e(href), e(label)))
        else:
            parts.append('<span aria-current="page">%s</span>' % e(label))
    return '<nav class="crumb wrap" aria-label="Breadcrumb">%s</nav>' % (
        '<span class="sep" aria-hidden="true">/</span>'.join(parts))


def quote_form(product_name="", form_id="quote"):
    u = C.UI
    return """
<form class="quote-form" id="%(fid)s" name="quote" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="/thanks/">
  <input type="hidden" name="form-name" value="quote">
  <p class="hp"><label>Leave this empty <input name="bot-field"></label></p>
  <div class="field">
    <label for="q-name">%(name)s <span class="req">%(req)s</span></label>
    <input id="q-name" name="name" type="text" required autocomplete="name">
  </div>
  <div class="field">
    <label for="q-company">%(company)s <span class="req">%(req)s</span></label>
    <input id="q-company" name="company" type="text" required autocomplete="organization">
  </div>
  <div class="field">
    <label for="q-email">%(email)s <span class="req">%(req)s</span></label>
    <input id="q-email" name="email" type="email" required autocomplete="email">
  </div>
  <div class="field">
    <label for="q-phone">%(phone)s</label>
    <input id="q-phone" name="phone" type="tel" autocomplete="tel">
  </div>
  <div class="field">
    <label for="q-product">%(product)s</label>
    <input id="q-product" name="product" type="text" value="%(pval)s">
  </div>
  <div class="field field-wide">
    <label for="q-message">%(message)s</label>
    <textarea id="q-message" name="message" rows="5"></textarea>
  </div>
  <div class="field field-wide">
    <button class="btn" type="submit">%(submit)s</button>
  </div>
</form>""" % {
        "fid": e(form_id), "name": e(u["field_name"]), "company": e(u["field_company"]),
        "email": e(u["field_email"]), "phone": e(u["field_phone"]),
        "product": e(u["field_product"]), "message": e(u["field_message"]),
        "req": e(u["field_required"]), "submit": e(u["submit"]), "pval": e(product_name),
    }


def reach_block(product_name=""):
    """The quote section on a host that cannot accept a POST.

    Three ways to reach a person, in the order a buyer would use them. On a
    product page the email subject arrives with the product already in it.
    """
    co = C.COMPANY
    subject = "Quote request"
    if product_name:
        subject += ": " + product_name
    subject = urllib.parse.quote(subject)
    return """
<div class="reach-wrap">
<div class="reach">
  <a class="reach-item" href="tel:%(tel)s">
    <span>Call the office</span>
    <strong>%(phone)s</strong>
  </a>
  <a class="reach-item" href="mailto:%(email)s?subject=%(subject)s">
    <span>Quotes and enquiries</span>
    <strong>%(email)s</strong>
  </a>
  <a class="reach-item" href="mailto:%(support)s">
    <span>Equipment already installed</span>
    <strong>%(support)s</strong>
  </a>
</div>
<p class="reach-hours">%(hours)s</p>
</div>""" % {
        "tel": e(co["phone_link"]), "phone": e(co["phone_display"]),
        "email": e(co["email"]), "support": e(co["support_email"]),
        "hours": e(co["hours"]), "subject": subject,
    }


def quote_section(product_name=""):
    """Whichever of the two the current host can run."""
    return quote_form(product_name, "quote-form") if FORMS else reach_block(product_name)


def brand_mark(slug, name):
    """A logo on its own white tile, so brand colours stay right on a dark page."""
    logo = brand_logo(slug)
    if not logo:
        return ""
    return ('<span class="bmark"><img src="%s" alt="%s" loading="lazy"></span>'
            % (e(logo), e(name)))


def testimonials_band():
    if not TESTIMONIALS:
        return ""
    bg = site_image("testimonials.jpg")
    quotes = "".join("""
<figure class="quote%s">
  <blockquote>%s</blockquote>
  <figcaption><b>%s</b><span>%s</span></figcaption>
</figure>""" % (" on" if i == 0 else "", e(t["quote"]), e(t["name"]), e(t["role"]))
        for i, t in enumerate(TESTIMONIALS))
    dots = "".join('<button class="q-dot%s" type="button" aria-label="Quote %d"></button>'
                   % (" on" if i == 0 else "", i + 1) for i in range(len(TESTIMONIALS)))
    return """
<section class="testi%s" id="customers"%s>
  <div class="wrap testi-in">
    <div class="sec-head r">
      <p class="eyebrow">Customers</p>
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="quotes r" data-d="1">%s</div>
    <div class="q-dots">%s</div>
  </div>
</section>""" % (" has-bg" if bg else "",
                 (' style="background-image:url(%s)"' % e(bg)) if bg else "",
                 e(C.HOME["testi_h2"]), e(C.HOME["testi_sub"]), quotes, dots)


def stats_html(stats):
    """A figure counts up; a word like "Nationwide" is set smaller so it fits
    the box instead of running out of it."""
    out = []
    for s in stats:
        fig, label = s["figure"], s["label"]
        counts = fig.isdigit() and fig != "2006"
        out.append('<div class="stat"><strong class="%s"%s>%s</strong><span>%s</span></div>'
                   % ("stat-n" if fig.isdigit() else "stat-word",
                      ' data-count="%s"' % e(fig) if counts else "",
                      "0" if counts else e(fig), e(label)))
    return "".join(out)


def company_quotes():
    """All three quotes laid out to read, rather than rotating."""
    if not TESTIMONIALS:
        return ""
    items = "".join("""
<figure class="q-card r" data-d="%d">
  <blockquote>%s</blockquote>
  <figcaption><b>%s</b><span>%s</span></figcaption>
</figure>""" % (i + 1, e(t["quote"]), e(t["name"]), e(t["role"]))
        for i, t in enumerate(TESTIMONIALS))
    return """
<div class="q-cards" id="customers">
  <div class="cat-head"><h2>%s</h2></div>
  %s
</div>""" % (e(C.HOME["testi_h2"]), items)


def featured_band():
    """The three brand posters from the old home page, retyped."""
    tiles = []
    for i, f in enumerate(C.FEATURED):
        img = featured_image(f["brand"])
        if not img:
            continue
        meta = BRANDS.get(f["brand"])
        if not meta:
            continue
        tiles.append("""
<a class="feat r"%s href="/brands/%s/">
  <img src="%s" alt="%s equipment supplied by 8BTSI Corp" loading="lazy">
  <span class="feat-body">
    <i>%s</i>
    <strong>%s</strong>
    <span>%s</span>
    <em>%s %s</em>
  </span>
</a>""" % ('' if i == 0 else ' data-d="%d"' % i, e(f["brand"]), e(img), e(meta["name"]),
           e(f["line"]), e(meta["name"]), e(f["blurb"]), e(C.UI["view_all"]), ARROW))
    if not tiles:
        return ""
    return """
<section class="section">
  <div class="wrap">
    <div class="sec-head r">
      <p class="eyebrow">Featured</p>
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="feats">%s</div>
  </div>
</section>""" % (e(C.HOME["featured_h2"]), e(C.HOME["featured_sub"]), "".join(tiles))


def search_box(scope):
    """scope "all" searches the index, "page" narrows the cards already here."""
    return """
<div class="find" data-scope="%s" data-root="%s/" data-index="%s/search.json" data-none="%s" data-pending="%s">
  <label class="find-label" for="find">%s</label>
  <div class="find-field">
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M11 11l4 4" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>
    <input id="find" type="search" autocomplete="off" placeholder="%s">
    <button class="find-clear" type="button" aria-label="Clear" hidden>&times;</button>
  </div>
  <p class="find-count" role="status" aria-live="polite"></p>
  <div class="find-results grid" hidden></div>
</div>""" % (e(scope), e(BASE), e(BASE),
             e(C.UI["find_none"]), e(C.UI["image_pending"]),
             e(C.UI["find_label"]), e(C.UI["find_placeholder"]))


def build_search_index():
    """One small JSON file the equipment hub loads on the first keystroke."""
    rows = []
    for slug, p in PRODUCTS.items():
        b = BRAND_OF.get(slug)
        cats = [slug_title(c) for c in CATS_OF.get(slug, [])]
        line = p["excerpt"].split(".")[0].strip()
        if len(line) > 96:
            line = line[:93].rsplit(" ", 1)[0] + "..."
        rows.append({
            "s": slug,
            "t": p["title"],
            "b": brand_name(b) if b else "",
            "c": cats,
            "l": line,
        })
    rows.sort(key=lambda r: r["t"].lower())
    write("search.json", json.dumps(rows, separators=(",", ":")))


def cta_band():
    return """
<section class="band">
  <div class="wrap band-inner">
    <div>
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <a class="btn btn-light" href="/contact/#quote">%s</a>
  </div>
</section>""" % (e(C.HOME["cta_h2"]), e(C.HOME["cta_body"]), e(C.UI["quote_button"]))


# ------------------------------------------------------------------- pages
def build_home():
    pillars = "".join("""
<a class="pillar r"%s href="/equipment/%s/">
  <span class="pillar-n">%02d</span>
  <h3>%s</h3>
  <p>%s</p>
  <span class="pillar-count">%d products</span>
  <span class="pillar-go">%s</span>
</a>""" % ('' if i == 0 else ' data-d="%d"' % min(i, 5),
           s, i + 1, e(d["title"]), e(C.PILLARS[s]["card"]),
           len({x for c in d["categories"] for x in tax["categories"].get(c, [])}), ARROW)
        for i, (s, d) in enumerate(tax["pillars"].items()))

    services = "".join("""
<div class="svc r" data-d="%d">
  <span class="svc-n">%02d</span>
  <h3>%s</h3>
  <p>%s</p>
</div>""" % (i + 1, i + 1, e(s["title"]), e(s["body"])) for i, s in enumerate(C.SERVICES))

    brands = "".join(
        '<a class="brand-chip" href="/brands/%s/">%s<strong>%s</strong><span>%s</span></a>'
        % (b, brand_mark(b, BRANDS[b]["name"]), e(BRANDS[b]["name"]), e(BRANDS[b]["line"]))
        for b in sorted(BRANDS, key=lambda x: BRANDS[x]["name"]))

    # Only the first slide is a real img. The other two are absolutely
    # positioned over the viewport, so loading="lazy" would not defer them:
    # the browser treats anything inside the viewport as needed now. They carry
    # their source in data-src and site.js swaps it in after load instead.
    slides = "".join(
        ('<div class="slide on"><img src="%s" srcset="%s" sizes="100vw" alt="%s" '
         'fetchpriority="high" width="1920" height="1080"></div>'
         % (e(s["src"]), e(photo_srcset(s["id"])), e(s["alt"]))
         if i == 0 else
         '<div class="slide"><img data-src="%s" data-srcset="%s" sizes="100vw" alt="%s" '
         'width="1920" height="1080"></div>'
         % (e(s["src"]), e(photo_srcset(s["id"])), e(s["alt"])))
        for i, s in enumerate(SCENES))

    first = SCENES[0]
    preload = ('<link rel="preload" as="image" href="%s" imagesrcset="%s" '
               'imagesizes="100vw" fetchpriority="high">\n'
               % (e(first["src"]), e(photo_srcset(first["id"]))))

    # The first gallery photograph is the one already in the hero, so it costs
    # nothing. The other two wait until the gallery is nearly in view, because
    # loading="lazy" fires about 1250px early and that is closer than this
    # section sits on a phone.
    gallery = "".join("""
<div class="gal-item">
  <img %s="%s" %s="%s" sizes="100vw" alt="%s" width="1920" height="840">
  <div class="gal-cap">
    <i>%s</i>
    <h3>%s</h3>
    <p>%s</p>
  </div>
</div>""" % ("src" if i == 0 else "data-src", e(s["src"]),
             "srcset" if i == 0 else "data-srcset", e(photo_srcset(s["id"])),
             e(s["alt"]), e(s["label"]), e(s["head"]), e(s["body"]))
        for i, s in enumerate(SCENES))

    ticker_bits = [C.COMPANY["tagline"]] + [d["title"] for d in tax["pillars"].values()]
    ticker_bits.append("Nationwide installation")
    ticker = "".join("<span>%s</span>" % e(t) for t in ticker_bits)

    n_products, n_brands = len(PRODUCTS), len(BRANDS)
    stats = stats_html(C.COMPANY_PAGE["stats"])

    credits = "\n".join("     %s: %s" % (s["label"], s["credit"]) for s in SCENES)

    body = """
<!-- Photographs on this page, from Unsplash under the Unsplash licence.
%(credits)s
-->
<section class="hero">
  <div class="hero-bg">%(slides)s</div>
  <div class="hero-rule" aria-hidden="true"></div>
  <div class="wrap hero-inner">
    <p class="onair r">%(eyebrow)s</p>
    <h1 class="r" data-d="1">%(h1)s</h1>
    <div class="hero-row r" data-d="2">
      <p class="lede">%(sub)s</p>
      <div class="hero-cta">
        <a class="btn" href="/equipment/rf-transmission/">%(cta1)s</a>
        <a class="btn btn-ghost" href="/contact/#quote">%(cta2)s</a>
      </div>
    </div>
    <div class="hero-dots r" data-d="3"></div>
  </div>
  <div class="scroll-cue" aria-hidden="true">Scroll<i></i></div>
</section>

<div class="ticker"><div class="tick-track">%(ticker)s</div></div>

<section class="section">
  <div class="wrap">
    <div class="sec-head r">
      <p class="eyebrow">Equipment</p>
      <h2>%(ph2)s</h2>
      <p>%(psub)s</p>
    </div>
    <div class="pillars">%(pillars)s</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="gal r">
      <div class="gal-view">%(gallery)s</div>
      <div class="gal-ctl">
        <span class="gal-i"><b>01</b> / %(gn)02d</span>
        <div class="gal-bar"><b></b></div>
        <button class="gal-btn gal-prev" type="button" aria-label="Previous"><svg width="16" height="12" viewBox="0 0 16 12" aria-hidden="true"><path d="M6 1L1 6l5 5M1 6h14" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>
        <button class="gal-btn gal-next" type="button" aria-label="Next"><svg width="16" height="12" viewBox="0 0 16 12" aria-hidden="true"><path d="M10 1l5 5-5 5M15 6H1" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>
      </div>
    </div>
  </div>
</section>

%(featured)s

%(testimonials)s

<section class="section slab">
  <div class="wrap">
    <div class="sec-head r">
      <p class="eyebrow">Services</p>
      <h2>%(sh2)s</h2>
      <p>%(ssub)s</p>
    </div>
    <div class="svc-grid">%(services)s</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head r">
      <p class="eyebrow">Company</p>
      <h2>%(ch2)s</h2>
      <p>%(csub)s</p>
    </div>
    <div class="stats r" data-d="1">%(stats)s</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="sec-head r">
      <p class="eyebrow">Brands</p>
      <h2>%(bh2)s</h2>
      <p>%(bsub)s</p>
    </div>
    <div class="brand-strip r" data-d="1">%(brands)s</div>
  </div>
</section>
%(cta)s
""" % {
        "credits": credits,
        "featured": featured_band(), "testimonials": testimonials_band(),
        "slides": slides, "ticker": ticker, "gallery": gallery, "gn": len(SCENES),
        "eyebrow": e(C.HOME["hero_eyebrow"]), "h1": e(C.HOME["hero_h1"]),
        "sub": e(C.HOME["hero_sub"]), "cta1": e(C.HOME["hero_cta_primary"]),
        "cta2": e(C.HOME["hero_cta_secondary"]),
        "ph2": e(C.HOME["pillars_h2"]), "psub": e(C.HOME["pillars_sub"]),
        "pillars": pillars,
        "sh2": e(C.HOME["services_h2"]), "ssub": e(C.HOME["services_sub"]),
        "services": services,
        "ch2": e(C.COMPANY_PAGE["lead"]), "csub": e(C.COMPANY_PAGE["body"][0]),
        "stats": stats,
        "bh2": e(C.HOME["brands_h2"]), "bsub": e(C.HOME["brands_sub"]),
        "brands": brands, "cta": cta_band(),
    }

    co = C.COMPANY
    ld = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": co["name"], "url": SITE_URL, "foundingDate": "2006-11",
        "email": co["email"], "telephone": co["phone_display"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": co["address_line1"] + ", " + co["address_line2"],
            "addressLocality": "Pasig City", "addressRegion": "Metro Manila",
            "postalCode": "1609", "addressCountry": "PH",
        },
        "sameAs": [co["facebook"], co["linkedin"]],
    }
    write("index.html", page(
        "8BTSI Corp. | Broadcast transmission and studio equipment, Philippines",
        C.HOME["hero_sub"], body, "index.html", "home", ld, preload=preload))


def build_pillars():
    for slug, d in tax["pillars"].items():
        meta = C.PILLARS[slug]
        sections = []
        seen = set()
        for cat in d["categories"]:
            slugs = [s for s in tax["categories"].get(cat, []) if s in PRODUCTS]
            if not slugs:
                continue
            seen.update(slugs)
            sections.append("""
<section class="cat-block" id="%s">
  <div class="cat-head">
    <h2>%s</h2>
    <span class="count">%d</span>
  </div>
  %s
</section>""" % (e(cat), e(slug_title(cat)), len(slugs), grid(slugs)))

        jump = "".join('<a href="#%s">%s</a>' % (e(c), e(slug_title(c)))
                       for c in d["categories"] if tax["categories"].get(c))

        body = """
%(crumb)s
<section class="wrap page-head">
  <p class="eyebrow">Equipment</p>
  <h1>%(title)s</h1>
  <p class="lede">%(intro)s</p>
  <nav class="jump" aria-label="Categories">%(jump)s</nav>
</section>
<div class="slab"><div class="wrap slab-body">%(find)s%(sections)s</div></div>
%(cta)s
""" % {
            "crumb": breadcrumb([("Home", "/"), ("Equipment", None), (meta["title"], None)]),
            "title": e(meta["title"]), "intro": e(meta["intro"]),
            "jump": jump, "find": search_box("page"),
            "sections": "".join(sections), "cta": cta_band(),
        }
        write("equipment/%s/index.html" % slug, page(
            "%s | 8BTSI Corp." % meta["title"], meta["meta"], body,
            "equipment/%s/index.html" % slug, "equipment"))

    # equipment index redirects into the first pillar via a simple hub page
    cards = "".join("""
<a class="pillar r"%s href="/equipment/%s/">
  <span class="pillar-n">%02d</span>
  <h3>%s</h3>
  <p>%s</p>
  <span class="pillar-count">%d products</span>
  <span class="pillar-go">%s</span>
</a>""" % ('' if i == 0 else ' data-d="%d"' % min(i, 5), s, i + 1,
           e(d["title"]), e(C.PILLARS[s]["card"]),
           len({x for c in d["categories"] for x in tax["categories"].get(c, [])}), ARROW)
        for i, (s, d) in enumerate(tax["pillars"].items()))
    body = """
%s
<section class="wrap page-head">
  <p class="eyebrow">Equipment</p>
  <h1>All equipment</h1>
  <p class="lede">%s</p>
</section>
<div class="slab"><div class="wrap slab-body">%s</div></div>
<div class="wrap slab-body"><div class="pillars">%s</div></div>
%s""" % (breadcrumb([("Home", "/"), ("Equipment", None)]),
         e(C.HOME["pillars_sub"]), search_box("all"), cards, cta_band())
    write("equipment/index.html", page(
        "Equipment | 8BTSI Corp.",
        "Transmission, playout, studio audio and IP codec equipment supplied in the Philippines by 8BTSI Corp.",
        body, "equipment/index.html", "equipment"))


def build_brands():
    order = sorted(BRANDS, key=lambda x: BRANDS[x]["name"])
    cards = "".join("""
<a class="brand-card" href="/brands/%s/">
  %s
  <h3>%s</h3>
  <p class="brand-line">%s</p>
  <p class="brand-meta">%d products</p>
</a>""" % (b, brand_mark(b, BRANDS[b]["name"]), e(BRANDS[b]["name"]), e(BRANDS[b]["line"]),
           len([s for s in tax["brands"].get(b, []) if s in PRODUCTS])) for b in order)

    body = """
%s
<section class="wrap page-head">
  <p class="eyebrow">Brands</p>
  <h1>Brands we represent</h1>
  <p class="lede">%s</p>
</section>
<div class="wrap slab-body"><div class="brand-grid r">%s</div></div>
%s""" % (breadcrumb([("Home", "/"), ("Brands", None)]), e(C.HOME["brands_sub"]),
         cards, cta_band())
    write("brands/index.html", page(
        "Brands | 8BTSI Corp.", C.HOME["brands_sub"], body, "brands/index.html", "brands"))

    for b in order:
        meta = BRANDS[b]
        slugs = [s for s in tax["brands"].get(b, []) if s in PRODUCTS]
        body = """
%(crumb)s
<section class="wrap page-head">
  %(mark)s
  <p class="eyebrow">%(line)s</p>
  <h1>%(name)s</h1>
  <p class="lede">%(blurb)s</p>
</section>
<div class="slab"><div class="wrap slab-body">
  <div class="cat-head"><h2>%(products_in)s %(name)s</h2><span class="count">%(n)d</span></div>
  %(find)s
  %(grid)s
</div></div>
%(cta)s""" % {
            "crumb": breadcrumb([("Home", "/"), ("Brands", "/brands/"), (meta["name"], None)]),
            "line": e(meta["line"]), "mark": brand_mark(b, meta["name"]),
            "name": e(meta["name"]), "blurb": e(meta["blurb"]),
            "products_in": e(C.UI["products_in"]), "n": len(slugs),
            "find": search_box("page") if len(slugs) > 6 else "",
            "grid": grid(slugs), "cta": cta_band(),
        }
        write("brands/%s/index.html" % b, page(
            "%s | 8BTSI Corp." % meta["name"],
            "%s %s supplied and supported in the Philippines by 8BTSI Corp."
            % (meta["name"], meta["line"].lower()),
            body, "brands/%s/index.html" % b, "brands"))


def build_products():
    for slug, p in PRODUCTS.items():
        b = BRAND_OF.get(slug)
        cats = CATS_OF.get(slug, [])
        pillar = next((PILLAR_OF_CAT[c] for c in cats if c in PILLAR_OF_CAT), None)
        paras, features, faq = clean_body(p["body"], p["title"], p["excerpt"])

        img = product_image(slug)
        if img:
            media = '<img src="%s" alt="%s" width="900" height="675">' % (e(img), e(p["title"]))
            media_cls = ""
        else:
            media = ('<div class="ph-big">'
                     '<img class="ph-mark" src="/assets/site/logo-mark.png" alt="" '
                     'width="160" height="160">'
                     '<span class="ph-text">%s</span></div>' % e(C.UI["image_pending"]))
            media_cls = " is-placeholder"

        feat_html = ""
        if features:
            feat_html = '<h2>%s</h2><ul class="features">%s</ul>' % (
                e(C.UI["spec_heading"]),
                "".join("<li>%s</li>" % e(f) for f in features))

        faq_html = ""
        if faq:
            faq_html = '<h2>%s</h2><ul class="faqs">%s</ul>' % (
                e(C.UI["faq_heading"]), "".join("<li>%s</li>" % e(f) for f in faq))

        body_html = "".join("<p>%s</p>" % e(x) for x in paras)

        siblings = [s for s in (tax["brands"].get(b) or []) if s in PRODUCTS and s != slug][:4]
        related = ""
        if siblings:
            related = """
<div class="slab"><section class="wrap slab-body">
  <div class="cat-head"><h2>%s %s</h2></div>
  %s
</section></div>""" % (e(C.UI["related"]), e(brand_name(b)), grid(siblings))

        cat_links = " ".join(
            '<a class="tag" href="/equipment/%s/#%s">%s</a>'
            % (e(PILLAR_OF_CAT.get(c, "")), e(c), e(slug_title(c)))
            for c in cats if c in PILLAR_OF_CAT)

        crumb = [("Home", "/"), ("Equipment", "/equipment/")]
        if pillar:
            crumb.append((tax["pillars"][pillar]["title"], "/equipment/%s/" % pillar))
        crumb.append((p["title"], None))

        body = """
%(crumb)s
<article class="wrap product">
  <div class="product-media%(media_cls)s">%(media)s</div>
  <div class="product-main">
    %(chip)s
    <h1>%(title)s</h1>
    <p class="lede">%(excerpt)s</p>
    <div class="tags">%(tags)s</div>
    <a class="btn" href="#quote">%(quote)s</a>
  </div>
</article>
<div class="slab"><div class="wrap slab-body narrow">
  <div class="prose">
    %(body)s
    %(features)s
    %(faq)s
  </div>
</div></div>
<section class="section slab slab-alt" id="quote">
  <div class="wrap form-wrap">
    <div class="form-intro">
      <h2>%(qh)s</h2>
      <p>%(qi)s</p>
      %(note)s
    </div>
    %(form)s
  </div>
</section>
%(related)s
""" % {
            "crumb": breadcrumb(crumb), "media": media, "media_cls": media_cls,
            "chip": ('<a class="chip chip-link" href="/brands/%s/">%s</a>' % (e(b), e(brand_name(b)))) if b else "",
            "title": e(p["title"]), "excerpt": e(p["excerpt"]),
            "tags": cat_links, "quote": e(C.UI["quote_button"]),
            "body": body_html, "features": feat_html, "faq": faq_html,
            "qh": e(C.UI["quote_heading"]),
            "qi": e(C.UI["quote_intro"] if FORMS else C.UI["quote_intro_direct"]),
            "note": ('<p class="muted">%s</p>' % e(C.CONTACT_PAGE["form_note"])) if FORMS else "",
            "form": quote_section(p["title"]),
            "related": related,
        }

        desc = p["excerpt"][:155].rsplit(" ", 1)[0]
        ld = {
            "@context": "https://schema.org", "@type": "Product",
            "name": p["title"], "description": p["excerpt"][:400],
            "brand": {"@type": "Brand", "name": brand_name(b)} if b else None,
            "url": SITE_URL + "/products/%s/" % slug,
        }
        ld = {k: v for k, v in ld.items() if v is not None}
        write("products/%s/index.html" % slug, page(
            "%s | 8BTSI Corp." % p["title"], desc, body,
            "products/%s/index.html" % slug, "equipment", ld, "product"))


def build_static_pages():
    cp = C.COMPANY_PAGE
    stats = stats_html(cp["stats"])
    body = """
%s
<section class="wrap page-head">
  <p class="eyebrow">Company</p>
  <h1>%s</h1>
  <p class="lede">%s</p>
</section>
<div class="slab"><div class="wrap slab-body">
  <div class="narrow prose r">%s</div>
  <div class="stats r" data-d="1">%s</div>
  %s
</div></div>
%s""" % (breadcrumb([("Home", "/"), ("Company", None)]), e(cp["h1"]), e(cp["lead"]),
         "".join("<p>%s</p>" % e(x) for x in cp["body"]), stats,
         company_quotes(), cta_band())
    write("company/index.html", page(
        "Our company | 8BTSI Corp.",
        "8BTSI Corp has supplied and installed broadcast equipment for Philippine radio and television since November 2006.",
        body, "company/index.html", "company"))

    services = "".join("""
<div class="svc svc-lg r" data-d="%d">
  <span class="svc-n">%02d</span>
  <h2>%s</h2>
  <p>%s</p>
</div>""" % (i + 1, i + 1, e(s["title"]), e(s["body"])) for i, s in enumerate(C.SERVICES))
    body = """
%s
<section class="wrap page-head">
  <p class="eyebrow">Services</p>
  <h1>%s</h1>
  <p class="lede">%s</p>
</section>
<div class="slab"><div class="wrap slab-body"><div class="svc-grid">%s</div></div></div>
%s""" % (breadcrumb([("Home", "/"), ("Services", None)]), e(C.HOME["services_h2"]),
         e(C.HOME["services_sub"]), services, cta_band())
    write("services/index.html", page(
        "Services | 8BTSI Corp.",
        "Project management, engineering services, installation and wiring, and product training for Philippine broadcast stations.",
        body, "services/index.html", "services"))

    co = C.COMPANY
    ct = C.CONTACT_PAGE
    body = """
%(crumb)s
<section class="wrap page-head">
  <p class="eyebrow">Contact</p>
  <h1>%(h1)s</h1>
  <p class="lede">%(lead)s</p>
</section>
<div class="slab"><div class="wrap contact-grid slab-body">
  <div class="contact-details">
    <h2>Office</h2>
    <address>%(a1)s<br>%(a2)s<br>%(a3)s</address>
    %(dl)s
    <h2>Social</h2>
    <ul class="plain">
      <li><a href="%(fb)s" rel="noopener">Facebook</a></li>
      <li><a href="%(li)s" rel="noopener">LinkedIn</a></li>
    </ul>
  </div>
  <div class="contact-form" id="quote">
    <h2>%(qh)s</h2>
    <p>%(qi)s</p>
    %(note)s
    %(form)s
  </div>
</div></div>
""" % {
        "crumb": breadcrumb([("Home", "/"), ("Contact", None)]),
        "h1": e(ct["h1"]), "lead": e(ct["lead"]),
        "a1": e(co["address_line1"]), "a2": e(co["address_line2"]), "a3": e(co["address_line3"]),
        "fb": e(co["facebook"]), "li": e(co["linkedin"]),
        "dl": ("""<dl>
      <dt>Office line</dt><dd><a href="tel:%s">%s</a></dd>
      <dt>Enquiries</dt><dd><a href="mailto:%s">%s</a></dd>
      <dt>Support</dt><dd><a href="mailto:%s">%s</a></dd>
      <dt>Hours</dt><dd>%s</dd>
    </dl>""" % (e(co["phone_link"]), e(co["phone_display"]), e(co["email"]), e(co["email"]),
                e(co["support_email"]), e(co["support_email"]), e(co["hours"]))) if FORMS else "",
        "qh": e(C.UI["quote_heading"]),
        "qi": e(C.UI["quote_intro"] if FORMS else C.UI["quote_intro_direct"]),
        "note": ('<p class="muted">%s</p>' % e(ct["form_note"])) if FORMS else "",
        "form": quote_section(),
    }
    write("contact/index.html", page(
        "Contact us | 8BTSI Corp.",
        "Office in Pasig City, Metro Manila. Call 02 275 4035 or send a quote request to 8BTSI Corp.",
        body, "contact/index.html", "contact"))

    if FORMS:
        body = """
<section class="wrap page-head narrow-head">
  <h1>%s</h1>
  <p class="lede">%s</p>
  <a class="btn" href="/">Back to home</a>
</section>""" % (e(C.UI["thanks_h1"]), e(C.UI["thanks_body"]))
        write("thanks/index.html", page("Request received | 8BTSI Corp.",
                                        C.UI["thanks_body"], body, "thanks/index.html"))

    body = """
<section class="wrap page-head narrow-head">
  <h1>%s</h1>
  <p class="lede">%s</p>
  <a class="btn" href="/equipment/">All equipment</a>
</section>""" % (e(C.UI["notfound_h1"]), e(C.UI["notfound_body"]))
    write("404.html", page("Page not found | 8BTSI Corp.",
                           C.UI["notfound_body"], body, "404.html"))


def build_meta_files():
    urls = ["/"]
    urls += ["/equipment/"] + ["/equipment/%s/" % s for s in tax["pillars"]]
    urls += ["/brands/"] + ["/brands/%s/" % b for b in BRANDS]
    urls += ["/products/%s/" % s for s in PRODUCTS]
    urls += ["/company/", "/services/", "/contact/"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("  <url><loc>%s%s</loc></url>" % (SITE_URL, u))
    sm.append("</urlset>")
    write("favicon.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="10" fill="#113C93"/>
<text x="32" y="45" font-family="Montserrat,Arial,sans-serif" font-size="38" font-weight="700"
 fill="#ffffff" text-anchor="middle">8</text></svg>""")

    build_search_index()

    if TARGET == "pages":
        # A preview, so it stays out of search results and out of the way of
        # btsi.com.ph. The empty .nojekyll stops Pages running the build
        # through Jekyll, which would drop any path beginning with an
        # underscore.
        write("robots.txt", "User-agent: *\nDisallow: /\n")
        write(".nojekyll", "")
        return

    write("sitemap.xml", "\n".join(sm))
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    write("netlify.toml", '[build]\n  publish = "."\n  command = ""\n')

    # Keep every URL the old WordPress site earned. One line per old address.
    lines = [
        "# Old WordPress addresses, kept so search results and bookmarks still land.",
        "/our-company/            /company/     301!",
        "/contact-us/             /contact/     301!",
        "/news/                   /             301!",
        "/news/*                  /             301!",
    ]
    # The addresses these products had on the old WordPress site, kept in
    # archive/old-urls.json rather than on the product records: it is a fact
    # about 2018, not something anyone should be shown a form field for. A
    # product added since then has no old address and needs no redirect.
    old_urls = {}
    old_path = os.path.join(ROOT, "archive", "old-urls.json")
    if os.path.exists(old_path):
        with open(old_path, encoding="utf-8") as f:
            old_urls = json.load(f)
    for slug in PRODUCTS:
        if slug in old_urls:
            lines.append("%-24s /products/%s/  301!" % (old_urls[slug], slug))
    for cat in tax["categories"]:
        pillar = PILLAR_OF_CAT.get(cat)
        if pillar:
            lines.append("%-24s /equipment/%s/#%s  301!"
                         % ("/product-category/%s/" % cat, pillar, cat))
    for b in BRANDS:
        lines.append("%-24s /brands/%s/  301!" % ("/product-category/%s/" % b, b))
    lines += [
        "/product-category/*      /equipment/   301",
        "/shop/*                  /equipment/   301",
    ]
    write("_redirects", "\n".join(lines) + "\n")
    write("_headers", """/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/style.css
  Cache-Control: public, max-age=31536000, immutable

/site.js
  Cache-Control: public, max-age=31536000, immutable
""")


def copy_assets():
    for name in ("style.css", "site.js"):
        src = os.path.join(ROOT, "src", name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(DIST, name))
    if os.path.isdir(ASSETS_SRC):
        dest = os.path.join(DIST, "assets")
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(ASSETS_SRC, dest)


def build_admin():
    """The editor, and the configuration that tells it what the fields are.

    The manufacturer and category dropdowns are written from the real data, so
    a category added to taxonomy.json or a manufacturer added to data/brands
    turns up in the form on the next build. There is no second list to keep in
    step, which is the whole point of the exercise.
    """
    src = os.path.join(ROOT, "src", "admin", "index.html")
    if not os.path.exists(src):
        return
    dest = os.path.join(DIST, "admin")
    os.makedirs(dest, exist_ok=True)
    shutil.copy(src, os.path.join(dest, "index.html"))

    def q(s):
        return '"%s"' % str(s).replace("\\", "\\\\").replace('"', '\\"')

    def options(pairs, indent):
        pad = " " * indent
        return "\n".join("%s- { label: %s, value: %s }" % (pad, q(label), q(value))
                         for value, label in pairs)

    brand_opts = options(sorted(((s, b["name"]) for s, b in BRANDS.items()),
                                key=lambda x: x[1].lower()), 10)
    cat_opts = options(sorted(((c, slug_title(c)) for c in PILLAR_OF_CAT),
                              key=lambda x: x[1].lower()), 10)

    media = "%s/assets" % BASE if BASE else "/assets"

    write("admin/config.yml", """# Written by build.py. Editing this file by hand achieves nothing: the next
# build overwrites it. The dropdowns come from data/brands and taxonomy.json.
backend:
  name: github
  repo: %(repo)s
  branch: main

# Where an uploaded picture is written in the repository, and the path that
# gets stored in the entry. build.py strips the %(base)s prefix back off when it
# reads the value, so this stays right if the site moves to its own domain.
media_folder: /assets/products
public_folder: %(media)s/products

media_libraries:
  all:
    slugify_filename: true

collections:
  - name: products
    label: Products
    label_singular: Product
    icon: inventory_2
    description: >-
      Everything in the catalogue. Press **New Product** to add one. It is on
      the site about two minutes after you save.
    folder: /data/products
    format: json
    extension: json
    create: true
    duplicate: false
    identifier_field: title
    slug: "{{title}}"
    summary: "{{title}}"
    thumbnail: photo
    sortable_fields:
      fields: [title, brand]
      default:
        field: title
        direction: ascending
    fields:
      - name: title
        label: Product name
        widget: string
        hint: >-
          The full name as it should read, including the manufacturer, as in
          Elenos Indium 2000. It becomes the web address of the page, so
          changing it later breaks any link anyone had to the old one.
      - name: brand
        label: Manufacturer
        widget: select
        hint: >-
          Not on the list? Add it under Manufacturers first, then come back.
        options:
%(brands)s
      - name: categories
        label: Categories
        widget: select
        multiple: true
        min: 1
        hint: >-
          At least one. The product appears on the page of every category you
          tick.
        options:
%(cats)s
      - name: photo
        label: Photograph
        widget: image
        required: false
        hint: >-
          About 1200 pixels wide. Leave it empty and the card shows a grey
          panel saying the photograph is to follow.
      - name: excerpt
        label: One line summary
        widget: text
        hint: >-
          One or two sentences. This is what shows on the product card, in the
          search box, and in the preview when someone shares the page.
      - name: body
        label: Full description
        widget: text
        required: false
        hint: >-
          The long text on the product page. Leave a blank line between
          paragraphs. A line reading `Features:` turns everything under it
          into a list.

  - divider: true

  - name: brands
    label: Manufacturers
    label_singular: Manufacturer
    icon: factory
    description: >-
      The manufacturers whose equipment you sell. Add one here before adding
      its products.
    folder: /data/brands
    format: json
    extension: json
    create: true
    duplicate: false
    identifier_field: name
    slug: "{{name}}"
    summary: "{{name}}"
    thumbnail: logo
    sortable_fields:
      fields: [name]
      default:
        field: name
        direction: ascending
    fields:
      - name: name
        label: Manufacturer name
        widget: string
        hint: As it should appear, as in Telos Alliance.
      - name: line
        label: One line summary
        widget: string
        hint: >-
          What they make, in a few words, as in FM transmitters, exciters and
          remote control. It sits under the name on the manufacturers page.
      - name: blurb
        label: Description
        widget: text
        hint: A paragraph for the top of their page.
      - name: logo
        label: Logo
        widget: image
        required: false
        hint: >-
          A PNG with a transparent background or a JPEG on white both work,
          since it sits on a white tile. Without one the tile shows the name
          as text.
        media_folder: /assets/brands
        public_folder: %(media)s/brands

  - divider: true

  - name: testimonials
    label: Testimonials
    label_singular: Testimonial
    icon: format_quote
    description: >-
      What customers have said. These rotate on the home page and are listed
      on the Company page.
    folder: /data/testimonials
    format: json
    extension: json
    create: true
    duplicate: false
    identifier_field: name
    slug: "{{name}}"
    summary: "{{name}}, {{role}}"
    fields:
      - name: quote
        label: What they said
        widget: text
        hint: >-
          Their words, unedited. Tidying a quote misquotes the person who gave
          it.
      - name: name
        label: Their name
        widget: string
      - name: role
        label: Job title and company
        widget: string
        hint: As in President and CEO, Eight TriMedia Pro, Inc.
""" % {"repo": "%s/%s" % (GH_USER, REPO), "media": media, "base": BASE or "(none)",
       "brands": brand_opts, "cats": cat_opts})


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    build_home()
    build_pillars()
    build_brands()
    build_products()
    build_static_pages()
    build_meta_files()
    build_admin()
    copy_assets()

    n = sum(len(files) for _, _, files in os.walk(DIST))
    print("built %d files into dist/" % n)
    print("  %d products, %d brands, %d pillars, %d categories"
          % (len(PRODUCTS), len(BRANDS), len(tax["pillars"]), len(tax["categories"])))
    missing = [s for s in PRODUCTS if not product_image(s)]
    print("  %d products still need a photograph" % len(missing))


if __name__ == "__main__":
    main()
