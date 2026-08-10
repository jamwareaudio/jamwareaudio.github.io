#!/usr/bin/env python3
"""
Rewrite the Gumroad slugs across the whole site in one pass.

Every buy button on the site is https://jamwareaudio.gumroad.com/l/<slug>, and the
slugs shipped here were ASSUMED — never checked against the real dashboard.
Each product's slug appears twice (its card on index.html and its own page in
apps/), so hand-editing is exactly the job that leaves one behind.

Usage — pass only the ones that are wrong:

    ./set-store-links.py --spectrl spectrl-analyser
    ./set-store-links.py --mutationstation acid-mutation-sequencer \\
                         --suite the-companion-suite

Run with no arguments to print the current slugs and exit without touching
anything. Stdlib only, no build step, same as the rest of this folder.

A product is identified by its PAGE, not by its slug: --spectrl means "whatever
apps/spectrl.html currently points at". That is what makes the script safe to
run twice. Keying the flags to the slugs instead would work exactly once, and
then silently no-op once a slug had been changed.
"""
import argparse
import pathlib
import re
import sys

BASE = "https://jamwareaudio.gumroad.com/l"
HERE = pathlib.Path(__file__).resolve().parent
SLUG = re.compile(re.escape(BASE) + r"/([a-z0-9-]+)")

#: flag name -> the page that owns that product. The Suite has no page of its
#: own; it is resolved as the slug on index.html no product page claims.
OWNER = {
    "mutationstation": "apps/mutationstation.html",
    "chordinator": "apps/chordinator.html",
    "spectrl": "apps/spectrl.html",
    "midimirror": "apps/midimirror.html",
}


def pages():
    """Every published page. gumroad/ is tooling, not part of the site."""
    return sorted(
        p for p in HERE.rglob("*.html")
        if "gumroad" not in p.relative_to(HERE).parts
    )


def slug_of(flag):
    """The slug a product currently uses, read from the page that owns it."""
    if flag == "suite":
        owned = set()
        for other in OWNER:
            s = slug_of(other)
            if s:
                owned.add(s)
        found = [s for s in SLUG.findall((HERE / "index.html").read_text())
                 if s not in owned]
        return found[0] if found else None
    page = HERE / OWNER[flag]
    if not page.exists():
        return None
    m = SLUG.search(page.read_text())
    return m.group(1) if m else None


def show(header="Current slugs:"):
    print(header)
    counts = {}
    for p in pages():
        for s in SLUG.findall(p.read_text()):
            counts[s] = counts.get(s, 0) + 1
    if not counts:
        print("  (none found — has the store URL changed?)")
        return
    owners = {}
    for flag in list(OWNER) + ["suite"]:
        s = slug_of(flag)
        if s:
            owners.setdefault(s, flag)
    for s in sorted(counts):
        print("  %-24s %d occurrence(s)   [--%s]"
              % (s, counts[s], owners.get(s, "?")))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in list(OWNER) + ["suite"]:
        ap.add_argument("--" + flag, metavar="SLUG",
                        help="real Gumroad slug for %s" % flag)
    args = ap.parse_args()

    wanted = {f: getattr(args, f) for f in list(OWNER) + ["suite"]
              if getattr(args, f)}
    if not wanted:
        show()
        print("\nNothing changed. Pass e.g. --spectrl <real-slug> to rewrite one.")
        return 0

    for flag, new in sorted(wanted.items()):
        old = slug_of(flag)
        if old is None:
            print("  ERROR: could not find a store link for --%s" % flag,
                  file=sys.stderr)
            continue
        if old == new:
            print("  %s already %s" % (flag, new))
            continue
        # The trailing quote anchors the match, so a slug that is a prefix of
        # another ("spectrl" inside "spectrl-pro") cannot be corrupted.
        needle, repl = '%s/%s"' % (BASE, old), '%s/%s"' % (BASE, new)
        touched = 0
        for p in pages():
            s = p.read_text()
            if needle in s:
                p.write_text(s.replace(needle, repl))
                touched += 1
        print("  %-16s %s -> %s   (%d file(s))" % (flag, old, new, touched))

    print()
    show("Now:")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
