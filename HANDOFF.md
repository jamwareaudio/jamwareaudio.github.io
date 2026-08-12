# HANDOFF — website, Gumroad storefront, launch sequence

Written 2026-08-10. Covers the website, the Gumroad store and the launch
sequence. It does **not** cover app source, manuals or the performance work —
those belong to other sessions (see *Who owns what*).

Everything buildable is done. The launch is gated on one thing: an Apple
Developer ID certificate that does not exist yet.

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
   gh repo edit toastonjam-debug/jamwareaudio --visibility public
   gh api -X POST repos/toastonjam-debug/jamwareaudio/pages \
     -f 'source[branch]=main' -f 'source[path]=/'
   ```
   Live at `https://toastonjam-debug.github.io/jamwareaudio/` a minute or two
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

- Its own git repo, pushed to <https://github.com/toastonjam-debug/jamwareaudio>,
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
