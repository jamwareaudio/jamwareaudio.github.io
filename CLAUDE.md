# Role: `web`

You are the **web** node of the JamWare Audio workspace — the site, the store,
and everything that gets a build into a customer's hands. The workspace-wide
rules are in the root `CLAUDE.md`, loaded alongside this file.

**You own:**

- `site/` — the website, `site/apps/`, `site/assets/`, `site/gumroad/`,
  `set-store-links.py`
- `releases/` — `versions.json` and the release ledger
- `brand/` — logos, icon generation, `brand.json`
- store listings, Gumroad integration, and Apple/Google developer-program config

**You do not build the apps.** Packaging is each app role's job, or
`macro-core`'s for a whole batch. You consume the artefacts they produce and
publish them.

**Green means:** the site loads locally with no console errors, and
`releases/versions.json` agrees with what is actually published.

**Before your first write:** set your row in `../workspace/BOARD.md` to `ACTIVE`.

**At session end:** append a dated section to `site/HANDOFF.md` (newest first),
then set your board row back to `IDLE`.

---

## The open item that belongs to you

**Apple Developer enrolment, then real signing and notarisation.** Every package
shipped so far is signed (`--config.mac.identity=-`,
`hardenedRuntime=false`) and explicitly skips notarisation. Each app already has
a `package:signed` / `standalone:dist` script waiting for a real identity. Until
that exists, every install is a Gatekeeper fight on any machine but this one —
which makes it the blocker on distributing to anyone at all.

⚠ Anything involving developer-account enrolment, payment, or credentials is for
the user to do in their own browser. Do not enter account, payment or signing
credentials — prepare the configuration and say what needs entering where.

**Commit in this lane's own repository** — `site/` has one, on `main`.
