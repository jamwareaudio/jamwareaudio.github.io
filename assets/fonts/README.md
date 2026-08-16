# Brand display font (the graffiti wordmark)

The site header wordmark and the front-page hero mark ("JAMWARE AUDIO") are
wired to render in a spiky graffiti-tag face — the "BELTERBOX"-style reference
the user supplied. That face is **not on the system** and cannot be faithfully
hand-lettered from a picture, so it needs a real font file.

## To turn it on

Drop **one** font file here, named exactly:

    jamware-display.woff2      (preferred — smallest, self-hosts cleanest)
    jamware-display.woff
    jamware-display.otf
    jamware-display.ttf

`styles.css` already declares the `@font-face` and points `--font-display` at it,
with a fallback to the milled `--font-plate` stack. So:

- **No file here** → the wordmark renders in Futura/Century Gothic, exactly as
  the site looked before. Nothing is broken; the graffiti face is simply absent.
- **A file here** → it activates on the header wordmark and the hero mark on
  **every** page at once, no other edit needed.

`.woff2` is best for the web. If you only have a `.ttf`/`.otf`, that works too;
convert to `.woff2` later for a smaller download if you like.

## Licensing — read before shipping

This is a **commercial product site**, so the font must be licensed for
commercial use / web embedding. A "free for personal use" graffiti font is not
enough. Check the licence that ships with whatever file you obtain.

## Still to do once the file lands (web lane)

The Gumroad art renders the wordmark separately and does **not** read this CSS:

- `gumroad/cover.html` — the "JAMWARE AUDIO" rail across the product cover.
- `gumroad/make-gumroad-shots.py` — the same rail baked into the hero shots.

Both need the same face pointed at this file (an `@font-face` in cover.html; a
`PIL.ImageFont.truetype()` path in the shots script) and the covers/shots
re-rendered. Do that in the same sitting the file arrives.
