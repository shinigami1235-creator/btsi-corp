# 8BTSI Corp website

A static rebuild of btsi.com.ph. No WordPress, no plugins, no database, nothing
to patch. 141 files, 1.9 MB for the whole site.

## What is here

```
dist/                 the finished site, ready to upload
src/style.css         the stylesheet, copied into dist on build
src/site.js           menu behaviour, copied into dist on build
content.py            every sentence written for the site
build.py              the generator
lint.py               the writing lint
catalogue.json        106 products pulled from the old site
taxonomy.json         category, brand and pillar mapping
image-manifest.csv    which photograph goes where
assets/products/      drop product photographs here
```

## Putting it online

The Netlify project `btsi-corp` already exists and is empty. Open
https://app.netlify.com/projects/btsi-corp, go to Deploys, and drag the `dist`
folder onto the drop area. The site goes live at btsi-corp.netlify.app in a few
seconds.

To move the real domain across, add btsi.com.ph under Domain management and
point the DNS at Netlify. Keep the old site running until the DNS has moved.

## The quote form

The form posts to Netlify Forms, so there is no backend to run and no mail
server to configure. Turn Forms on in the project settings before the first
deploy. Submissions land in the Netlify dashboard and can be forwarded to
info@btsi.com.ph by email notification.

## Adding product photographs

Save each photograph as `assets/products/<slug>.jpg` using the slug in
image-manifest.csv, then run `python3 build.py`. Any product without a
photograph shows a placeholder tile, so the site works with none, some or all
of them.

Shoot or export at 1200px on the long edge. Anything larger is wasted on a
card that displays at 240px.

## Rebuilding

```
python3 lint.py      # check the writing
python3 build.py     # write dist/
```

`lint.py` fails on em dashes, curly quotes, negative parallelism, demonstrative
glosses, restated sentences and a list of banned vocabulary. It carries its own
known-bad and known-good lines so a rule cannot rot into one that matches
nothing. Run it before every deploy.

## What the old site was doing

- WordPress 5.3.23 and Avada 6.1.2, both years out of date
- Four lorem ipsum posts published on the News Blog since 2015
- Three menu links pointing at `http://localhost/wp88/`
- 208 requests and 70 images on the homepage, around 5 seconds to load
- Brand logos served at 506x406 and displayed at 143x115
- A WooCommerce cart on a catalogue with no prices
- The contact form asking for an email address twice

Every old address redirects to its new page. The 106 product URLs are mapped
one to one in `dist/_redirects`, so search results and bookmarks still land.

## Still needed

- Product photographs, 106 of them
- The logo as SVG or a high resolution PNG. The header currently sets the
  wordmark in Montserrat, which is close to the original but not the original.
- Body text for the four Aldena antennas. The old site had none.
- Real news posts, or leave the News section off.
