# -*- coding: utf-8 -*-
"""One-off: turn the scraped catalogue into files a person can edit.

catalogue.json is a 106 entry array with the scrape's own fields still in it,
and taxonomy.json holds the brand and category membership as lists of slugs
somewhere else again. Adding a product therefore meant editing three places and
knowing which. This writes one file per product, per brand and per testimonial,
with each product carrying its own brand and categories, so adding one is
adding a file.

Run once. After that the files under data/ are the source and this script and
catalogue.json are history.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

sys.path.insert(0, ROOT)
import content as C  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


# The same two cleaning passes build.py has always run on import, applied once
# here instead so that what the editor sees in the form is what the page says.
def straighten(s):
    return (s.replace("‘", "'").replace("’", "'")
             .replace("“", '"').replace("”", '"'))


def dedash(s):
    s = re.sub(r"\s*[–—]\s*(?=[A-Z][a-z]{2,}\s)", ". ", s)
    s = re.sub(r"\s*[–—]\s*", ", ", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"\s+([,.])", r"\1", s)
    return straighten(s)


def clean_title(t):
    t = re.sub(r"(\d[\w.]*)\s*[–—]\s*(?=\d)", r"\1 to ", t)
    t = re.sub(r"\s*[–—]\s*", " ", t)
    t = t.replace(" & ", " and ")
    return straighten(re.sub(r"\s+", " ", t).strip())


# The old theme printed its quote form and its gallery instructions into the
# body text, and every scraped description still ends with "Request A Quote,
# Name (required), Company (required)". build.py has always cut these two
# before rendering, so cutting them here changes no page. It changes what the
# editor is shown in the form, which is the point: nobody should have to look
# at a dead form from the 2018 site to fix a typo in a description.
QUOTE_BOILERPLATE = re.compile(r"×?\s*Request A Quote.*$", re.S | re.I)
GALLERY_BOILERPLATE = re.compile(
    r"Click on the (left or right arrow button|image).*?(\.pdf|another image)\.?", re.S | re.I)


def clean_stored_body(raw):
    t = QUOTE_BOILERPLATE.sub("", raw or "")
    t = GALLERY_BOILERPLATE.sub("", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def photo_for(slug):
    for ext in ("jpg", "jpeg", "png", "webp"):
        if os.path.exists(os.path.join(ROOT, "assets", "products", "%s.%s" % (slug, ext))):
            return "/assets/products/%s.%s" % (slug, ext)
    return ""


def logo_for(slug):
    for ext in ("jpg", "png", "webp"):
        if os.path.exists(os.path.join(ROOT, "assets", "brands", "%s.%s" % (slug, ext))):
            return "/assets/brands/%s.%s" % (slug, ext)
    return ""


def main():
    catalogue = load("catalogue.json")
    tax = load("taxonomy.json")

    # build.py has carried these three corrections to the scrape since the
    # first build. They belong in the data now, not in the code that reads it.
    tax["brands"].setdefault("playbox", [])
    if "productionairbox" not in tax["brands"]["playbox"]:
        tax["brands"]["playbox"].append("productionairbox")
    if "productionairbox" not in tax["categories"]["tv-automation"]:
        tax["categories"]["tv-automation"].append("productionairbox")
    for slug, brand in {
        "routing-control-panels": "axia", "softsurface": "axia",
        "studio-control-panels": "axia", "studioengine": "axia",
        "xselector": "axia", "xnodes": "telos", "xswitch": "telos",
    }.items():
        if slug not in tax["brands"][brand]:
            tax["brands"][brand].append(slug)

    brand_of = {}
    for b, slugs in tax["brands"].items():
        for s in slugs:
            brand_of.setdefault(s, b)
    cats_of = {}
    for c, slugs in tax["categories"].items():
        for s in slugs:
            cats_of.setdefault(s, []).append(c)

    if os.path.isdir(DATA):
        shutil.rmtree(DATA)

    problems = []

    # ---------------------------------------------------------- products
    seen = set()
    for p in catalogue:
        slug = p["slug"]
        if slug in seen:
            problems.append("duplicate slug in catalogue.json: %s" % slug)
            continue
        seen.add(slug)

        brand = brand_of.get(slug, "")
        if not brand:
            problems.append("%s has no brand" % slug)
        # The scrape's own "category" field is whichever term WordPress
        # happened to call primary, so for 51 of the 106 it is a category and
        # for the other 55 a brand. taxonomy.json is what build.py has always
        # believed, so that is what carries over. Only a value that is neither
        # means the scrape has drifted from the taxonomy.
        c = p.get("category", "")
        if c and c not in tax["brands"] and c not in tax["categories"]:
            problems.append("%s: catalogue's %r is neither a brand nor a category" % (slug, c))

        cats = cats_of.get(slug, [])
        if not cats:
            problems.append("%s is in no category, so nothing links to it" % slug)

        write(os.path.join(DATA, "products", slug + ".json"), {
            "title": clean_title(p["title"]),
            "brand": brand,
            "categories": cats,
            "photo": photo_for(slug),
            "excerpt": dedash(re.sub(r"\s+", " ", p["excerpt"]).strip()),
            "body": clean_stored_body(p["body"]),
        })

    # ------------------------------------------------------------ brands
    for slug, b in C.BRANDS.items():
        if slug not in tax["brands"]:
            problems.append("brand %s is described in content.py but absent from taxonomy.json" % slug)
        write(os.path.join(DATA, "brands", slug + ".json"), {
            "name": b["name"],
            "line": b["line"],
            "blurb": b["blurb"],
            "logo": logo_for(slug),
        })
    for slug in tax["brands"]:
        if slug not in C.BRANDS:
            problems.append("brand %s is in taxonomy.json but has no description" % slug)

    # ------------------------------------------------------ testimonials
    for i, t in enumerate(C.TESTIMONIALS, 1):
        write(os.path.join(DATA, "testimonials", "%02d.json" % i), {
            "quote": t["quote"], "name": t["name"], "role": t["role"],
        })

    n = lambda d: len(os.listdir(os.path.join(DATA, d)))
    print("wrote %d products, %d brands, %d testimonials into data/"
          % (n("products"), n("brands"), n("testimonials")))
    print("%d of %d products have a photograph"
          % (sum(1 for f in os.listdir(os.path.join(DATA, "products"))
                 if json.load(open(os.path.join(DATA, "products", f), encoding="utf-8"))["photo"]),
             n("products")))
    if problems:
        print("\n%d thing(s) to look at:" % len(problems))
        for x in problems:
            print("  " + x)


if __name__ == "__main__":
    main()
