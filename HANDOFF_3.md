# Handing the site over

Follows HANDOFF_2.md. The site looks the same. What changed is who can change
it and where it gets built.

## What was wrong

Adding a product meant editing catalogue.json, then taxonomy.json in two
places, then running ship.bat on your computer. Your friend could not do any
of that, so every change came through you.

## What it is now

One product is one file in `data/products/`, carrying its own manufacturer
and categories. Manufacturers and testimonials work the same way, in
`data/brands/` and `data/testimonials/`.

`taxonomy.json` now holds only the five pillars and the categories under
them, since which products are in them is decided by the products.
`content.py` holds only our own authored copy.

The site is built by GitHub rather than by your laptop. Pushing to main runs
the checks, builds the 133 pages and publishes them, in about a minute and a
half.

Your friend's editor gets a form at `/admin/`, which writes those files
straight to the repository. Saving publishes.

## The changeover

The repository currently holds the built site and Pages serves it from the
branch. It needs to hold the source instead, with Pages serving what the
build produces.

1. Run `setup-workflow.bat`. It copies the build instructions into
   `.github\workflows\deploy.yml`. This exists because Explorer refuses to
   create a folder whose name starts with a dot.
2. Run `first-push.bat`. It replaces the repository contents with this folder,
   and refuses to run if step 1 has not been done.
3. On GitHub: the repository, Settings, Pages, under "Build and deployment"
   set Source to **GitHub Actions**.

Steps 2 and 3 can go the other way round. Doing only step 2 leaves the site
blank until you do step 3, because the branch no longer holds any pages.

4. Watch the build at
   https://github.com/shinigami1235-creator/btsi-corp/actions
5. When it goes green, check the site and then
   https://shinigami1235-creator.github.io/btsi-corp/admin/

`btsi-corp-repo` next to this folder is the old clone and can go.

From then on `ship.bat` is what you run: it checks the data, builds, checks
every link, then commits and pushes.

## Giving your friend access

1. Get their GitHub username.
2. The repository, Settings, Collaborators, Add people, give them **Write**.
3. Send them `EDITING.md` and the editor address.

Write access lets them change the files under `data/` through the form, and
also everything else in the repository if they go looking. There is no
narrower permission on GitHub that still allows the editor to save.

## Transferring the repository

Do this once your friend has a GitHub account and the site is running.

1. The repository, Settings, General, bottom of the page, Transfer
   ownership.
2. Give their username. They accept by email.
3. They add you back as a collaborator with Write access.

The address changes to `https://<their-username>.github.io/btsi-corp/`, which
breaks the links in `build.py`, `ship.bat`, `first-push.bat` and the generated
editor config. Change `GH_USER` at the top of `build.py` and the two URLs in
the batch files, then push. The Actions workflow and the Pages setting carry
over on their own.

## When a build fails

Nothing is published and the site keeps serving the last good version. GitHub
emails whoever pushed, with a link to the log.

The checks run in this order:

- **Check the data.** Every product, manufacturer and testimonial: fields
  present and not empty, the manufacturer exists, every category is a real
  one, every photograph path points at a file that is there, and the filename
  works as a web address. Failure names the file and the field.
- **Check the writing.** The house style lint, on `content.py`. It reports and
  carries on, since a turn of phrase is not a reason to stop a product going
  live.
- **Build the site.**
- **Check nothing links to a page that is not there.** 8042 links and
  pictures on the current site. This catches a product deleted while a brand
  page still points at it.

`ship.bat` runs the same four checks before it pushes, so a mistake costs you
ten seconds rather than a failed build and an email.

## Moving to btsi.com.ph

Change `TARGET` at the top of `build.py` from `"pages"` to `"domain"`. That
drops the `/btsi-corp` prefix from every path, turns off `noindex`, writes
the sitemap, and writes `_redirects` with all 106 old WordPress addresses
from `archive/old-urls.json`.

GitHub Pages ignores `_redirects`, so those 106 addresses only start working
on a host that reads it, such as Netlify or Cloudflare Pages. Until then
anyone following an old link or an old search result lands on a 404.

The editor keeps working, since the image paths it writes are normalised on
the way in.

## Still open

- One product photograph is still missing, the Omnia µMPX. It failed to
  download and needs to come from your friend.
- Four Aldena antenna products have a one line summary and no description:
  `uhf-band`, `vhf-band-fm`, `vhf-band-i`, `vhf-band-iii`. Their pages are
  nearly empty. `validate.py` warns about them on every build.
- The logo is a PNG. An SVG would be sharper on a large screen.
- The 276 phrases the lint flags in manufacturer copy, and whether "We are
  your bridge to technical innovation" goes back on the About page. Both
  carried over from HANDOFF_1.
