#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="${1:-"$SCRIPT_DIR/lyd-ark-kde-installer.iso"}"
shopt -s nullglob
PARTS=("$SCRIPT_DIR"/lyd-ark-kde-installer.iso.part[0-9][0-9][0-9].part)

if (( ${#PARTS[@]} == 0 )); then
  echo "No ISO parts found beside $0" >&2
  exit 1
fi

EXPECTED=$(awk '$2 == "lyd-ark-kde-installer.iso" {print $1}' "$SCRIPT_DIR/SHA256SUMS")
if [[ ! "$EXPECTED" =~ ^[[:xdigit:]]{64}$ ]]; then
  echo "Could not read expected SHA-256 from SHA256SUMS" >&2
  exit 1
fi

echo "Joining ${#PARTS[@]} ISO parts..."
cat "${PARTS[@]}" > "$OUTPUT"

ACTUAL=$(sha256sum "$OUTPUT" | awk '{print $1}')
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Checksum mismatch; reconstructed ISO is not valid." >&2
  rm -f "$OUTPUT"
  exit 1
fi

echo "ISO successfully reconstructed and verified:"
echo "$OUTPUT"
echo "SHA-256: $ACTUAL"
