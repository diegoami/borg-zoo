#!/usr/bin/env bash
# Play one of the zoo deaths yourself.
#   ./play.sh                              list the deaths and their saves
#   ./play.sh priest-809881907             play the latest save before that death
#   ./play.sh priest-809881907 1721        play the stored save at (or just before) game turn 1721
#   ./play.sh priest-809881907 --to 1500   let the Borg replay the game from birth to game turn 1500
#                                          (the same game as the zoo run), then play from there
# Each session runs in its own copy, so the files here are never changed.
set -euo pipefail
K="$(cd "$(dirname "$0")" && pwd)"
if [ $# -eq 0 ]; then
  for d in "$K"/*/saves; do n=$(basename "$(dirname "$d")"); . "$K/$n/start.env"; echo "$n (dies at game turn $DEATH_TURN): $(ls "$d" | sed 's/\.save$//' | tr '\n' ' ')"; done
  exit 0
fi
D="$K/$1"; [ -d "$D/saves" ] || { echo "no such death: $1 (run ./play.sh to list them)" >&2; exit 2; }
. "$D/start.env"
W=$(mktemp -d "${TMPDIR:-/tmp}/borg-play-$1-XXXX")
mkdir -p "$W"/{user,save,archive,panic,scores}
cp "$D"/user/* "$W/user/"
cd "$K/bin/game"
if [ "${2:-}" = "--to" ]; then
  TURN="${3:?give a game turn: ./play.sh $1 --to TURN}"
  [ "$TURN" -lt "$DEATH_TURN" ] || { echo "the Borg dies at game turn $DEATH_TURN: choose an earlier turn" >&2; exit 2; }
  echo "The Borg replays $1 from birth to game turn $TURN ..."
  env -u BORG_PROFILE -u BORG_CORE -u BORG_ERRAND -u BORG_PLAN TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    ./angband -mborgh -n -uPlayer -duser="$W/user" -dsave="$W/save" -darchive="$W/archive" -dpanic="$W/panic" -dscores="$W/scores" \
    -- -seed "$SEED" -race "$RACE" -class "$CLASS" -turns "$TURN" -keylog "$W/keys.log" -summary "$W/summary.json" \
    -menu-letters -exact-turns -save-on-stop "$W/save/Player" > "$W/replay.log" 2>&1
  N=$(wc -l < "$W/keys.log")
  if head -n "$N" "$D/replay/keys.log" | cmp -s - "$W/keys.log"; then
    echo "Same game as the zoo run up to game turn $TURN ($N keys). Opening the game window."
  else
    echo "WARNING: this replay differs from the zoo run's keys; it is not the same game." >&2
  fi
else
  if [ $# -ge 2 ]; then
    SAVE=$(ls "$D"/saves/*.save | awk -v t="$2" -F'turn-' '{split($2,a,"-"); if (a[1]+0 <= t+0) s=$0} END{print s}')
  else
    SAVE=$(ls "$D"/saves/*.save | tail -1)
  fi
  [ -n "$SAVE" ] || { echo "no stored save at or before turn $2; use --to $2 instead" >&2; exit 2; }
  cp "$SAVE" "$W/save/Player"
  echo "Playing $(basename "$SAVE") of $1."
fi
echo "Session files: $W"
exec ./angband -mx11 -duser="$W/user" -dsave="$W/save" -darchive="$W/archive" -dpanic="$W/panic" -dscores="$W/scores" -uPlayer
