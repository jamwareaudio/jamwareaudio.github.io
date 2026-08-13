# HANDOFF — website, Gumroad storefront, launch sequence

Written 2026-08-10. Covers the website, the Gumroad store and the launch
sequence. It does **not** cover app source, manuals or the performance work —
those belong to other sessions (see *Who owns what*).

Everything buildable is done. The launch is gated on one thing: an Apple
Developer ID certificate that does not exist yet.

---

## 2026-08-13 — Gumroad kit brought back in sync with the site

User asked to confirm all the day's website content changes are also live on
the Gumroad side. Most already were (taglines, Arranger's absence), but
`gumroad/GUMROAD-KIT.md` still described the old single four-app "Companion
Suite" bundle from before `f57e595` split it into two — that predates every
change in this session and was the real gap.

- **Rewrote the bundle section** of `GUMROAD-KIT.md`: one Companion Suite
  entry → two entries, Creative Bundle (MutationStation + Chordinator) and
  Toolbox Bundle (Spectrl + MidiMirror), copy matching `index.html`'s
  `#bundles` panel word for word, plus the exact Gumroad permalink slugs
  (`creative-bundle`, `toolbox-bundle`) the website's buttons already link to.
- **Updated the profile section order and the cohesion checklist** to match —
  "the Suite" language throughout replaced with "each bundle" / "both
  bundles".
- **Regenerated the local Gumroad art** (`./make-gumroad-art.sh`) so the
  MutationStation and Spectrl cover images carry the current tagline wording
  rather than the pre-edit text baked into the old PNGs.
- `gumroad/` is entirely gitignored (per `.gitignore`), so none of this is a
  commit — it is what actually gets pasted into Gumroad's product editor by
  hand. Nothing on the live site changed this round; no publish needed.
- **Still open:** the actual Gumroad listings for `creative-bundle` and
  `toolbox-bundle` need to exist at those permalinks with this copy pasted in
  — that's a manual step in the Gumroad dashboard, not something a commit
  here can do.

---

## 2026-08-13 — MutationStation tagline tweak

"...and chase acid lines you would not have written" → "...and discover acid
lines you would not have usually written." Updated in the four places it
appears: homepage product card and `apps/mutationstation.html` (both
`index.html`'s repo), plus the untracked Gumroad kit (`gumroad/cover.html`,
`gumroad/GUMROAD-KIT.md`).

- **Published.** `./publish.sh` run.
- Commit: `e8d977d`.

---

## 2026-08-13 — About panel rewritten, version line dropped, Spectrl tagline tweaked

More copy changes from the user, same day as the two batches below:

- **Dropped "All apps are version 1.0.0"** from the Licence &middot; updates
  &middot; refunds panel (`index.html`, `#licence`).
- **Replaced the About panel.** "Why they all look the same" (the shared
  faceplate/one-accent-colour design-language pitch) is gone — the user called
  it uninteresting. In its place, "Built to be used": built for the author's
  own sessions first and sold second, following his own workflow and opinions,
  which is framed honestly as both a possible mismatch for a given buyer and
  the actual point — these are tools built to be used, not commodities built
  to be sold.
- **Spectrl tagline**: "Spectrum, key, note frequencies, ..." → "Spectrum, key
  **detection**, note frequencies, ...". Fixed in three places: the homepage
  product card (`index.html`), Spectrl's own page (`apps/spectrl.html`), and
  the untracked Gumroad kit (`gumroad/cover.html`, `gumroad/GUMROAD-KIT.md`) —
  the user asked for both site and Gumroad.
- **Published.** `./publish.sh` run.
- Commit: `cd5035c`.

---

## 2026-08-13 — Homepage copy: "Ableton Live Companion apps", eyebrow line dropped

Two more copy changes from the user, on top of the same day's Arranger/hero-crop
batch below:

- **Hero claim reworded.** "Standalone Mac apps with the depth of hardware" →
  "Ableton Live Companion apps with the depth of hardware", across the
  `<h1 class="hero-claim">` and the meta description / `og:description` /
  `twitter:description` tags (4 occurrences, `index.html`). The `<title>` tag
  ("JamWare Audio · Standalone Mac apps for music production") is worded
  differently and was left alone — not the string the user named.
- **Dropped the `<p class="legend eyebrow">Standalone tools for macOS</p>`**
  line above the hero heading entirely, per the user's instruction to remove
  it from the front-page title. `.hero .eyebrow` in `styles.css` is a generic,
  reusable rule shared with other uses of `.legend` — left in place.
- This commit also carried the `make-hero.py`/`hero-stack.png` BLEED fix from
  the entry below, which had been made but not yet committed in this repo.
- **Published.** `./publish.sh` run.
- Commit: `222cbf2`.

---

## 2026-08-13 — Arranger pulled off the site, hero cascade crop fixed

The user flagged two live-site bugs from a screenshot, both from the
`35bc8dc` cutout work: the homepage hero (`assets/shots/hero-stack.png`)
had MidiMirror cropped out of frame entirely, and Spectrl was sliced
through the middle of its toolbar instead of along a rounded corner. Also:
Arranger was live on the homepage and had its own product page before
there is anything to sell — should not have been there yet.

- **Hero crop fixed.** `make-hero.py`'s `BLEED` constant was 0.62, on the
  theory that cropping into the back of the cascade made the front window
  read bigger once scaled down to the page's 620px height cap. That theory
  was wrong: the cap scales off the canvas's *height*, and the crop only
  trims width/top, so the front window rendered the same size regardless —
  the only effect of a high BLEED was cropping the back windows out. Set to
  `BLEED = 0` (full cascade, no crop) and regenerated `hero-stack.png`; all
  four windows now show with clean rounded corners and their own drop
  shadow, MidiMirror included.
- **Arranger removed from the homepage**, not just relabelled: pulled its
  product card, deleted `apps/arranger.html`, and fixed the Toolbox
  Bundle's copy/icon-row/price line, which used to read "Spectrl, MidiMirror
  and Arranger" — it's a two-app bundle (Spectrl + MidiMirror) until
  Arranger actually ships. Also dropped `arranger` from the untracked
  Gumroad art tooling (`gumroad/cover.html`, `gumroad/make-gumroad-art.sh`)
  so that local kit doesn't generate art for an unlisted product either.
- **Published.** `./publish.sh` run; live site is at `00dd201`.
- Commit: `00dd201`.

---

## 2026-08-13 — 3D nameplate work tried and retired, two bundles replace the Companion Suite, a review pass, the cutout fix, and a stale publish caught

Catch-up entry: six commits (`43b6328`..`35bc8dc`) had landed in this repo with
no handoff section written for any of them, and the live site had not been
republished since `43b6328` — so the cutout fix below was sitting unpublished
while the user was looking straight at the bug it was meant to fix. Both gaps
are closed now: this section, and `./publish.sh` run at the end of it.

- **Three attempts at giving the site physical depth, all rejected, now
  deleted** (`9dd1649`→`fb71f78`, retired in `4b65935`): a CSS/PIL hardware
  chassis around the screenshots, extruded-screenshot renders (rejected because
  treating a whole app window as the render subject gives hundreds of elements
  uniform micro-relief and warps legend text at any raking angle), and a
  modelled-metal nameplate built as real Blender geometry (anodised plate,
  boolean-cut wordmark, DIN type) — closer, but never placed on any page before
  the whole direction was dropped. **This site engraves only; it does not
  emboss** — a raised/embossed treatment was tried as `.engraved`'s mirror and
  rejected too, and both dead rules carry do-not-reintroduce comments rather
  than being silently deletable-and-forgettable. Render assets and both render
  rigs are gone.
- **The Companion Suite (all four apps, one price) is replaced by two bundles**
  (`f57e55f`): **Creative** (MutationStation + Chordinator — the two that write
  notes) and **Toolbox** (Spectrl + MidiMirror + Arranger — the three that
  handle the session around them). The old bundle asked a first-time visitor to
  commit to everything at once and lumped two different buying reasons into one
  price. ⚠ **Neither Gumroad product exists yet** — `/l/creative-bundle` and
  `/l/toolbox-bundle` are linked from the site but 404 until created.
- **Site review pass** (`aed594e`): OG/Twitter social cards on all six pages
  (every link pasted anywhere had been previewing as a blank box — there were
  no `og:`/`twitter:` tags at all); a licence/updates/refunds panel (three
  machines, deactivate-and-regenerate on a Mac move, 14-day EU refund window —
  ⚠ **no activation code exists yet, the panel says so in a comment**); version
  1.0.0 stated on the four released app pages; "small" dropped from the About
  copy (the same pricing-down problem the headline rewrite already fixed once);
  real favicon (company mark, not MutationStation's icon, on the homepage only
  — app pages correctly keep their own icons); hero cropped tighter for
  legibility (windows were rendering under half their designed size); mobile
  header/button/scroll-repaint/overflow fixes, verified overflow-free at 390px
  on all six pages. Prices and an update feed were explicitly deferred by the
  user, not forgotten.
- **The screenshots came out of the dark recess** (`35bc8dc`, the fix the user
  asked about): the `.screen` inset was borrowed from the apps' own dark
  analyser/piano-roll panels — right for UI-inside-an-app, wrong for a picture
  of a whole app, since it wrapped a black rectangle around a cream window and
  made every page read as a dark card on the plate instead of a window lying on
  it. Screenshots now sit directly on the faceplate with `filter:
  drop-shadow()` (not `box-shadow`, which traces the bounding box and would
  print a hard square behind the corners the cutout just made transparent).
  New `make-cutouts.py` re-masks each full-window capture to a rounded
  rectangle (antialiased, 4x-supersampled, radius scaled to each capture's own
  width) because macOS rounds a window's corners but a screenshot flattens
  whatever was behind them into the file — `chordinator.png` and
  `mutationstation.png` had pure black baked into all four corners,
  `midimirror.png` a grey desktop. Idempotent, safe to rerun after any
  recapture. ⚠ **The hero composite is deliberately not in its list** —
  `make-hero.py` bakes its own shadows between the stacked windows, so running
  the cutout mask over it would double up. `.screen.empty` is untouched and
  keeps the dark inset — the arranger page has no window to cut out, and bare
  text on the plate needs to read as a filled panel, not a gap waiting for one.
  Also fixed in the same commit: a 3px horizontal overflow on the
  MutationStation page at 371px (one unbreakable 15-character name at a fixed
  width next to an 88px icon).
- **Republished.** `.public-mirror` was six commits stale (last publish
  `43b6328`); `./publish.sh` run after this entry brings
  `jamwareaudio.github.io` up to `35bc8dc`. If the black corners are still
  visible, it's GitHub Pages' redeploy lag (a minute or two), not a code gap.

---

## 2026-08-13 (later still) — The site has a short URL: `https://jamwareaudio.github.io/`

The old address was `toastonjam-debug.github.io/jamwareaudio-site/`, which the
user called out as long and, fairly, as not reading like a company — it had
"debug" in it. Two separate problems lived in that string and they had different
fixes:

- **The `/jamwareaudio-site/` path segment** exists because GitHub serves a
  repository at the domain *root* only when it is named exactly
  `<account>.github.io`. Any other name is a project page one segment deeper.
- **`toastonjam-debug`** is the account name and nothing about the repository
  could change it.

So both were renamed, and they have to match. The account rename
(`toastonjam-debug` → `jamwareaudio`) was the **user's own action in GitHub's web
UI — there is no REST endpoint for changing your own login**, so do not go
looking for one. The repo rename and everything downstream was scripted.

⚠ **Do not rename the public repo.** `jamwareaudio.github.io` is load-bearing;
renaming it silently puts the path segment back.

**What moved with it:** eight git remotes (all seven lanes plus the
`.public-mirror` checkout), `publish.sh` (`REPO=` and the URL it prints),
`site/README.md`, this file, root `CLAUDE.md`, `releases/README.md` and
`workspace/BOARD.md`. **No published page referenced the URL**, so the site's own
HTML needed no edit.

Verified after republishing: `/`, `/styles.css`, `/apps/spectrl.html` and
`/assets/shots/hero-stack.png` all `200`; `/README.md`, `/CLAUDE.md`,
`/HANDOFF.md` and `/publish.sh` all `404` — the allowlist fence survived the move
intact, which was the thing worth checking.

⚠ **The old URL is dead, not redirected** — `404`, no `Location` header. GitHub
redirects renamed *repositories*, but a `<user>.github.io` domain simply stops
existing when the user is renamed. Worse, the freed `toastonjam-debug` username
is claimable by anyone, so even the repo-level redirects are on borrowed time.
Anything already sent out carrying the old link should be reissued rather than
left to a redirect that may one day land on a stranger's account.

**The four Gumroad descriptions are the live instance of that** and are still
untouched (browser not connected), so when they are next edited, check them for
the old URL as well as for the de-AI pass below.

Not done, and it is the better answer if it ever comes up again: a real domain.
`jamwareaudio.github.io` still reads as a GitHub page. The DNS steps are in
`README.md` under *A custom domain*; the purchase is the user's to make.

---

## 2026-08-13 (later) — Cascaded hero, the stale spec strips are gone, and a de-AI pass over every word on the site (`c0bee4d`)

Three items from the user, all three shipped and live. The em-dash item is the
one with a long tail, so read that part before writing any new copy here.

### 1. The hero is no longer one Spectrl window

`make-hero.py` builds `assets/shots/hero-stack.png` from the four existing
captures: four windows cascaded back-to-front, **MutationStation in front and
Chordinator immediately behind it**, which was the brief. The script's header
carries the reasoning at length; the short version is that a lone spectrum
analyser was the wrong first impression for a company selling four tools, and
depth ordering is what does the ranking.

⚠ **Do not hand-edit the PNG — re-run `./make-hero.py`.** The four source
captures disagree with each other (two RGB with the corners already flattened to
black, one RGBA with real transparent corners, one full-retina and
square-cornered), so every window is rescaled to one width and re-masked with
the same radius. That uniform re-mask is why the stack reads as four windows on
one desktop rather than four screenshots taken on four different days. The
output background is transparent on purpose: it nests in the site's dark
`.screen` recess, and a baked-in colour would show as a rectangle the moment
that recess changes.

### 2. The spec strips are gone, and the CSS rule went with them

The `.specs` badge rows came off all five product pages, and the `.specs` rule
was deleted from `styles.css` and replaced with a comment saying not to
reintroduce it. This is the *same* correction the user had already made once
against the Gumroad covers, and it had been missed here — worth knowing, because
the reason generalises:

- A finite row of badges reads as *the* feature list. Every one of these apps
  has more in it than three chips, so the strip actively undersold them.
- One of the three chips was `macOS · Apple Silicon`, which is a system
  requirement and not a reason to buy anything.

### 3. The de-AI pass — and the rule for anything written here from now on

The user's words: *"avoid ai tells, like long - . Make it seem human written."*

**The em dash was the tell.** Every one in reader-visible copy is gone from all
six pages. What replaced it was chosen per sentence, never by find-and-replace,
because a blanket swap to a comma produces its own tell:

- In titles and `panel-head` bands → `·`, which is **already this site's own
  separator** (the footer legend and the suite price both used it before this
  pass). Nothing new was invented.
- Mid-sentence, where the dash introduced an explanation → a colon, or a full
  stop and a new sentence. Several of these read better short.
- Around an aside → parentheses, or commas where the aside was brief.

⚠ **Five em dashes remain in `index.html` and all five are inside HTML
comments.** That is house style for the WHY blocks and readers never see them.
Do not "finish the job" by stripping those.

**The bigger tell was not punctuation, it was repetition.** The identical
sentence *"Two independent programs talking over MIDI beats one process that
takes both down when either one stumbles."* closed the "Why standalone" section
on three different product pages, word for word. Anybody who opens two pages
sees it instantly, and it is a stronger generated-copy signal than any dash.
Each is now written in that app's own terms. **Do not reintroduce shared
boilerplate across the product pages** — if a paragraph is worth saying on three
pages, it is worth saying three different ways.

Also checked and clean: no en dashes anywhere, and a grep for the usual vocabulary
tells (`seamless`, `effortless`, `unlock`, `elevate`, `robust`, `leverage`,
`cutting-edge`, `delve`, `whether you`, `isn't just`, …) found nothing. Three
uses of "not just" survive and were left deliberately — all three are natural
("Reads in notes, not just hertz").

Register, from the user, and it governs everything above: **"They are tools, not
ai doing the work for you."** No copy here should imply the app is making the
music.

### ⚠ Still owed: the Gumroad half of item 3

The user asked for the de-AI pass over **"gumroad and website"**. Only the
website half is done. The four descriptions — MidiMirror `ohhpmz`, Spectrl
`zpedfw`, Chordinator `ztjqq`, MutationStation `gligmk` — still carry the old
prose, so the store and the site now disagree with each other.

It is blocked on the browser: the Claude Chrome extension was not connected this
session (`list_connected_browsers` returned empty), and there is no other way
into that editor.

**When it is connected, the method is the one already documented below** under
the Gumroad editor section — every trap in it still applies, in particular that
the save interceptor must swap on **any** body containing `"description"` and
must never filter on the request URL. The specific plan:

1. Read each description's current HTML straight out of the editor.
2. Apply the *same* substitutions already made to the matching
   `site/apps/*.html`, as targeted text-only replacements.
3. Swap it in through the `fetch` / `XMLHttpRequest` interceptor.

Step 2 being text-only is the important part: it leaves every image node in the
description untouched, so **nothing has to be re-uploaded**. Rebuilding the HTML
from scratch would mean re-running the whole blob-key dance for no reason.

⚠ All four listings are still deliberately **unpublished**. Click only **Save
and continue**. Never the pink **Publish and continue** — publishing is the
user's own job in their own browser. And nothing is to be done about TouchXY:
*"Let's wait with uploading touchxy. I wanna release ur a bit later."*

---

## 2026-08-13 — The site is on the web, the buy buttons became an overlay, and `git push` no longer publishes anything

**THE SITE IS LIVE:** `https://jamwareaudio.github.io/`
Verified after the first Pages build — `/`, `/styles.css`, `/apps/midimirror.html`
and a screenshot all `200`; `/README.md`, `/CLAUDE.md` and `/HANDOFF.md` all
`404`, which is the entire point of the arrangement below.

### ⚠ Read this before you push: there are now two repositories

| Repository | Visibility | Role |
|---|---|---|
| `jamwareaudio/jamwareaudio` | **private** | `site/` — the real work |
| `jamwareaudio/jamwareaudio.github.io` | **public** | build output only |

Pages on the free tier serves only a *public* repository, and serves every file
in it. This directory is a working lane as well as a website — `CLAUDE.md`,
`HANDOFF.md`, `README.md` — so making `jamwareaudio` public to obtain a URL
would have published the lane rules, every session note and the go-live
checklist, history included, in order to save copying six files. Visibility is a
property of a repository and not of a branch, so branch tricks do not help and
the split had to be a second repo.

**`git push` in `site/` publishes nothing now.** `./publish.sh` does. It copies
an **allowlist** — `index.html`, `styles.css`, `apps/`, `assets/` — into a
gitignored `.public-mirror/` checkout and pushes that. The script's header
argues the allowlist at length and it is worth not undoing: the obvious
inversion, copy-everything-minus-the-internal-files, **fails open**. The day
someone drops a `NOTES.md` or a `.env` in here an exclude list publishes it and
nobody finds out. An allowlist fails closed — a new page is simply missing from
the site, which is a bug you notice rather than one a customer notices for you.

The public repo is output, not a workspace: `publish.sh` overwrites it wholesale
and anything edited there is lost. A `CNAME` for a custom domain is the one
exception and belongs in `.public-mirror/`, where a republish leaves it alone.

⚠ **This is the first public repository in the tree**, against the standing
"every JamWare repository is private" rule. It was the user's explicit choice
after being shown what going public would expose, and it holds no app source —
only the rendered website. The rule stands for all seven others.

### The buy buttons open a Gumroad overlay now (`0d1a626`)

All nine "Get it" anchors carry `class="btn gumroad-button"` and every page loads
`gumroad.js`, so checkout opens as a modal *over* the site rather than sending
the customer to gumroad.com — the user's ask was to make buying "as quick and
smooth as possible". The anchors keep real `href`s, so a blocked or changed
script degrades to the plain links the site already had; no state leaves a
button dead. Gumroad's *inline* embed was rejected: it renders the whole product
box into a div, duplicating copy already written here and ignoring the layout.

**The styling guard in `styles.css` was written against the real CSS, not
guessed.** `gumroad.js` is a 539-byte loader that appends
`assets.gumroad.com/vite/assets/entrypoints/overlay-<hash>.css`; that URL needs
no published product, so it was fetched and read. Two findings a guess would
have missed, both now answered:

- Its `:hover`/`:active` rules are one pseudo-class *more* specific than a base
  rule, so they would have won — the button would slide up-left a quarter rem on
  hover, grow a hard offset shadow and turn pink. Hence the explicit
  `a.btn.gumroad-button:hover` / `:active` rules mirroring `.btn`'s.
- ⚠ **Gumroad sets `--accent: 255 144 232` on `.gumroad-button` itself.** Any
  `var(--accent)` in a rule targeting that element resolves against *that* — and
  a bare `255 144 232` is not a colour, so our gradient and border would not go
  pink, they would fail to parse and vanish, leaving a transparent button. The
  guard reads `--btn-accent` instead, copied off `.btn-row` one level up where
  Gumroad's rules cannot reach. **Do not "simplify" it back to `var(--accent)`.**

**Still unverified, and unverifiable for now:** that the modal actually opens.
An unpublished product's `/l/<slug>` 404s for anyone but the seller, and a modal
onto a 404 is indistinguishable from a broken one. It is a launch-day check in
`README.md`.

### What the live site is, honestly

A preview. The four Gumroad listings remain **unpublished** by standing
instruction, so every buy button 404s for the public — the user was shown this
and chose to go up anyway to see the thing. Publishing the listings is theirs to
do in their own browser, and it is the last step before the site is a shopfront
rather than a brochure. The Apple Developer enrolment blocker is unchanged.

Also decided, and recorded in `README.md`: **Gumroad Pages is not being used** —
it would be a second, weaker copy of this site to keep in sync. The *profile*
page at `jamwareaudio.gumroad.com` is still worth setting up so a trimmed URL or
a receipt link lands on the four products.

---

## 2026-08-13 — MidiMirror: per-device saved order promoted, every Device-mode shot recaptured against an instrument, the drop shown at last

**The user's instruction was flat: not a single MidiMirror screenshot may show
the Pitch MIDI effect as the addressed device.** Pitch is a three-parameter
utility, so a Device-mode shot built on it makes the feature look thin — the
knob row reads "Pitch, Pitch, Lowest, Range" and the mapping screen offers a
handful of parameters where a real instrument offers ninety-two. Everything was
recaptured against a plain Wavetable on its own track, so the deck header reads
3-WAVETABLE / Wavetable and the swap bar's button reads **Remember this order
for Wavetable** — which is the point of that panel, since the order key is the
Live device display name (`MidiMirror/visualizer/swap.js` around 265).

Three commits in this lane: `96de644` promoted the per-device saved-order copy
into its own panel high on `apps/midimirror.html` (the user's own bullet,
lightly edited — it had been a trailing `li` on Gumroad and absent from the site
entirely); `1323849` replaced the shots and rewrote every alt and figcaption
that named Pitch.

| `assets/shots/` | Size | State |
|---|---|---|
| `midimirror.png` | 3456x2016 | already Wavetable, untouched |
| `midimirror-knobs.png` | 1979x738 | already Wavetable, untouched |
| `midimirror-modes.png` | 447x1279 | side panel only, untouched |
| `midimirror-order.png` | 2532x500 | **recaptured** |
| `midimirror-mapping.png` | 3426x1992 | **recaptured** |
| `midimirror-map-dialog.png` | 1448x784 | **recaptured** |
| `midimirror-drop.png` | 3408x742 | **new** |

The drop shot is taken deliberately mid-move: the drop is held, then six knobs
and a fader were dragged away from where they were stored, so the orange pip
sits visibly apart from the pointer instead of hiding underneath it. A shot
taken straight after arming looks like nothing happened, which is exactly the
failure the paragraph beside it is trying to explain. The page had described
snap-back in prose since it was written and never once showed it.

**Gumroad `ohhpmz` is in step with the page.** Seven images now, four of them
uploaded this session; the two old *Pitch* blobs that were still live (the
picker and the mapping screen) were swapped out too, which is easy to miss —
the placeholder keys in the staged description were not the only ones that
needed replacing. Verified after a reload: 7 images, zero occurrences of
"Pitch", captions matching the site's. Still **unpublished**; only "Save and
continue" was clicked.

### Two capture lessons worth more than the shots

- **`screencapture -x -o -l<windowid> out.png` grabs the window's own backing
  buffer**, so an overlapping window no longer ruins the frame. Window ids come
  from `Quartz.CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, …)`,
  which returns front-to-back z-order with `kCGWindowNumber`, owner name and
  bounds in *points*. This removes the entire class of retakes lost to the
  Claude desktop window raising itself, and it crops to the target window by
  construction — which is also the privacy-safe default after the full-screen
  capture that once caught the user's Mail app mid-search.
- **Display scale here is exactly 2.0.** Points are real pixels halved;
  framebuffer 3456x2234, desktop bounds 1728x1117. The figure 1.728 that an
  earlier session used as a scale factor is the screen *width in points*, and
  reading it as a ratio is what made every click miss.

Two traps that cost time and will again:

- **`cliclick` clicks go to whatever is topmost at that point.** A full-screen
  MidiMirror window silently ate every click aimed at Live behind it, including
  a `kp:delete` meant for a track. Check with
  `osascript -e 'tell application "System Events" to name of first process whose frontmost is true'`
  before trusting a click, and quit the app in front rather than trying to raise
  the one behind (root `CLAUDE.md` §5 — MidiMirror cannot be raised by
  `activate`).
- **The Gumroad save interceptor must not filter on the request URL.** The
  version documented below matched only URLs containing `/products/`; the real
  save goes out somewhere else, so it sailed past unpatched and committed the
  raw editor body — four freshly uploaded images dumped at the caret, on top of
  the old ones. Swap on *any* body whose string contains `"description"`
  instead, and treat an empty `window.__hits` after a successful save as a
  failure even when the URL moves `/edit` → `/edit/content`. Recovery is just a
  reload and a second attempt; the damage is only ever one bad description.
- The first click on "Save and continue" often does nothing and the second one
  saves. Also: `computer` coordinates are screenshot pixels (1528 wide here),
  not CSS pixels (1728) — multiply a `getBoundingClientRect()` result by ~0.884
  before clicking it.

The machine was left as it was found: the drop released so every Live value
snapped back, MidiMirror quit, and the temporary "3 Wavetable" track deleted
with the user's own two tracks and their automation intact.

---

## 2026-08-13 — Feature gaps filled, zoom crops added, all four Gumroad descriptions rewritten from the site pages

**The site and Gumroad now carry the same text.** This was the session's whole
job: audit each app's copy against its actual feature set, add zoomed-in
screenshots tied to specific descriptions, and make the store match the site.

**On the site** (`0c7aa37`, and `8af604b` before it): every product page had its
feature list checked against the app's own manual and its gaps filled, and each
page gained 2–3 `figure.zoom` crops sitting immediately beside the paragraph
they illustrate — not decorative, each one is the thing the sentence above it
describes. The crops live in `site/assets/shots/` (12 new files) and the
`.zoom` rule is in `styles.css`. `index.html` cards and `apps/*.html` taglines
agree.

**On Gumroad**, all four descriptions were replaced wholesale with prose derived
from the matching `site/apps/*.html`, each with its images inline:

| App | ID | Nodes | Images |
|---|---|---|---|
| Chordinator | `ztjqq` | 31 | 5 |
| MutationStation | `gligmk` | 26 | 5 |
| Spectrl | `zpedfw` | 21 | 4 |
| MidiMirror | `ohhpmz` | 30 | 5 |

All four verified after a reload — node structure, image natural sizes, caption
counts. Each also picked up the Gatekeeper paragraph (ad-hoc signing, right-click
→ Open) and the support address, which the site pages do not carry.

Two Gumroad-specific fixes went in along the way: Spectrl's "Why standalone"
body had been mis-tagged as an `<h3>`, and MidiMirror's had the same problem —
both are `<p>` now.

⚠ **All four remain unpublished.** Only "Save and continue" was ever clicked;
the pink "Publish and continue" was deliberately left alone. Spectrl was already
unpublished before this session.

### How to edit a Gumroad description again — read this before trying

The obvious route does not work and costs an hour to rediscover:

- **`<img>` tags are stripped from pasted HTML.** Images must be uploaded through
  the editor's own toolbar file input to get a CDN URL. Click into the editor
  body to place a caret, click "Insert image" at ~(551, 305), then `find` the
  hidden file input — the *first* ref returned is Insert image, the second is
  Insert video/audio — and `file_upload` to it. Wait ~10 s.
- **Uploads fail silently and intermittently** (Gumroad 502/504 on
  `/rails/active_storage/direct_uploads`). One crop needed four attempts. Verify
  by comparing each `img.naturalWidth x naturalHeight` in the editor against the
  local PNG's real size; retry whichever is missing.
- **Scripted upload from a local HTTP server is dead** — Gumroad's CSP blocks
  `connect-src` to `127.0.0.1`. Do not spend time on it again.
- **The working method** is to upload the images, collect their blob keys, build
  the full HTML in `window.__desc`, then monkey-patch `window.fetch` and
  `XMLHttpRequest.prototype.send` to swap the `description` field in the app's
  own save request. That preserves `editor_revision`, which a hand-rolled POST
  would not.
- **The save only fires if the form is dirty**, and dirtying it is the fiddly
  part. Clicking a fixed coordinate usually lands on an image node, where typing
  does nothing. Place the caret via a real `<p>`:
  `pm.children[3].scrollIntoView({block:'center'})`, click at its rect + (40, 10),
  then type a space.
- **The scroll container is `<main>`, not the document.**
  `document.scrollingElement.scrollTop = 0` does nothing, the Save button stays
  off-screen, and the click silently misses. Walk up from `.ProseMirror` to
  `MAIN` and set *its* `scrollTop`.
- **Reloading discards unsaved edits** and wipes the patch, so install the
  interceptor only after the last reload. Proof of a save is the "Changes saved!"
  toast plus the URL moving `/edit` → `/edit/content`.
- **The Summary field does not save on the first click.** Use React's native
  `HTMLInputElement.prototype.value` setter plus `input`/`change` events, and
  re-read it after a fresh reload — the live preview pane is *not* proof.

**TouchXY is still on hold** at the user's instruction: no listing, no art, no
action until they say so.

**Next session:** the Apple Developer enrolment blocker below is unchanged and is
still the only thing standing between these listings and a customer who can
actually open the app.

---

## 2026-08-13 — Taglines rewritten, spec strip cut, art pushed live to Gumroad

**The covers are now on Gumroad.** Four listings — MidiMirror (`ohhpmz`),
Spectrl (`zpedfw`), Chordinator (`ztjqq`), MutationStation (`gligmk`) — each got
its new 1280×720 cover and 600×600 square thumbnail from
`site/gumroad/out/`, old art deleted, saved without publishing. All four read
`Unpublished` on the Products page as of this session's end. MutationStation was
the one that had been `Published`; the user asked for it to be unpublished and
it now is.

**The taglines were rewritten twice.** The first pass was rejected outright, and
the reason is the part worth keeping: the copy was written in a
"without-doing-it-yourself" register — as if the app does the work for you. The
user's words were *"They are tools, not ai doing the work for you."* The second
pass was written only from features that actually ship, read off each app's own
`site/apps/*.html`, rather than invented from the app's name. Do not write these
from imagination; the failure mode is not clumsy prose, it is claiming the wrong
thing about the product. Final copy lives in the `APPS` table in
`site/gumroad/cover.html`; MidiMirror's and Chordinator's were supplied by the
user directly.

**The spec strip is gone**, and the WHY is recorded at length as a comment in
`cover.html` (the `.specs` CSS block was replaced by it) — briefly: a finite row
of badges reads as *the* feature list, which undersold apps that have far more
in them. Note this reverses the user's own earlier "add all features" request;
they reversed it themselves once they saw it rendered. The `macOS · Apple
Silicon` badge went with the strip.

**MidiMirror's Gumroad description was also corrected** — it still said only the
Akai MIDI Mix had a ready-made script. Both stale sentences (the body paragraph
and the Requirements paragraph) now match the three-controller wording in
`site/apps/midimirror.html:110-115` and `:231-236`.

**The screenshot and the taglines were then swept too**, in the same session,
after the two items below had first been *reported* as open rather than done.
They are finished now; what follows replaces the "open, deliberately not acted
on" list this section used to carry.

- **MidiMirror's description screenshot is swapped.** The stale 2000×1166
  "Pitch Tool" capture is gone; `site/assets/shots/midimirror.png` (3456×2016)
  is in its place. Verified on reload: the description holds exactly two images,
  3456×2016 and 3456×2018.
- **The taglines are one wording everywhere.** `site/index.html` cards,
  `site/apps/*.html` heroes, `site/gumroad/GUMROAD-KIT.md` Summary lines, and
  the live Gumroad **Summary** field on all four listings now all match the
  `APPS` table in `cover.html`. Committed as `8af604b` (the `GUMROAD-KIT.md`
  half is not in that commit — `site/gumroad/` is gitignored). The bundle
  listing's Summary ("All four apps. One purchase.") was left alone on purpose;
  it is not one of the four app taglines.
- **TouchXY stays on hold** — the user's standing instruction is to release it
  later. No listing, no art upload.

⚠ **Behavioural note, and this is the reason the section had to be rewritten.**
The user's response to seeing those two items listed as "flagged, not acted on"
was *"why are you not following my orders"* — and they had already given the
same correction once before. **When the follow-through on a task is obvious, do
it.** Reporting the obvious next step back to them as a decision reads as
refusing to finish the job, not as diligence.

**Reusable: the Gumroad Summary field does not save on the first click.** The
Summary is a plain `<input type=text>` under "Product info", and setting it
through the tooling's `form_input` updates the preview pane live — which makes
it look saved when it is not. Three of the four listings silently kept their old
Summary through a reload. Two things fix it: write the value with React's own
native setter (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,
'value').set` + `input`/`change` events) so the editor's state actually changes,
and then **click "Save and continue" until the URL moves from `/edit` to
`/edit/content`** — that transition, or a `POST` to `gumroad.com/links/<id>`,
is the only reliable evidence the save fired. The first click after a page load
routinely does nothing at all. **Always re-read the field after a reload before
calling it done**; the preview pane is not proof.

**Reusable: how the Gumroad cover upload actually works.** It is not obvious and
cost most of a session to work out. Scroll the Cover section into view *first* —
clicking "Add cover" without doing so scrolls the page to the top and silently
closes the popover. Then "Add cover" → "Upload images or videos" → "Computer
files", clicking each by ref through the `computer` tool, never via JS
`.click()`, which loses the popover the same way. The real `<input type=file>`
is nested inside the "Computer files" `<label>`, so a `find` query has to be
specific enough to return the input and not its wrapper; naming the accept types
in the query works. Never click a file input — that opens a native picker
nothing can see. To delete the old cover, click its thumbnail to select it and a
small red ✕ appears just above and right of it. The square thumbnail is a
separate "Thumbnail" section with its own Remove button and its own file input.

---

## 2026-08-12 (later) — Cover/thumbnail copy rewritten for full app scope, MK3 mention added

The user pushed back that cover/thumbnail short descriptions stated only one
generic aspect of each app (their MidiMirror example: the cover text made it
sound like just a display, when it is much more). Fixed after a full survey of
all 5 apps' real current feature sets (five parallel background survey agents,
grounded in `docs/MANUAL.md`, `HANDOFF.md` and source, not the existing site
text).

**MutationStation had the biggest gap** — the existing blurb covered only
mutation/rhythm/pitch and omitted three real feature areas entirely: live
recording (Record / Overdub / Recapture, Chord In / Root In), bidirectional
Live import (↓ From Live, ↓ Rhythm Import, Send to Live / Replace clip), and
up to 8 modulation lanes as 14-bit device automation. Added to `index.html`'s
card, `apps/mutationstation.html` (two new feature bullets, expanded "Particular
integration with Live" panel), `gumroad/cover.html`'s tagline/specs, and
`gumroad/GUMROAD-KIT.md`'s Description block. Also corrected the pitch-strategy
count "30+" → the exact **33** (counted `<li>`s in `docs/MANUAL.md`) everywhere
it appears.

Chordinator and Spectrl blurbs were smaller gaps (harmony-engine/suggestions,
key-detection) and were fixed the same way earlier in this session.

**New from the user mid-session**: MidiMirror will ship with a ready-made
Novation Launch Control MK3 script (not yet in `MidiMirror/` source — this is
forward-looking, supplied directly by the user, confirmed via grep that it
isn't there yet). Added the MK3 mention to `apps/midimirror.html` (the "ready-
made script" paragraph and the Requirements panel) and to `GUMROAD-KIT.md`
(Description + `launch control` tag). While there, also fixed an independently
stale claim in `GUMROAD-KIT.md`'s MidiMirror section and its Companion Suite
bundle section — both said "requires... an Akai MIDIMIX" as a hard
requirement, which was already untrue on the website itself (any controller
works via Learn) before the MK3 addition made it doubly wrong.

Regenerated all Gumroad cover/thumbnail PNGs via `gumroad/make-gumroad-art.sh`
(local-only, headless Chrome, safe to re-run) so `gumroad/out/` matches the new
`cover.html` taglines/specs.

**Not done**: nothing pushed to the live Gumroad listing (browser-permission-
gated — `GUMROAD-KIT.md` is the local source of record, not the live page).
TouchXY still has no listing anywhere on the site or Gumroad — flagged to the
user in a prior segment, not acted on without an explicit instruction.

**Update, same day**: the user set up Live with Wavetable loaded and MidiMirror
connected in Device mode and said so ("Live is running and wavetable is in
focus as device"). Captured the new screenshot — no dedicated native-GUI-
automation tool exists in this session, so it was assembled from raw
`osascript` (window bounds via System Events) + `screencapture -R<region> -x`
(capture just that window) + `cliclick` (found at `/opt/homebrew/bin/cliclick`,
used to move the pointer out of frame and clear a lingering tooltip before a
clean recapture). Result: `site/assets/shots/midimirror.png` replaced —
Device/Track mode, Wavetable in focus ("8-WAVETABLE Wavetable" panel, orange
device-select highlight), no stray UI. Alt text in `apps/midimirror.html`
updated to match. **Handed off to `midimirror`** via a `workspace/BOARD.md`
Queue entry: the same screenshot is meant to replace
`MidiMirror/docs/img/01-device-mode.png` (referenced at `docs/MANUAL.md:53`),
per the user's instruction that this become the screenshot used everywhere,
manual included — `web` cannot write into `MidiMirror/docs/` directly, so the
Queue entry is the handoff mechanism. Not yet done: pushing this screenshot to
the live Gumroad listing (same permission gate as the copy); whether the
second MidiMirror screenshot on the site, `midimirror-mapping.png`, also needs
a retake was not investigated this round.

---

## 2026-08-12 — MidiMirror mapping screenshot added, site text synced to revised Gumroad copy

The user hand-edited the Gumroad MidiMirror listing further and asked for a
screenshot of the mapping screen plus a site/Gumroad text sync in that
direction (Gumroad → site this time, reverse of the Spectrl entry below).

Captured a screenshot of the "Knob · strip 1" mapping dialog (Learn from Live /
Device Parameter / The Device Itself sections) from the running app and saved
it as `site/assets/shots/midimirror-mapping.png`. Added it to both the site
(`apps/midimirror.html`, new `<section class="section wrap">` right after the
existing `midimirror.png` screenshot) and to the Gumroad listing's description
editor, inserted after the "Double-click any control…" paragraph.

Site copy then rewritten to match the user's revised Gumroad text verbatim:
tagline, both lede paragraphs, trims to "A controller you design yourself"
and "The drop", "What it does" renamed to "What else is in it" with its bullet
list shortened (three bullets dropped, others trimmed), and the Requirements
panel's opening paragraph shortened. Left alone on purpose: the site-only
"Setting it up" panel (Gumroad has no equivalent section) and the `<meta
name="description">` SEO tag.

Site: `cc48b52`. Gumroad (`products/ohhpmz`) edited directly in the rich-text
editor — image inserted via the hidden file input (`mcp__claude-in-chrome__
file_upload`, ref `ref_66`), not the toolbar button, which opens a native file
picker the browser tool cannot see or drive — then saved, confirmed by the
"Changes saved!" toast.

---

## 2026-08-12 — Spectrl key-detection and system-audio-capture copy fixed

Two of Spectrl's feature bullets were imprecise to the point of being wrong
about what the features do. "Tells you the key" now says what actually
happens: press a button, the Scale panel listens to 10 seconds of incoming
audio, then shows the predicted key. The old "Records to WAV" bullet undersold
the actual feature — one-click capture of anything playing through the Mac,
no routing or extra software — so it's rewritten as "Samples anything your Mac
is playing, in one click," and both points are now also folded into the
`.lede` intro so they read before the bullet list, not just inside it.

Site copy at `site/apps/spectrl.html`, committed in `14311c2`. Gumroad
description (`products/zpedfw`) edited directly in the rich-text editor and
saved — verified verbatim match against the site's lede and both bullets per
the "we want it consistent" rule.

Note for next time editing the Gumroad rich-text editor: shift-click / shift+
End to extend a selection across a paragraph is unreliable here — it can
auto-scroll and select everything down to near the end of the document, which
on one attempt this session caused an accidental mass-deletion (recovered with
Cmd+Z, no lasting damage). **Triple-click to select a single paragraph or
bullet** instead; it worked cleanly every time. A `shift`-modifier `left_click`
from a plain click point (not combined with `Home`/`End`) was fine for
bold/unbold spans within a single already-selected block.

---

## 2026-08-12 — Spectrl pitch rewrite, "Why standalone" on all four listings

**Spectrl's Gumroad + site intro rewritten** away from "standalone device" and
onto the actual pitch: five tools reading one signal (spectrum with note
mapping, key detection, loudness metering, oscilloscope, tonal-balance
targets) instead of five plugins. Site copy at `site/apps/spectrl.html`'s
`.lede`; Gumroad description matched verbatim.

**Added a "Why standalone" panel to all four app descriptions** — Spectrl,
Chordinator, MutationStation, MidiMirror — on both Gumroad and the site, sitting
directly above "Requirements" in each. Same two points everywhere, phrased per
app: a DAW/Live crash doesn't lose the app's work and vice versa, and the app
talks to the DAW the way outboard/MIDI hardware would (virtual MIDI port for
Chordinator/MutationStation, Remote Script for MidiMirror, Core Audio tap for
Spectrl, framed as "cuts both ways" rather than crash-recovery since it has no
DAW connection to lose). TouchXY excluded — no Gumroad listing, not on the site.

Site changes committed in `88fa771`. Gumroad listings edited directly through
the product editor (rich-text, not source-controlled) and saved individually:
Spectrl, Chordinator (`products/ztjqq`), MutationStation (`products/gligmk`),
MidiMirror (`products/ohhpmz`). Verified the "Why standalone" text on all four
Gumroad listings is verbatim identical to the corresponding site panel, per the
user's "we want it consistent" instruction.

Nothing left half-done here. Next open item for this lane is still the Apple
signing blocker in §1 above.

---

## 1. The one blocker

**No code-signing certificate exists.** `security find-identity -v -p codesigning`
returns `0 valid identities found`.

The user is enrolling in the Apple Developer Program as an **individual** (chosen
over Organization: no D-U-N-S needed, approval in hours rather than weeks, and
for apps sold direct the name on the cert is invisible to buyers).

**Enrolment is stuck on identity verification.** The Apple Developer app offers
*driver's licence only*, and the user does not hold one. They are in **Sweden**
(+46 trusted number), where passports and national ID cards are standard, and
Apple's own docs say passports are accepted in most regions. There is a
documented escape hatch — Apple's identity-verification page says *"To verify
using a method other than the Apple Developer app, contact support."*

**Next action, user's:** contact <https://developer.apple.com/contact/> and ask
to verify by passport. Framing that works: *individual enrolment, Sweden, the
Developer app only offers driver's licence, I hold a passport, please verify me
another way.*

Two-factor auth is already enabled on the Apple ID, so that prerequisite is met.
There is no separate "developer account" to create — the ordinary Apple ID
becomes one on first sign-in at developer.apple.com.

⚠ **Do not ship unsigned.** The current artifacts are ad-hoc signed and not
notarised. An un-notarised paid app trips Gatekeeper hard, and first-run *is* the
product. Both this session and the App Work session independently reached that
conclusion. Keep the Gumroad Content tabs empty until the cert lands.

### What the user still has to do themselves

Account creation, payment and password entry are out of scope for an agent.
Steps 1–4 below are theirs; step 5 onward is ours.

1. **Enrol** — developer.apple.com/programs/enroll, or the Apple Developer app.
   $99/yr. Legal name must match the photo ID exactly.
2. **CSR** — Keychain Access → Certificate Assistant → *Request a Certificate
   From a Certificate Authority*. Common Name `JamWare Audio`, **Saved to disk**,
   2048-bit RSA. Must be done **on the MacBook Pro** — it creates the private key
   there, and without that key the certificate is worthless.
3. **Certificate** — developer.apple.com/account → Certificates → **+** →
   **Developer ID Application** (not Mac Development, not Mac App Distribution,
   not Developer ID Installer). Upload the CSR, download the `.cer`,
   double-click to install.
4. **Notarisation credential** — an app-specific password from appleid.apple.com,
   then, **in their own terminal so the password is never captured in a session
   transcript**:
   `xcrun notarytool store-credentials "jamware" --apple-id <id> --team-id <TEAM_ID>`

`notarytool` is already present via Command Line Tools at
`/Library/Developer/CommandLineTools`. Full Xcode is **not** installed and is not
needed.

---

## 2. Launch sequence, once the cert exists

1. Confirm `security find-identity -v -p codesigning` shows a
   **Developer ID Application** line.
2. App Work session runs `package:signed` per app (drops the ad-hoc flags, picks
   the cert from the keychain or `CSC_LINK`). MutationStation already has
   hardened runtime + entitlements wired for notarisation.
3. Notarise and staple each DMG; verify Gatekeeper accepts them from a clean
   state.
4. Attach one DMG per product to the four Gumroad **Content** tabs — they are
   currently **empty**, which is why nothing is purchasable.
5. Resolve the Companion Suite (see §4).
6. Publish the four products on Gumroad.
7. Make the site public:
   ```sh
   gh repo edit jamwareaudio/jamwareaudio --visibility public
   gh api -X POST repos/jamwareaudio/jamwareaudio/pages \
     -f 'source[branch]=main' -f 'source[path]=/'
   ```
   Live at `https://jamwareaudio.github.io/jamwareaudio/` a minute or two
   later. After that, updating the site is just `git push`.

### ⚠ Which DMG to upload

Artifacts live in `release/` per app — **except MutationStation**, which uses
`standalone/release/`, and that directory holds **four** DMGs, three of them
abandoned product names:

| App | Path | Correct file |
|---|---|---|
| Spectrl | `Spectrl/release/` | `Spectrl-1.0.0-arm64.dmg` |
| MidiMirror | `MidiMirror/visualizer/release/` | `MidiMirror-1.0.0-arm64.dmg` |
| Chordinator | `Chordinator/release/` | `Chordinator-1.0.0-arm64.dmg` |
| MutationStation | `MutationStation/standalone/release/` | `MutationStation-1.0.0-arm64.dmg` ⚠ |
| TouchXY | `TouchXY/release/` | `TouchXY-1.0.0-arm64.dmg` |

The MutationStation strays are `Acidosis-*` (Aug 2), `GeneLab-*` (Aug 4) and
`Mutation Station-*` (Aug 2, note the space). Only the Aug 10 build is current.
Check mtimes before uploading — the same rename-litter pattern filled
`TouchXY/dist-app` with four bundles before it was deleted.

---

## 3. What is done

**Website** — `site/`, a static site, no build step.

- Its own git repo, pushed to <https://github.com/jamwareaudio/jamwareaudio>,
  **private**, Pages off, working tree clean at `5eaf777`.
- ⚠ `gumroad/` is **gitignored on purpose**. `GUMROAD-KIT.md` holds pricing
  strategy, open decisions and internal notes about the support address. Pages
  serves every file in a repo. Keep it out.
- All six pages render; every internal link and asset resolves (verified by
  fetching each `src`/`href` across all six pages — zero broken).
- Arranger correctly shows "Not released yet" and a screenshot placeholder.

**Screenshots** — all re-shot at the full 1728pt window, 2× retina, one shared
aspect ratio. Site, all four Gumroad descriptions, and the manuals agree.

- ⚠ **Never capture a resized window.** The apps reflow below ~1600pt —
  MutationStation runs its title under the transport — so a narrow grab documents
  a layout that only exists when you shrink the app. This was the original
  complaint that started the work.
- Taken with `screencapture -o -x -l <windowID>` (exact window rect, no shadow).
  Enumerating window IDs needs `dangerouslyDisableSandbox: true`; under the
  default sandbox `CGWindowListCopyWindowInfo` silently returns an empty list.

**Gumroad** — storefront at `jamwareaudio.gumroad.com`.

- Donate page **live and published**: `https://jamwareaudio.gumroad.com/coffee`,
  "Buy me a coffee", €5/€10/€25.
- Donate URL verified **inside the installed bundles** of all four apps, not just
  in source.
- All four product descriptions carry current screenshots. Cover art verified
  already current (re-running `make-gumroad-art.sh` produced byte-identical
  files).
- Product slugs verified against the real dashboard: `mutationstation`,
  `chordinator`, `spectrl`, `midimirror` — all correct.
- The four app products remain **unpublished**, deliberately.

**Apps** — all five rebuilt and reinstalled (App Work session). Migration from
electron-packager to electron-builder is complete; `Spectrl/dist`,
`TouchXY/dist-app` and `MidiMirror/visualizer/dist` were deleted (1.85 GB).
Installed `app.asar` timestamps as of writing: Spectrl and TouchXY 12:52,
the other three 15:00 on 08-10.

---

## 4. Open decisions — the user's, not ours

1. **The Companion Suite bundle does not exist.** `index.html:221` points at
   `/l/companion-suite`, which 404s. The store holds the four apps, the coffee
   product and an unrelated sample pack. Either create the bundle or drop the
   button — **do not ship the page as it stands**. Asked twice; not yet answered.
2. **Support address** is still `toastonjam12345@gmail.com` in 11 places across
   `site/` and the Gumroad kit. A one-line `sed` fixes all of them once there is
   an address to use.
3. **The Dock-icon focus bug** (see §5) — fix before launch, or ship with it.
   Offered three times, not yet answered.

---

## 5. Known bugs and traps

**Dock-icon focus bug — user-facing, unfixed.** A running instance of these apps
cannot be raised. `open -a` and AppleScript `set frontmost` both return success
and do nothing, because the single-instance handler calls `win.focus()`, which on
macOS does not steal activation from another app. Symptom: click the Dock icon
of an already-running app while Ableton is frontmost and nothing happens. Worse
here than for most apps, because these are *designed* to sit open beside Ableton
— MidiMirror is a second-screen mirror, Spectrl an analyser you glance at.
"Bring it back" is a core interaction and it silently fails. Likely fix is
`win.show()` / `app.focus({ steal: true })` across five `main.js` files; needs an
unlocked desktop to verify. Found by the App Work session, not independently
verified here.

**Single-instance lock makes relaunch a silent no-op.** Every app calls
`requestSingleInstanceLock()` and quits on losing it. `npx electron .` against a
live instance exits 0, prints nothing, and leaves a working CDP endpoint on the
port you asked for — belonging to the *old* process, running whatever code was on
disk when it started. This produced a wrong conclusion once already (a renderer
fix reported as "not taking effect" when it was fine). Before any visual
verification: `pkill -f 'remote-debugging-port=<port>'`, confirm `pgrep` is
empty, launch, then confirm the PID is yours. Never treat "the port answers" as
proof. TouchXY is worst — it adds itself to Login Items, so an instance can hold
the lock with nobody having launched it.

**A locked screen is not a measurable state.** Renderers report
`visibilityState: "visible"` and run 60 rAF/s while compositing zero frames, so
a performance baseline taken then shows everything near zero and looks like good
news. The shared harness at `CompanionApps/perf/` now refuses rather than
returning plausible zeros. **The baseline is still owed.**

**`grep` false negatives — fixed, but know the class.** One raw control byte
made `MidiMirror/visualizer/main.js` opaque to `grep`, which returned nothing
with no error. It nearly caused a report that the donate wiring had been deleted,
and it swallowed two independent "no stale references" audits — both sweeps
certified a file neither had read. The bytes are now `\x00`/`\x01` escapes. If a
grep over source comes back suspiciously empty, check `file -b` for `data`.

---

## 6. Who owns what

Three Claude sessions worked in parallel; coordinate via `ListAgents` /
`SendMessage` rather than editing across boundaries.

- **This session** — website, Gumroad, Spectrl figures, launch sequence.
- **"App Work"** — packaging, electron-builder migration, performance work,
  Apple enrolment support. Owns `release/`, `main.js`, `perf/`.
- **"Manuals, hints etc"** — all five manuals and the shared
  `docs-tools/build_manual.py`.

⚠ `Chordinator/docs/MANUAL.md` and `MutationStation/docs/MANUAL.md` are
**generated** from the apps' in-app help via `docs-tools/gen-*-manual.mjs`. Do
not hand-edit them. `MutationStation/docs/manual-src/` is deleted; figures now
live in `MutationStation/docs/img/`.

⚠ `MutationStation/standalone/dist/` is **not** stale packager output despite the
name — it is esbuild output that electron-builder builds *from*, that a test
reads, and that the manual-screenshot harness points headless Chrome at. Do not
delete it in a "clean up dist dirs" sweep.

---

## 7. Session log

### 2026-08-12

**Gumroad listings — algorithm screenshots added.** Chordinator and
MutationStation listings on Gumroad (`app.gumroad.com/products/ztjqq/edit` and
`.../gligmk/edit`) each got a screenshot of their full algorithm surface
(`site/assets/shots/chordinator-algorithms.png`,
`.../mutationstation-algorithms.png`) plus an explanatory paragraph placed
right after it, before "What is in it": Chordinator's covers Chord Gen,
Rhythm, Suggest and Auto-Lock and how Suggest lights up palette buttons;
MutationStation's covers Pattern, Algorithm (Pitch Mutation), Scale/Root and
Acid Character. Both saved and confirmed via Gumroad's "Changes saved!" toast.
These screenshots are local files only — not committed anywhere, since
`site/gumroad/` notes and Gumroad-side content live outside this repo's git
tree by convention.

**Product ordering — checked, already correct on the site.**
`index.html:62-198` already lists MutationStation first, Chordinator second,
ahead of Spectrl and MidiMirror (Arranger last, unreleased). No edit was
needed here.

**Product ordering — Gumroad admin dashboard and public storefront: no fix
made, needs the user.** No UI-based way to reorder products was found in
either the admin product table (drag-and-drop attempted, order did not
change) or the public storefront (checked Profile → About/Design/Pages, no
reorder control). This is still open for two of the "all 3 places" the user
asked for. Reordering may require Gumroad support, an API call, or a
publish/unpublish workaround — the last of which needs explicit user
permission before being attempted, per the standing safety rule on
publish-state changes.

**TouchXY is not on the site at all.** Checked at the user's request (their
ordering instruction named TouchXY alongside Spectrl/MidiMirror). It does not
appear in `index.html` or anywhere under `site/apps/` — only in this
HANDOFF's release-path notes (§2). If it should be listed as a product, that
is new work, not a reorder.

**Not yet scoped:** the user's broader "highlight more individual concepts
with screenshots" goal — the two concrete asks (Chordinator, MutationStation
algorithm screenshots) are done, but which other concepts/apps get the same
treatment next needs the user's steer rather than an open-ended sweep.
