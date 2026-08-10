# site/ — the JamWare Audio website

A plain static site. No build step, no dependencies, no framework: five
product pages, one homepage, one stylesheet. Open `index.html` in a browser
and it works.

**Four products are for sale** — MutationStation, Chordinator, Spectrl and
MidiMirror — plus **The Companion Suite** bundle. **Arranger is listed but not
released**: it is the one Ableton Extension left, the rest of the range is
standalone, and its page carries a "Not released yet" panel instead of a buy
button. Do not add a buy button until there is something to download.

```
site/
  index.html          homepage — hero, five product cards, about
  styles.css          the whole design system (see below)
  apps/*.html         one page per product
  assets/
    logo.svg          the company mark (copy of ../brand/company-logo.svg)
    icons/*.png       copies of ../brand/out/<app>-1024.png
    shots/*.png       product screenshots
  gumroad/            NOT part of the published site — the storefront kit:
    GUMROAD-KIT.md      ready-to-paste copy + a cohesion checklist
    cover.html          the cover-art generator
    make-gumroad-art.sh renders out/<app>-cover.png and -square.png
```

## The design system

`styles.css` does not invent a look. The palette is copied from the apps' own
`:root` (MutationStation's `interface.html`, mirrored in Spectrl and
Chordinator) and from `../brand/brand.json`, so the site reads as another
surface in the same instrument family:

- **The faceplate** — the page background is the apps' brushed-aluminium
  gradient, `background-attachment: fixed` so the whole site is one milled
  panel you scroll across rather than a stack of cards.
- **Panel furniture** — every block is `.panel` with an engraved
  `.panel-head` band, the same component as a section header in the software.
- **The dark inset screen** — `.screen` is the recess Spectrl's analyser and
  MutationStation's piano roll sit in. Screenshots go inside it, so an app
  window nests into the page instead of floating on it.
- **One accent per product** — set with `--accent` on the card or in the page's
  `<style>` block. It drives the pilot lamp on the panel header, the buy
  button, and the feature bullets. Nothing else on the page is coloured.

The design commits to the light faceplate deliberately — there is no dark-mode
version of a milled aluminium panel — so every colour is painted explicitly and
there is no `prefers-color-scheme` override.

### Changing an accent

An accent lives in three places and all three must agree:

1. `../brand/brand.json` (the source of truth, drives the icons)
2. the `style="--accent:…"` on that product's card in `index.html`
3. the `<style>:root { --accent: … }</style>` in `apps/<product>.html`

## Before this goes live

- [x] **Confirm the Gumroad URLs.** Checked against the real dashboard on
      2026-08-10. The four app slugs — `mutationstation`, `chordinator`,
      `spectrl`, `midimirror` — are all correct and need no rewriting.
- [ ] **The Suite button is a dead link.** `/l/companion-suite` does not exist:
      the store holds the four apps, a "Buy me a coffee" tip product, and an
      unrelated sample pack, and nothing else. So the `#suite` panel on
      `index.html` sends buyers to a 404. Either create the bundle on Gumroad
      or drop that panel's button — do not ship the page as it stands.

      If you do create it, each slug appears twice (the card on `index.html`,
      the page in `apps/`), so use the script rather than editing by hand:

      ```sh
      ./set-store-links.py                              # list what is there now
      ./set-store-links.py --spectrl <real-slug> \
                           --suite <real-slug>          # rewrite only what is wrong
      ```

      A product is identified by its page, not its slug, so the script is safe
      to run repeatedly.
- [x] **Screenshots** — all four shipping products now carry a capture taken on
      2026-08-10 from the installed build, at the **full 1728pt window width**
      (3456×2014 retina, downscaled to 2000px for the site). All four share one
      aspect ratio, so the cards and the `.screen` insets line up.

      They were taken with `screencapture -o -x -l <windowID>`, which captures
      exactly the window rectangle with no drop shadow and no desktop behind
      it. ⚠ **Do not resize the window smaller first.** The earlier captures
      were made at 1280–1600pt and the apps reflow at those widths —
      MutationStation's header ran its title under the transport controls,
      which is why the old shot looked wrong rather than merely small.

      Arranger still shows a "Screenshot coming soon" panel; it is unreleased,
      so there is nothing to capture. Its page keeps the `SCREENSHOT SLOT`
      comment.
- [ ] **Decide the support address.** Pages currently link
      `toastonjam12345@gmail.com`. If JamWare Audio gets its own domain, a
      `support@` address on it will look considerably more professional.

## Deploying to GitHub Pages

This folder sits inside `CompanionApps/`, which is **not** a git repository. The
cleanest option is a separate repo for the site alone, so publishing the website
never means publishing the app source.

```sh
cd site
git init
git add .
git commit -m "JamWare Audio website"
git branch -M main
git remote add origin git@github.com:<you>/jamware-site.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch →
`main` / `/ (root)`**. It goes live at `https://<you>.github.io/jamware-site/`
within a minute or two.

### A custom domain

`jamware.io` / `jamware.app` / `jamware.dev` — whichever you get — makes the
Gumroad pages look like part of a company rather than a hobby.

1. Add a file called `CNAME` in this folder containing just the domain, e.g.
   `jamware.app`.
2. At your registrar, add these DNS records:
   - `A` records for the apex `@` pointing at `185.199.108.153`,
     `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - a `CNAME` for `www` pointing at `<you>.github.io`
3. Back in **Settings → Pages**, enter the domain and tick **Enforce HTTPS**
   once the certificate has been issued (it can take up to an hour).

### If you would rather not use GitHub

The site is static files with no build step, so it deploys anywhere. Netlify and
Cloudflare Pages both accept this folder dragged onto their dashboard, and both
handle custom domains with less DNS work than Pages.
