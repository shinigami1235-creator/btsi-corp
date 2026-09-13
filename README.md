# 8BTSI Corp website

A static rebuild of btsi.com.ph. No WordPress, no plugins, no database, nothing
to patch. 133 pages, about 2 MB for the whole site.

Editing it needs no code and no computer: the form at `/admin/` writes to this
repository and GitHub rebuilds the site within two minutes. The guide for
whoever does that is [EDITING.md](EDITING.md).

## What is here

```
data/products/        one file per product, 106 of them
data/brands/          one file per manufacturer, 14
data/testimonials/    one file per quote
taxonomy.json         the five pillars and the categories under them
content.py            our own authored copy, everything not in data/
assets/               photographs, logos, icons
src/style.css         the stylesheet
src/site.js           the motion, hand written, no libraries
src/admin/            the website editor
build.py              the generator
validate.py           refuses a broken entry before it can publish
check-links.py        refuses a link that goes nowhere
lint.py               the writing lint
archive/              the original scrape, kept for its old addresses
```

`dist/` is the built site. It is not committed, because GitHub builds it.

## Adding a product

Through the editor at
https://shinigami1235-creator.github.io/btsi-corp/admin/, which is the point of
the arrangement. By hand it is one file in `data/products/`, named for the
address you want the page to have.

Nothing else needs editing. A product carries its own manufacturer and
categories, so the lists it belongs to work themselves out.

## Publishing

Pushing to `main` runs the checks, builds the site and publishes it. `ship.bat`
pushes for you, having run the same checks here first so a mistake costs ten
seconds rather than a failed build and an email.

If a check fails nothing is published and the live site carries on serving the
last good build. GitHub emails whoever pushed, with a link to a log that names
the file and the field.

## Rebuilding by hand

```
python validate.py     # the data
python lint.py         # the writing
python build.py        # write dist/
python check-links.py  # every link and picture resolves
```

`lint.py` fails on em dashes, curly quotes, negative parallelism, demonstrative
glosses, restated sentences and a list of banned vocabulary, across both the
authored copy and the markdown documents. It carries its own known-bad and
known-good lines so a rule cannot rot into one that matches nothing.

## Moving to btsi.com.ph

`TARGET` at the top of `build.py`, from `"pages"` to `"domain"`. That drops the
`/btsi-corp` prefix, turns off `noindex`, writes the sitemap, and writes
`_redirects` mapping all 106 old WordPress addresses one to one.

GitHub Pages ignores `_redirects`, so those only start working on a host that
reads it. Until then an old link lands on a 404.

## Still needed

- One product photograph, the Omnia µMPX.
- Body text for four Aldena antennas: `uhf-band`, `vhf-band-fm`, `vhf-band-i`,
  `vhf-band-iii`. The old site had none, so those pages carry one line each.
- The logo as SVG. Everything in `assets/site/` is raster.
