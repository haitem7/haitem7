#!/usr/bin/env bash
# Turn a hero video into the frame sequence the scroll-scrub reads.
#
#   tools/hero_frames.sh assets/video/hero.mp4 [fps] [width] [quality]
#
# Seeking a compressed video on scroll is unreliable -- iOS Safari in
# particular refuses to seek smoothly -- so the scrub draws pre-decoded
# frames to a canvas instead. 48 frames at 1280px costs about 1.5 MB,
# less than the same clip as video.
set -euo pipefail
SRC="${1:?usage: hero_frames.sh <video> [fps] [width] [quality]}"
FPS="${2:-6}"; W="${3:-1280}"; Q="${4:-72}"
OUT="assets/hero-frames"
rm -rf "$OUT"; mkdir -p "$OUT"
ffmpeg -y -v error -i "$SRC" \
  -vf "fps=${FPS},scale=${W}:-2:flags=lanczos" \
  -c:v libwebp -quality "$Q" -compression_level 5 "$OUT/f-%03d.webp"
N=$(ls "$OUT" | wc -l | tr -d ' ')
echo "$N images -> $OUT  ($(du -sh "$OUT" | cut -f1))"
echo "Set hero.frames.count to $N in content/fr.json, en.json and ar.json."
