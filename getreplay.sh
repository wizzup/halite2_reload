#!/usr/bin/env nix-shell
#! nix-shell -p zstd python3 -i bash

# usage: getreplay.sh gameid_url player_id
# example: ./getreplay.sh https://halite.io/play?game_id=5626832 0

set -x

GAMEID=$(echo "$1" | cut -d = -f 2)
TARGET=replays/$GAMEID

[[ -d $TARGET ]] || mkdir -p "$TARGET"

cd "$TARGET" || exit 1

wget "https://api.halite.io/v1/api/user/1304/match/$GAMEID/replay" -O replay.hlt

zstdcat replay.hlt | python -m json.tool > replay.json

../../extract.py replay.json "$2" > rawinput.txt

../../MyBot +RTS -p < rawinput.txt | tee rawoutput.txt
