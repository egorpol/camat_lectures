#!/usr/bin/env bash
# Copy the seminar notebooks from GitHub into camat_lectures/, without git.
#
# In a terminal on Jupyter4NFDI (or any JupyterLab: File > New > Terminal):
#
#   curl -fsSLO https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.sh
#   bash get_notebooks.sh
#
# (No curl? Use: wget -q https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.sh)
#
# The notebooks land in camat_lectures/<session>/ below the current folder.
# Run it again after each session to get the new ones. Notebooks you already
# have are never overwritten, so your changes are safe; to get a fresh copy
# of one, rename or delete yours and run the script again.
#
# It does the same as get_notebooks.py.

set -euo pipefail

REPO="https://github.com/egorpol/camat_lectures"
ARCHIVE="https://codeload.github.com/egorpol/camat_lectures/tar.gz/refs/heads/main"
DEST="camat_lectures"

fail() {
    printf '%s\n' "$@" >&2
    exit 1
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "Downloading the notebooks from $REPO ..."
if command -v curl >/dev/null 2>&1; then
    fetch=(curl -fsSL --max-time 120 -A camat-lectures-get-notebooks -o "$tmp/main.tar.gz" "$ARCHIVE")
elif command -v wget >/dev/null 2>&1; then
    fetch=(wget -q -T 60 -U camat-lectures-get-notebooks -O "$tmp/main.tar.gz" "$ARCHIVE")
else
    fail "Neither curl nor wget is installed here. Run python get_notebooks.py instead."
fi
"${fetch[@]}" || fail "Could not download the notebooks from $REPO." \
    "Check the network, or download them from the session page and upload them."
tar -xzf "$tmp/main.tar.gz" -C "$tmp" || fail "The download is not a valid archive. Please tell the instructor."

# The archive unpacks to camat_lectures-main/sessions/<session>/notebooks/<name>.ipynb.
new=()
kept=()
for src in "$tmp"/*/sessions/*/notebooks/*.ipynb; do
    [ -f "$src" ] || continue
    session=$(basename "$(dirname "$(dirname "$src")")")
    target="$DEST/$session/$(basename "$src")"
    if [ -e "$target" ]; then
        kept+=("$target")
    else
        mkdir -p "$DEST/$session"
        cp -- "$src" "$target"
        new+=("$target")
    fi
done

if [ "${#new[@]}" -gt 0 ]; then
    echo "New:"
    printf '  %s\n' "${new[@]}"
fi
if [ "${#kept[@]}" -gt 0 ]; then
    echo "Already there, kept as they are:"
    printf '  %s\n' "${kept[@]}"
fi
if [ "${#new[@]}" -eq 0 ] && [ "${#kept[@]}" -eq 0 ]; then
    fail "The download has no notebooks in it. Please tell the instructor."
fi
echo "Open them from the file browser: $(cd "$DEST" && pwd)"
