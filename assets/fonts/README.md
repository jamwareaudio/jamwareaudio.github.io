# Brand display font (the wordmark face)

The site header wordmark and the front-page hero mark ("JAMWARE AUDIO") render
in a display face, one notch toward street/graffiti but kept legible. It is
**not** a system font, so it ships here as a self-hosted file.

## What is installed

**Permanent Marker** (Font Diner, Inc.) — a felt-tip marker face. Chosen as the
"slightly graffiti, not too much" option: confident hand-lettered tag, still
fully readable at header size.

- `jamware-display.woff2` — the served file (converted from the TTF below).
- `jamware-display.ttf`   — the original source, kept for re-conversion.
- `LICENSE-PermanentMarker.txt` — the licence (see below).

**Licence: Apache License 2.0.** Free for commercial use and web embedding, no
attribution required in the UI. This satisfies the commercial-site requirement.
(An earlier candidate, "Antihero", was swapped out for this on 2026-08-16.)

## How it is wired

`styles.css` declares the `@font-face` (family "JamWare Display") and points
`--font-display` at it, with a fallback to the milled `--font-plate` stack. The
src list names every format a hand-off might arrive in and the browser takes the
first that loads, so only `jamware-display.woff2` is strictly required:

- **File present** → activates on the header wordmark and the hero mark on
  **every** page at once, no other edit needed.
- **File removed** → the wordmark falls back to Futura/Century Gothic. Nothing
  breaks; the display face is simply absent.

## To swap the face later

Convert the new font to `.woff2` (fontTools: `TTFont(src).flavor='woff2'`),
overwrite `jamware-display.woff2`, drop in the new source file and its licence,
and delete the old source/licence. No CSS change needed.

## Not wired to this file (separate render path)

The Gumroad art renders its own wordmark and does **not** read this CSS. The
product covers currently draw the rail wordmark in the plate font; the square
thumbnails use a logo-only rail (no wordmark text) so they are unaffected. If the
display face should appear on the full covers too, point the same font at:

- `gumroad/cover.html` — an `@font-face` on the `.rail .wordmark`.
- `gumroad/make-gumroad-shots.py` — a `PIL.ImageFont.truetype()` path.
