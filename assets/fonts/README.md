# Brand display font (currently: none — plate fallback)

The site header wordmark and the front-page hero mark ("JAMWARE AUDIO") can
render in a self-hosted display face. **Right now no display file is installed**,
so both render in the milled Futura/Century Gothic `--font-plate` stack — the
site's original, geometric look. This is deliberate: two graffiti/marker
candidates (Antihero, then Permanent Marker) were trialled and both reverted on
2026-08-16 in favour of the plain plate caps.

## How the switch works

`styles.css` declares the `@font-face` (family "JamWare Display") and points
`--font-display` at it, with a fallback to `--font-plate`. The src list names
every format a hand-off might arrive in and the browser takes the first that
loads:

- **No file here** (current state) → every rule using `--font-display` resolves
  to the plate stack. Nothing is broken; the display face is simply absent.
- **A file here** → it activates on the header wordmark and the hero mark on
  **every** page at once, no other edit needed.

## To turn a display face back on later

Drop **one** font file here, named exactly:

    jamware-display.woff2      (preferred — smallest, self-hosts cleanest)
    jamware-display.woff
    jamware-display.otf
    jamware-display.ttf

Convert to `.woff2` with fontTools (`TTFont(src).flavor='woff2'`) if you only
have a TTF/OTF. Include its licence file alongside, and make sure the licence
permits commercial use / web embedding — this is a commercial product site.

## Not wired to this file (separate render path)

The Gumroad art renders its own wordmark and does **not** read this CSS. The
product covers draw the rail wordmark in the plate font; the square thumbnails
use a logo-only rail (no wordmark text). If a display face should appear on the
full covers too, point the same font at:

- `gumroad/cover.html` — an `@font-face` on the `.rail .wordmark`.
- `gumroad/make-gumroad-shots.py` — a `PIL.ImageFont.truetype()` path.
