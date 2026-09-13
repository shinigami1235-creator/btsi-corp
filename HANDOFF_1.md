# 8BTSI Corp website: handoff

Read this first, then README.md for the build mechanics.

## What this is

A replacement website for 8BTSI Corp, a broadcast transmission and audio
equipment supplier in Pasig City. The company belongs to a friend of Gid's, the
same friend the employee progress tracker was built for. Their live site is
btsi.com.ph and it is a 2018 WordPress install nobody has touched since.

The replacement is hand-built static HTML. No WordPress, no plugins, no
database. It is finished and it has not been deployed.

## Decisions already made

Do not reopen these without asking.

1. New static site rather than repairing the WordPress. Gid chose this.
2. Individual product pages for all 106 products, not category pages only.
3. Copy Gid authored is rewritten in his voice and passes lint.py.
4. Manufacturer product descriptions stay factual and unrewritten.
5. Business register throughout, applied after the first draft read too casual.
6. Brand colour is navy #113C93, sampled from their own logo file. Headings in
   Montserrat, body in Inter, which is the pairing the old theme already used.
7. Deploy target is Netlify, chosen because Netlify Forms runs the quote form
   with no backend.

## State

Built and verified:

- 141 files. Home, 5 pillar pages, 14 brand pages, 106 product pages, company,
  services, contact, thanks, 404.
- 1.9 MB for the whole site. Homepage is 11.7 KB of HTML, 18.6 KB of CSS,
  1.3 KB of JavaScript.
- Zero broken internal links, zero localhost links, one h1 per page, a meta
  description on every page, alt text on every image, no horizontal scroll at
  390px.
- Every old WordPress address redirects in dist/_redirects, including all 106
  product URLs mapped one to one.
- No em dashes, en dashes or curly quotes anywhere in the rendered output.

## Blocked

The Netlify project `btsi-corp` exists and is empty.
Site id `60bdbe26-e3d1-45f7-b688-e0b649fdca06`.

This container's egress policy blocks `api.netlify.com` and
`netlify-mcp.netlify.app`, so the deploy returns 403 every time. Two attempts
were made and stopped. A new session in the same container will hit the same
wall.

Deploy by hand instead. Open https://app.netlify.com/projects/btsi-corp, go to
Deploys, drag the `dist` folder onto the drop area. Turn Forms on in the
project settings before the first deploy or the quote form collects nothing.

## Waiting on Gid

Two questions were asked and are unanswered.

1. The manufacturer product copy carries 276 flagged phrases: "seamless" 16
   times, "robust" 13, "state-of-the-art" 9, and 45 rhetorical questions. Leave
   it factual, clean it mechanically, or rewrite all 106 properly.
2. The About page lead was their own tagline, "We are your bridge to technical
   innovation". It was replaced with a concrete line. Ask whether the original
   goes back.

## Waiting on his friend

- 106 product photographs. image-manifest.csv names every file, the slug to
  save it under, and the image currently on the old site. Save each one as
  `assets/products/<slug>.jpg` and run `python3 build.py`. Products with no
  photograph show a placeholder tile, so the site works with none of them.
- The logo as SVG or a high resolution PNG. The header sets the wordmark in
  Montserrat, which is close to the original and is not the original.
- Body text for the four Aldena antennas. The old site published none.
- Real news posts, or leave the News section off the site.

## Things that will waste a new session's time

- `btsi.com.ph` blocks WebFetch through robots.txt on every path, including
  robots.txt itself. Wayback, archive.ph, Bing, DuckDuckGo and jina.ai proxies
  are all blocked too. Read the site through a browser tool instead.
- The browser pane grants site access one page load at a time. Open the site
  once, then run same-origin `fetch()` from inside the open page with the
  javascript tool. That needs no further grants.
- Their WordPress REST API is open at `/wp-json/wp/v2/product`. All 106
  products came out of it in two calls. `/wp-json/wp/v2/product_cat` returns
  404, so category membership was scraped from the
  `/product-category/<slug>/` archives instead.
- Every category archive lists `productionairbox` because the link sits in the
  site's main menu. Strip it before trusting a category list.
- Google Fonts is blocked from this container, so the screenshots render in
  fallback faces. The fonts load normally for real visitors.
- Playwright chromium is at
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` rather than the path the
  environment note gives.

## Files

Everything is in btsi-website.zip. The container is ephemeral, so the zip is
the source of truth.

```
dist/                 the finished site, upload this
src/style.css         stylesheet, copied into dist on build
src/site.js           menu behaviour, copied into dist on build
content.py            every sentence written for the site
build.py              the generator
lint.py               the writing lint
catalogue.json        106 products pulled from the old site
taxonomy.json         category, brand and pillar mapping
image-manifest.csv    which photograph goes where
README.md             build and deploy mechanics
```

Rebuild:

```
python3 lint.py      # writing check, must pass
python3 build.py     # writes dist/
```

`lint.py` runs 18 known-bad and 6 known-good lines against itself before it
checks anything, so a rule cannot rot into one that matches nothing. Run it
before every deploy.

## What the old site is doing, for the record

- WordPress 5.3.23 and Avada 6.1.2
- Four lorem ipsum posts published on the News Blog since 2015
- Three menu links pointing at `http://localhost/wp88/`
- 208 requests and 70 images on the homepage, around 5 seconds to load
- Brand logos served at 506x406 and displayed at 143x115
- A WooCommerce cart on a catalogue with no prices
- A contact form asking for an email address twice
- No meta description on the homepage
