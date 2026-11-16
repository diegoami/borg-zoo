#!/usr/bin/env bash
# Append compact comparison artifacts. Never execute a downloaded artifact.
# Arguments: Git remote, comparison directory, experiment, run-attempt, workspace.
set -euo pipefail
REMOTE="$1"
COMPARISON="$2"
EXPERIMENT="$3"
RUN_ID="$4"
WORKSPACE="$5"
[[ "$EXPERIMENT" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$ ]]
[[ "$RUN_ID" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$ ]]
[ ! -e "$WORKSPACE" ]
for FILE in comparison.json index.html; do
    [ -f "$COMPARISON/$FILE" ] && [ ! -L "$COMPARISON/$FILE" ]
done
# A fresh metadata-only checkout avoids mutable execution/build directories.
git clone --quiet --single-branch --branch results "$REMOTE" "$WORKSPACE"
git -C "$WORKSPACE" config user.name github-actions
git -C "$WORKSPACE" config user.email github-actions@users.noreply.github.com
DEST="scenario-results/$EXPERIMENT/$RUN_ID"
[ ! -e "$WORKSPACE/$DEST" ]
mkdir -p "$WORKSPACE/$DEST"
cp "$COMPARISON/comparison.json" "$COMPARISON/index.html" "$WORKSPACE/$DEST/"
git -C "$WORKSPACE" add "$DEST"
git -C "$WORKSPACE" commit --quiet -m "Append synthetic comparison $EXPERIMENT/$RUN_ID"
for ATTEMPT in 1 2 3; do
    if git -C "$WORKSPACE" push origin HEAD:results; then exit 0; fi
    git -C "$WORKSPACE" fetch origin results
    git -C "$WORKSPACE" rebase origin/results
    [ "$ATTEMPT" -lt 3 ] || exit 1
done
