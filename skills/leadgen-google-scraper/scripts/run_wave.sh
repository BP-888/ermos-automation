#!/usr/bin/env bash
# Run one batch wave of leadgen-google-scraper with guard rails.
#
# Refuses to spend without a cap, checks credentials and Apify reachability,
# prints a dry run and a worst-case place/cost estimate, then asks for a typed
# "yes" (or takes --yes for unattended runs).
#
# Usage:
#   scripts/run_wave.sh --cap <USD> [--segment accounting] \
#     [--locations config/locations/accounting_wave1.txt] \
#     [--max-places 60] [--sop-version v0.2] [--yes]
#
# Environment: APIFY_TOKEN (never echoed), PIPELINE_RAW_DIR.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$HERE")"

SEGMENT="accounting"
LOCATIONS=""
MAX_PLACES=60
SOP_VERSION="v0.2"
CAP=""
ASSUME_YES=0
# Rate-card range for compass/crawler-google-places, USD per 1,000 places,
# with every paid add-on off. Confirm against the Apify console.
PRICE_LOW=1.50
PRICE_HIGH=4.00

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cap) CAP="$2"; shift 2 ;;
    --segment) SEGMENT="$2"; shift 2 ;;
    --locations) LOCATIONS="$2"; shift 2 ;;
    --max-places) MAX_PLACES="$2"; shift 2 ;;
    --sop-version) SOP_VERSION="$2"; shift 2 ;;
    --yes) ASSUME_YES=1; shift ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "ERROR: unknown option $1" >&2; exit 2 ;;
  esac
done

LOCATIONS="${LOCATIONS:-$SKILL_ROOT/config/locations/${SEGMENT}_wave1.txt}"
SEGMENT_FILE="$SKILL_ROOT/config/segments/${SEGMENT}.json"

[[ -n "$CAP" ]] || { echo "ERROR: --cap <USD> is required (Brad sets the wave cap)." >&2; exit 2; }
[[ -f "$LOCATIONS" ]] || { echo "ERROR: locations file not found: $LOCATIONS" >&2; exit 2; }
[[ -f "$SEGMENT_FILE" ]] || { echo "ERROR: segment file not found: $SEGMENT_FILE" >&2; exit 2; }
[[ -n "${APIFY_TOKEN:-}" ]] || { echo "ERROR: APIFY_TOKEN is not set." >&2; exit 2; }
[[ -n "${PIPELINE_RAW_DIR:-}" && -d "${PIPELINE_RAW_DIR}" ]] || {
  echo "ERROR: PIPELINE_RAW_DIR is not set or not a directory." >&2; exit 2; }

if ! curl -sS -m 15 -o /dev/null -H "Authorization: Bearer ${APIFY_TOKEN}" "https://api.apify.com/v2/acts/compass~crawler-google-places"; then
  echo "ERROR: api.apify.com is not reachable from here. Allow it in the network settings, or run this on a machine that can reach it." >&2
  exit 3
fi

N_LOC=$(grep -cvE '^\s*(#|$)' "$LOCATIONS")
N_TERMS=$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))['search_terms']))" "$SEGMENT_FILE")
MAX_TOTAL=$(( N_LOC * N_TERMS * MAX_PLACES ))
read -r EST_LOW EST_HIGH < <(python3 -c "m=$MAX_TOTAL;print(f'{m*$PRICE_LOW/1000:.2f} {m*$PRICE_HIGH/1000:.2f}')")

echo "== Dry run (first location only shown) =="
python3 "$HERE/google_scraper.py" --segment "$SEGMENT" --mode batch \
  --suburbs-file "$LOCATIONS" --max-places-per-search "$MAX_PLACES" \
  --run-cap-usd "$CAP" --sop-version "$SOP_VERSION" --dry-run | sed -n '1,22p'

cat <<EOF

== Wave summary ==
Segment:              $SEGMENT
Locations:            $N_LOC  ($LOCATIONS)
Search terms:         $N_TERMS
Max places / search:  $MAX_PLACES
Worst-case places:    $MAX_TOTAL (before Google's own overlap; real unique rows are far fewer)
Worst-case cost:      US\$$EST_LOW to US\$$EST_HIGH at US\$$PRICE_LOW to US\$$PRICE_HIGH per 1,000
Hard spend cap:       US\$$CAP (Apify stops spending here; remaining locations are skipped)
Output folder:        $PIPELINE_RAW_DIR
EOF

if [[ $ASSUME_YES -ne 1 ]]; then
  read -r -p "Type yes to start the wave: " ANSWER
  [[ "$ANSWER" == "yes" ]] || { echo "Not started."; exit 0; }
fi

python3 "$HERE/google_scraper.py" --segment "$SEGMENT" --mode batch \
  --suburbs-file "$LOCATIONS" --max-places-per-search "$MAX_PLACES" \
  --run-cap-usd "$CAP" --sop-version "$SOP_VERSION"
