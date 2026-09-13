# -*- coding: utf-8 -*-
"""Check the built site for links and pictures that go nowhere.

validate.py checks the data before the build. This checks the site after it,
which catches the one thing the data cannot show on its own: a product deleted
while something else still points at it. Deleting the last product of a brand,
for instance, removes nothing else, but the brand page and the search index
both still expect it.

Run from the project folder, after build.py.
"""
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

sys.path.insert(0, ROOT)
from build import BASE  # noqa: E402  the same prefix the pages were written with

REF = re.compile(r'(?:href|src)="([^"]+)"')
SRCSET = re.compile(r'(?:srcset|imagesrcset)="([^"]+)"')


def targets(text):
    for m in REF.finditer(text):
        yield m.group(1)
    for m in SRCSET.finditer(text):
        for part in m.group(1).split(","):
            part = part.strip().split(" ")[0]
            if part:
                yield part


def resolve(url):
    """The file on disk a site path should land on, or None if it is not ours."""
    url = url.split("#")[0].split("?")[0]
    if not url or url.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//")):
        return None
    if not url.startswith("/"):
        return None
    path = urllib.parse.unquote(url)
    if BASE and path.startswith(BASE + "/"):
        path = path[len(BASE):]
    elif BASE and path == BASE:
        path = "/"
    rel = path.lstrip("/")
    full = os.path.join(DIST, rel)
    if path.endswith("/") or not os.path.splitext(rel)[1]:
        full = os.path.join(full, "index.html")
    return full


def main():
    if not os.path.isdir(DIST):
        print("dist/ is not there. Run build.py first.")
        return 1

    pages = []
    for d, _, fs in os.walk(DIST):
        for f in fs:
            if f.endswith(".html"):
                pages.append(os.path.join(d, f))

    broken = {}
    checked = 0
    for page in sorted(pages):
        with open(page, encoding="utf-8") as f:
            text = f.read()
        for url in targets(text):
            full = resolve(url)
            if full is None:
                continue
            checked += 1
            if not os.path.exists(full):
                broken.setdefault(url, []).append(os.path.relpath(page, DIST))

    # The site links to itself constantly, so one missing page shows up on
    # dozens of others. Report the missing thing once, with a count.
    for url in sorted(broken):
        where = broken[url]
        print("MISSING  %s" % url)
        print("         linked from %s%s"
              % (", ".join(where[:3]), " and %d more" % (len(where) - 3) if len(where) > 3 else ""))

    print("\n%d links and pictures checked across %d pages" % (checked, len(pages)))
    if broken:
        print("%d of them point at something that is not there. Nothing was published."
              % len(broken))
        return 1
    print("All resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
