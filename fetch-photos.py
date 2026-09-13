# -*- coding: utf-8 -*-
"""Pull the 106 product photographs off the old WordPress site.

Reads image-manifest.csv, which pairs every product slug with the image it
currently uses on btsi.com.ph, and writes each one into assets/products/ under
the name build.py looks for. Run it once, then run build.py.

Files already in assets/products/ are left alone, so a photograph the friend
supplies by hand always beats the one scraped off the old site, and a second
run only picks up what failed the first time.

With Pillow installed the images are converted to JPEG and capped at 1200px
wide. Without it they are saved untouched under whatever extension the old
site used, which build.py also accepts.
"""
import csv
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "image-manifest.csv")
ASSETS = os.path.join(ROOT, "asset-manifest.csv")
OUT = os.path.join(ROOT, "assets", "products")
MAX_W = 1200
QUALITY = 82
TIMEOUT = 25
TRIES = 3
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

MAGIC = {b"\xff\xd8\xff": "jpg", b"\x89PNG": "png", b"GIF8": "gif", b"RIFF": "webp"}


def kind(blob):
    for sig, name in MAGIC.items():
        if blob.startswith(sig):
            return name
    return None


def already_there(slug):
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(OUT, slug + "." + ext)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://btsi.com.ph/"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def save(blob, slug):
    """JPEG at a sane size when Pillow is here, the raw bytes when it is not."""
    if not HAVE_PIL:
        ext = kind(blob) or "jpg"
        path = os.path.join(OUT, "%s.%s" % (slug, ext))
        with open(path, "wb") as f:
            f.write(blob)
        return path

    import io
    im = Image.open(io.BytesIO(blob))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (255, 255, 255))
        flat.paste(im, mask=im.split()[-1])
        im = flat
    else:
        im = im.convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    path = os.path.join(OUT, slug + ".jpg")
    im.save(path, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return path


def trim_white(im, pad=12):
    """Crop the white margin off a logo so it can be sized by its own artwork.

    The old site's brand logos are 506x406 with the logo floating in the
    middle, so laying them out untrimmed gives every one a different optical
    size.
    """
    from PIL import ImageChops
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad), min(im.height, b + pad)))


def fetch_assets():
    """Brand logos, the three featured posters and the testimonial photograph."""
    if not os.path.exists(ASSETS):
        return 0, []
    rows = list(csv.DictReader(open(ASSETS, encoding="utf-8")))
    print("")
    print("%d other images (brand logos, posters, backgrounds)" % len(rows))
    got = 0
    failed = []
    for row in rows:
        dest = os.path.join(ROOT, row["save_as"].replace("/", os.sep))
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        blob = None
        why = ""
        for attempt in range(TRIES):
            try:
                blob = get(row["source_url"])
                break
            except Exception as ex:
                why = getattr(ex, "code", ex.__class__.__name__)
            time.sleep(1.5 * (attempt + 1))
        if blob and not kind(blob):
            blob, why = None, "not an image"
        if not blob:
            failed.append((row["save_as"], row["source_url"], str(why)))
            continue

        if HAVE_PIL:
            import io
            im = Image.open(io.BytesIO(blob)).convert("RGB")
            if row["kind"] == "brand":
                im = trim_white(im)
            cap = 900 if row["kind"] == "brand" else 1600
            if im.width > cap:
                im = im.resize((cap, round(im.height * cap / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
        else:
            with open(dest, "wb") as f:
                f.write(blob)
        got += 1
        print("  %-34s %6.0f KB" % (row["save_as"], os.path.getsize(dest) / 1024))
        time.sleep(0.15)
    return got, failed


def main():
    if not os.path.exists(MANIFEST):
        print("image-manifest.csv is not here. Run this from the project folder.")
        return 1
    os.makedirs(OUT, exist_ok=True)

    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    print("%d products in the manifest" % len(rows))
    print("Pillow %s" % ("found, converting to JPEG at %dpx" % MAX_W
                         if HAVE_PIL else "missing, saving the files as they come"))
    print("")

    got = skipped = 0
    failed = []
    for i, row in enumerate(rows, 1):
        slug = os.path.splitext(os.path.basename(row["save_as"]))[0]
        url = row["current_image_on_old_site"].strip()

        if already_there(slug):
            skipped += 1
            continue

        blob = None
        why = ""
        for attempt in range(TRIES):
            try:
                blob = get(url)
                break
            except urllib.error.HTTPError as ex:
                why = "HTTP %s" % ex.code
                if ex.code in (403, 404, 410):
                    break
            except Exception as ex:
                why = ex.__class__.__name__
            time.sleep(1.5 * (attempt + 1))

        if blob and not kind(blob):
            blob, why = None, "not an image"

        if not blob:
            failed.append((slug, url, why))
            print("  %3d/%d  %-34s %s" % (i, len(rows), slug, why))
            continue

        try:
            path = save(blob, slug)
        except Exception as ex:
            failed.append((slug, url, "could not save: %s" % ex))
            continue
        got += 1
        print("  %3d/%d  %-34s %6.0f KB" % (i, len(rows), slug, os.path.getsize(path) / 1024))
        time.sleep(0.15)

    a_got, a_failed = fetch_assets()
    failed += a_failed

    print("")
    print("downloaded %d photographs and %d other images, already had %d, failed %d"
          % (got, a_got, skipped, len(failed)))
    if failed:
        print("")
        print("These need a photograph from the friend:")
        for slug, url, why in failed:
            print("  %-34s %-14s %s" % (slug, why, url))
    print("")
    print("Now run: python build.py")
    return 1 if failed and got == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
