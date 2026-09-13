# 8BTSI Corp website: design update

Follows HANDOFF_1.md. The site is the same 133 pages built by the same
generator. What changed is how it looks and how it moves.

## Direction

Variant C, "On air", chosen from the three in design-variants/.

Dark site. Navy #113C93 stays the brand colour, with #3A74E8 as the lit
version of it for small accents and #FF2D55 for the on-air dot. Montserrat
now loads weights 800 and 900 for headings. Body copy is still Inter.

Content that needs reading sits on a white slab: product descriptions,
company text, the services cards, every product grid and both forms. Dark
carries the hero, the equipment rows, the brands and the footer.

## What moves

Written by hand in src/site.js. No libraries, nothing fetched from a CDN,
6.9 KB unminified.

- Hero: three photographs crossfading on a seven second cycle, drifting
  against the scroll and against the pointer, with a progress bar per dot.
- Ticker under the hero, looping the tagline and the five equipment groups.
- Equipment rows that slide right and light up under the cursor.
- Gallery slider with a progress bar, arrows, and a six and a half second
  auto advance that stops when the tab is hidden.
- Section reveals on scroll, staggered.
- The two figures on the company block count up when they come into view.
- Header turns solid on scroll.

Every one of these is off under `prefers-reduced-motion`.

## Photographs

Three Unsplash photographs carry the hero and the gallery:

- Transmitter masts at sunset, Mario Caruso,
  https://unsplash.com/photos/0C9VmZUqcT8
- Broadcast audio console, Jacob Hodgson,
  https://unsplash.com/photos/Zwl5xuwGVUU
- Television gallery multiview, Gabriel Weyand,
  https://unsplash.com/photos/X8uonmU2Ssw

The Unsplash licence covers commercial use and does not require credit. The
three names are in an HTML comment at the top of the home page anyway, as
Unsplash asks.

They load from the Unsplash CDN, sized by the query string. To host them
yourself, download each one, save it under `assets/site/`, and change the
`src` in the `SCENES` list at the top of build.py to
`/assets/site/<file>.jpg`. Nothing else in the build refers to them.

The 106 product photographs are still outstanding, as before. Products
without one now show a dark placeholder panel rather than a white one, so a
missing photograph no longer pulls the eye.

## Checked

- 20 page and viewport combinations rendered in Chromium at 1440 and 390:
  no horizontal scroll, one h1 each, no console errors, every scroll reveal
  fires, no broken images.
- 133 pages: zero broken internal links, zero localhost links, a meta
  description on every page, alt text on every image, no em dashes, en
  dashes or curly quotes in the output.
- lint.py passes, including its own 18 known-bad and 6 known-good self test.
- 1.89 MB for the whole site. Home is 17.5 KB of HTML, 29.8 KB of CSS.

## Where the files are

Unpacked in place rather than zipped. The project sits directly in the
btsi-website folder: build.py, content.py, lint.py, the three data files,
src/ and dist/. The old btsi-website.zip is a previous version and can go.

## Looking at it locally

Double click `preview.bat`. It serves `dist` on http://localhost:8000 and
opens a browser at it.

Opening dist\index.html straight from Explorer gives you unstyled blue links
on a white page. The paths are absolute, so from the filesystem `/style.css`
points at the root of your C: drive and neither the stylesheet nor the
JavaScript loads. It needs a server.

## Host

GitHub Pages rather than Netlify. DEPLOY-GITHUB.md has the steps.

Two consequences. There is no form, because Pages runs nothing: the quote
section is the office line and both email addresses instead, and on a product
page the email opens with that product in the subject. And the 106 old
WordPress addresses are not redirected, because Pages has no redirect rules.
That only bites once btsi.com.ph points at the new site.

## Product photographs

`photos.bat` pulls all 106 off the old WordPress site. image-manifest.csv
already pairs every product slug with the image btsi.com.ph currently uses, so
the script reads that, downloads each one into assets/products/ under the name
build.py looks for, and reports whatever it could not get.

Anything already sitting in assets/products/ is left alone, so a photograph
the friend supplies by hand always wins over the scraped one, and running it a
second time only retries the failures.

With Pillow installed the images come out as JPEG capped at 1200px wide;
photos.bat installs it if it is missing. Without it they are saved as they
come, which build.py also accepts.

Order: `photos.bat`, then `ship.bat`.

## The rest of the old site's artwork

asset-manifest.csv covers what is not a product photograph, and photos.bat
pulls it in the same run:

- The 14 manufacturer logos, from the old home page carousel. Each was a
  506x406 JPEG with the logo floating in the middle, so the script trims the
  white margin off. They show on a white tile in the brand strip, the brand
  grid and at the top of each brand page, which keeps the manufacturers'
  colours right against a dark page.
- The three brand posters, telos, omnia and axia. Each is a product
  photograph on the manufacturer's colour with no text baked in, so the
  heading and line are set in our own type over the top. They drive the
  Featured band on the home page and link to the matching brand page.
- The studio photograph that sat behind the testimonials.

Every one of these is optional. Until the files are there the brand tiles
fall back to text, and the Featured band is left out of the page rather than
rendering empty.

The old home page also had three wide slider banners. They are not used: the
text is flattened into the JPEG, so they cannot be retyped, resized or
translated, and 2018 marketing type against this layout looks like what it
is.

## Testimonials

Three, quoted from the named customers on the old site: Cesiah Opulencia
Dacer of Eight TriMedia Pro, Paul David Domingo of FEBC, and Arden C. Ramos
of ABS-CBN. They rotate on the home page over the studio photograph, and sit
as three cards on the Company page for anyone reading properly.

They live in `TESTIMONIALS` in content.py and lint.py skips that block on
purpose, which it prints when it runs. They are other people's sentences and
tidying them would misquote the people who gave them.

The old site's own photographs carry whatever quality that site had. Treat them as a floor rather than the finished job, and swap in
better ones as the friend takes them.

## Still open

The two questions from HANDOFF_1: what to do about the 276 flagged phrases in
the manufacturer copy, and whether the "bridge to technical innovation"
tagline goes back on the About page.
