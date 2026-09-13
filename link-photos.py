# -*- coding: utf-8 -*-
"""Write the photograph each product already has into its record.

The 106 photographs in assets/products are named after the product slug, and
build.py finds them that way whether or not the record says so. The website
editor cannot: it shows an empty Photograph box for a product whose page has a
photograph on it, which reads as a missing file.

This fills the box in. Run it once, on the machine that has the photographs.
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
EXTS = ("jpg", "jpeg", "png", "webp")


def main():
    d = os.path.join(ROOT, "data", "products")
    filled = already = none = 0
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        slug = fn[:-5]
        path = os.path.join(d, fn)
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        if (rec.get("photo") or "").strip():
            already += 1
            continue
        found = next(("/assets/products/%s.%s" % (slug, e) for e in EXTS
                      if os.path.exists(os.path.join(ROOT, "assets", "products",
                                                     "%s.%s" % (slug, e)))), "")
        if not found:
            none += 1
            continue
        rec["photo"] = found
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
            f.write("\n")
        filled += 1

    print("%d filled in, %d already set, %d still without a photograph"
          % (filled, already, none))


if __name__ == "__main__":
    main()
