# -*- coding: utf-8 -*-
"""Check the data before the site is built from it.

This runs first in the deploy, so a bad entry stops the build rather than
reaching the site. When it stops, the live site carries on serving the last
good build: nothing breaks, the change just does not appear.

Errors stop the build. Warnings do not, because an empty category or a brand
with nothing in it yet is a normal state to be in for a while.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

SHAPES = {
    "products": {
        # body is optional: four of the Aldena antennas arrived from the old
        # site with nothing but a one line description, and a thin page is
        # better than a blocked deploy. It warns instead.
        "required": ("title", "brand", "categories", "excerpt"),
        "optional": ("photo", "body"),
    },
    "brands": {
        "required": ("name", "line", "blurb"),
        "optional": ("logo",),
    },
    "testimonials": {
        "required": ("quote", "name", "role"),
        "optional": (),
    },
}

errors = []
warnings = []


def err(where, msg):
    errors.append("%s: %s" % (where, msg))


def warn(where, msg):
    warnings.append("%s: %s" % (where, msg))


def read_folder(kind):
    """Load data/<kind>/, reporting a file that is not readable JSON rather
    than throwing, so a half-saved file gives one clear message rather than a
    stack trace someone has to read."""
    out = {}
    d = os.path.join(DATA, kind)
    if not os.path.isdir(d):
        err("data/" + kind, "folder is missing")
        return out
    for fn in sorted(os.listdir(fn_dir := d)):
        if fn.startswith(".") or not fn.endswith(".json"):
            if not fn.startswith("."):
                warn("data/%s/%s" % (kind, fn), "not a .json file, ignored")
            continue
        path = os.path.join(fn_dir, fn)
        try:
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
        except UnicodeDecodeError:
            err("data/%s/%s" % (kind, fn), "is not UTF-8 text")
            continue
        except json.JSONDecodeError as ex:
            err("data/%s/%s" % (kind, fn),
                "is not valid JSON, at line %d column %d (%s)" % (ex.lineno, ex.colno, ex.msg))
            continue
        if not isinstance(rec, dict):
            err("data/%s/%s" % (kind, fn), "should hold one entry rather than a %s"
                % type(rec).__name__)
            continue
        out[fn[:-5]] = rec
    return out


def check_fields(kind, slug, rec):
    where = "data/%s/%s.json" % (kind, slug)
    shape = SHAPES[kind]

    if not SLUG.match(slug):
        err(where, "the filename becomes the web address, so it needs lowercase "
                   "letters, numbers and hyphens only")

    for key in shape["required"]:
        if key not in rec:
            err(where, "%s is missing" % key)
            continue
        v = rec[key]
        if isinstance(v, str) and not v.strip():
            err(where, "%s is empty" % key)
        elif isinstance(v, list) and not v:
            err(where, "%s is empty" % key)

    known = set(shape["required"]) | set(shape["optional"])
    for key in rec:
        if key not in known:
            warn(where, "%s is not a field the site uses, so it will be ignored" % key)

    for key in shape["required"] + shape["optional"]:
        v = rec.get(key)
        if key == "categories":
            if v is not None and not isinstance(v, list):
                err(where, "categories should be a list")
        elif v is not None and not isinstance(v, str):
            err(where, "%s should be text rather than a %s" % (key, type(v).__name__))


def check_asset(where, field, value):
    """A path to a picture that is not there means a hole in the page."""
    v = (value or "").strip()
    if not v:
        return
    rel = v.lstrip("/")
    # An editor's upload may carry the /btsi-corp prefix the site is served
    # under; the build strips it, so accept it here too.
    for candidate in (rel, re.sub(r"^btsi-corp/", "", rel)):
        if os.path.exists(os.path.join(ROOT, candidate)):
            return
    err(where, "%s points at %s, which is not in the repository" % (field, v))


def main():
    tax_path = os.path.join(ROOT, "taxonomy.json")
    try:
        with open(tax_path, encoding="utf-8") as f:
            tax = json.load(f)
    except (OSError, json.JSONDecodeError) as ex:
        print("taxonomy.json could not be read: %s" % ex)
        return 1

    categories = {c for d in tax["pillars"].values() for c in d["categories"]}

    products = read_folder("products")
    brands = read_folder("brands")
    testimonials = read_folder("testimonials")

    for kind, recs in (("products", products), ("brands", brands),
                       ("testimonials", testimonials)):
        for slug, rec in recs.items():
            check_fields(kind, slug, rec)

    for slug, p in products.items():
        where = "data/products/%s.json" % slug
        b = (p.get("brand") or "").strip()
        if b and b not in brands:
            err(where, "brand is %r, which is not one of: %s"
                % (b, ", ".join(sorted(brands)) or "(none defined)"))
        cats = p.get("categories")
        if isinstance(cats, list):
            for c in cats:
                if c not in categories:
                    err(where, "category %r is not one of the %d in taxonomy.json"
                        % (c, len(categories)))
        check_asset(where, "photo", p.get("photo"))
        if not (p.get("body") or "").strip():
            warn(where, "no description, so the page will show only the one line summary")

    for slug, b in brands.items():
        check_asset("data/brands/%s.json" % slug, "logo", b.get("logo"))

    # Two products sharing a title is legal but reads as a mistake on a
    # category page, where they sit next to each other looking identical.
    seen = {}
    for slug, p in products.items():
        t = (p.get("title") or "").strip().lower()
        if t:
            seen.setdefault(t, []).append(slug)
    for t, slugs in seen.items():
        if len(slugs) > 1:
            warn("data/products", "%s share the title %r" % (" and ".join(slugs), t))

    used_brands = {(p.get("brand") or "") for p in products.values()}
    for slug in sorted(set(brands) - used_brands):
        warn("data/brands/%s.json" % slug, "no products, so its page will be empty")
    used_cats = {c for p in products.values() if isinstance(p.get("categories"), list)
                 for c in p["categories"]}
    for c in sorted(categories - used_cats):
        warn("taxonomy.json", "category %r has no products, so it will not appear" % c)

    if not testimonials:
        warn("data/testimonials", "none, so the home page band and the company "
                                  "page cards are left out")

    for w in warnings:
        print("warning  " + w)
    for e in errors:
        print("ERROR    " + e)

    print("\n%d products, %d brands, %d testimonials checked"
          % (len(products), len(brands), len(testimonials)))
    if errors:
        print("%d error(s). The site was not rebuilt and is still showing the "
              "last good version." % len(errors))
        return 1
    print("%d warning(s), nothing blocking." % len(warnings) if warnings else "No problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
