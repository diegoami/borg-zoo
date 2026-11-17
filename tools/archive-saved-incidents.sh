#!/usr/bin/env bash
# Append a validated compact saved comparison, preserving every earlier run.
set -euo pipefail
REMOTE="$1"
COMPARISON="$2"
EXPERIMENT="$3"
RUN_ID="$4"
WORKSPACE="$5"
[[ "$EXPERIMENT" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$ ]]
[[ "$RUN_ID" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$ ]]
[ ! -e "$WORKSPACE" ]
[ -f "$COMPARISON/comparison.json" ] && [ ! -L "$COMPARISON/comparison.json" ]
git clone --quiet --single-branch --branch results "$REMOTE" "$WORKSPACE"
git -C "$WORKSPACE" config user.name github-actions
git -C "$WORKSPACE" config user.email github-actions@users.noreply.github.com
DEST="saved-incident-results/$EXPERIMENT/$RUN_ID"
[ ! -e "$WORKSPACE/$DEST" ]
mkdir -p "$WORKSPACE/$DEST"
cp "$COMPARISON/comparison.json" "$WORKSPACE/$DEST/"
git -C "$WORKSPACE" add "$DEST"
git -C "$WORKSPACE" commit --quiet -m "Append saved comparison $EXPERIMENT/$RUN_ID"
for ATTEMPT in 1 2 3; do
    if git -C "$WORKSPACE" push origin HEAD:results; then exit 0; fi
    git -C "$WORKSPACE" fetch origin results
    git -C "$WORKSPACE" rebase origin/results
    [ "$ATTEMPT" -lt 3 ] || exit 1
done
