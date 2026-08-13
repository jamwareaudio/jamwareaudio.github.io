#!/bin/bash
#
# publish.sh — push the website to the public repo that GitHub Pages serves.
#
# WHY THERE ARE TWO REPOSITORIES, WHICH LOOKS LIKE ONE TOO MANY
# -------------------------------------------------------------
# GitHub Pages on the free tier will only serve a *public* repository, and it
# serves every file in it. This directory is not only a website: it is a working
# lane, and it carries CLAUDE.md (the lane's rules), HANDOFF.md (session notes,
# open decisions, what broke last time) and README.md (the go-live checklist and
# the deployment details). Making `jamwareaudio` public to get a URL would put
# all of that on the open web, history included, to save copying six files.
#
# Splitting by branch does not help — visibility is a property of the repository,
# not the branch — so the split has to be by repository:
#
#   toastonjam-debug/jamwareaudio        PRIVATE   this directory, the real work
#   toastonjam-debug/jamwareaudio-site   PUBLIC    only what a visitor loads
#
# The public one is a build output, not a place to work. Nothing is ever edited
# there; this script overwrites it wholesale. If it drifts, delete the mirror
# checkout and run this again.
#
# THE LIST BELOW IS AN ALLOWLIST, AND THAT IS DELIBERATE
# ------------------------------------------------------
# The obvious way to write this is to copy everything and exclude the internal
# files. Do not change it to that. An exclude list fails open: the day someone
# adds NOTES.md or a .env to this directory, an exclude list publishes it and
# nobody finds out. An allowlist fails closed — a new file is simply absent from
# the site until someone names it here, which is a bug you notice immediately and
# not one a customer notices for you. `gumroad/` is already kept out of the
# private repo by .gitignore for the same reason; this is the second fence.
#
# Usage:  ./publish.sh            from inside site/
#
set -euo pipefail

REPO="toastonjam-debug/jamwareaudio-site"
MIRROR=".public-mirror"          # gitignored; a checkout of the public repo

# Everything a browser loads, and nothing else.
PUBLIC_PATHS=(
  index.html
  styles.css
  apps
  assets
)

cd "$(dirname "$0")"

if [ ! -d "$MIRROR/.git" ]; then
  echo "==> No mirror checkout; cloning $REPO"
  git clone "https://github.com/$REPO.git" "$MIRROR"
fi

echo "==> Refreshing mirror from remote"
git -C "$MIRROR" fetch --quiet origin
git -C "$MIRROR" reset --quiet --hard origin/main 2>/dev/null || true

# Clear the mirror's tracked content before copying, so a file deleted here is
# deleted there too. `git rm` rather than `rm -rf *` so .git and CNAME survive.
git -C "$MIRROR" rm -r --quiet --cached . >/dev/null 2>&1 || true
for p in "${PUBLIC_PATHS[@]}"; do
  rm -rf "${MIRROR:?}/$p"
done

echo "==> Copying the public subset"
for p in "${PUBLIC_PATHS[@]}"; do
  cp -R "$p" "$MIRROR/$p"
done

# A CNAME file, if one exists, belongs to the published site and lives only in
# the mirror — it is created by hand when a custom domain is set up (see
# README.md) and must survive a republish.
git -C "$MIRROR" add -A

if git -C "$MIRROR" diff --cached --quiet; then
  echo "==> Nothing changed; site is already up to date."
  exit 0
fi

git -C "$MIRROR" commit --quiet -m "Publish site from jamwareaudio@$(git rev-parse --short HEAD)"
git -C "$MIRROR" push --quiet origin HEAD:main
echo "==> Pushed. GitHub Pages redeploys in a minute or two."
echo "    https://toastonjam-debug.github.io/jamwareaudio-site/"
