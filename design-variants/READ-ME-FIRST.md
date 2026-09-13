# Three homepage directions

Open each file in a browser and scroll the whole page. They use the same copy
from `content.py` and the same navy, so what differs is layout and motion.

## A, Signal

Full-screen hero with a three-image slider that crossfades and slowly zooms,
a live waveform drawn across the bottom, and a progress bar on each dot.
Equipment sits in a sideways rail you drag. Brands run past in a loop that
pauses on hover. Services go on a dark slab. Counters count up.

Closest to how a broadcaster's own site tends to look. Safe and confident.

## B, Signal chain

Split hero: type on the left, a tall image slider on the right. Headline
lines rise into place on load.

The equipment section is the piece to judge. It pins one large image on the
left while the five groups scroll past on the right, and the image and the
big number change as each one comes level. It reads as a walk down the signal
chain rather than five cards.

Lightest of the three. Most like a manufacturer's own site.

## C, On air

Dark on every section down to the footer. Oversized headline, the hero photo drifts
against the scroll and against the pointer, a ticker of the tagline and the
five groups runs under it.

Equipment is a list of full-width rows that slide right and light up under the
cursor, followed by a wide gallery slider. The services block flips to white
so the page has somewhere to breathe.

Boldest. Reads as a company that is confident about being the supplier.

## What is temporary

- The three photographs are generated placeholders. They stand in for real
  transmitter, studio and rack photography and should not ship.
- They load from a remote URL, so the pages need a connection to show them.
- Nothing here is wired to the 141-page build yet. Pick a direction and the
  templates in `build.py` get reshaped to match.
