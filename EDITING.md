# Editing the website

The editor is at
https://shinigami1235-creator.github.io/btsi-corp/admin/

Saving publishes. The site rebuilds and the change is live in about two
minutes.

## Signing in the first time

1. Make a GitHub account at github.com.
2. Send the username to whoever runs the site so they can give you access.
3. Open the editor address above.
4. Press **Sign In Using Access Token**, the lower of the two buttons. The one
   above it, "Sign In with GitHub", does not work on this site and ends on a
   blank page.
5. In the dialog, follow the link to the GitHub settings page. It opens with
   the name and the permission already filled in.
6. Under "Repository access" choose "Only select repositories" and pick
   btsi-corp. Choose how long the token should last. Press Generate token.
7. Copy the token, paste it into the dialog, then press Sign In.

A token is a password for the site, so do not send it to anyone. It is kept in
this browser only: signing in on another computer or another browser needs a
new one, and so does a token that has expired.

## What you can change

Products, Manufacturers and Testimonials, listed down the left. Everything
else on the site is fixed.

## Adding a product

1. Press Products, then "Create new".
2. **Product name.** The full name as you want it read, including the
   manufacturer: "Elenos Indium 2000".
3. **Manufacturer.** Pick from the list. To add a product for a manufacturer
   that is not there yet, add the manufacturer first.
4. **Categories.** Pick at least one. The product appears on the page for
   every category you tick.
5. **Photograph.** Press the field, then Upload. A JPEG about 1200 pixels
   wide is the right size. Leaving it empty gives a grey panel saying the
   photograph is to follow.
6. **One line summary.** One or two sentences, shown on the product card, in
   search results and in the link preview when someone shares the page.
7. **Full description.** The long text on the product page. Leave a blank
   line between paragraphs. A line reading "Features:" turns everything under
   it into a list.
8. Press Save.

The web address comes from the product name, so "Elenos Indium 2000" becomes
`/products/elenos-indium-2000/`. Renaming a product later changes its address
and breaks any link anyone had to the old one.

## Adding a manufacturer

1. Press Manufacturers, then "Create new".
2. **Manufacturer name.** As it should appear: "Telos Alliance".
3. **One line summary.** What they make, in a few words: "FM transmitters,
   exciters and remote control". This shows under the name on the
   manufacturers page.
4. **Description.** A paragraph for the top of their page.
5. **Logo.** Upload their logo. A PNG with a transparent background or a JPEG
   on white both work, since it sits on a white tile. Without one the tile
   shows the name as text.
6. Save, then add their products.

A manufacturer with no products gets a page with nothing on it, so add the
products the same day.

## Adding a testimonial

1. Press Testimonials, then "Create new".
2. **What they said.** Their words, unedited. Tidying a quote misquotes the
   person who gave it.
3. **Their name.**
4. **Job title and company.** "President and CEO, Eight TriMedia Pro, Inc."
5. Save.

They rotate on the home page and sit as cards on the Company page, in the
order the files are listed.

## Removing something

Open it, then Delete entry. A deleted product disappears from its
manufacturer page, its category pages and the search box on the next build.

Deleting the last product of a manufacturer leaves that manufacturer with an
empty page, so delete the manufacturer too.

## When a save does not appear on the site

Give it three minutes and reload the page.

If it is still missing, the build found a problem and stopped, and the site
is still showing the version before your change. GitHub sends an email with a
link to the log, and the log names the file and what is wrong with it, like
this:

    data/products/elenos-indium-2000.json: excerpt is empty

Fix that field in the editor and save again.

## Photographs

Upload them at about 1200 pixels wide. Bigger files make the page slow to
load on a phone, and the site never shows a product photograph larger than
that.

Uploading a photograph with the same name as one already there replaces it
everywhere it is used.
