#!/usr/bin/env bash
# Generate pen set preview images (SVG + PNG) for documentation.
#
# Requires: vpype with vpype-penset installed, cairosvg
#
# Usage: ./docs/generate_images.sh

set -euo pipefail

OUTDIR="docs/images"
OUTER_RADIUS=5  # cm
PNG_WIDTH=1200  # px

mkdir -p "$OUTDIR"

# Get pen counts from Python
pen_counts=$(python3 -c "
from vpype_penset import PEN_SETS
for name, ps in PEN_SETS.items():
    print(f'{name} {len(ps)}')
")

while read -r name count; do
    echo "Generating $name ($count pens)..."

    # Build circle commands with evenly spaced radii
    circles=""
    for i in $(seq 1 "$count"); do
        radius=$(python3 -c "print(round($OUTER_RADIUS * ($count - $i + 1) / $count, 2))")
        circles="$circles circle -l $i 0 0 ${radius}cm"
    done

    svg="$OUTDIR/$name.svg"
    png="$OUTDIR/$name.png"

    # Generate SVG
    vpype penset "$name" $circles colorize write "$svg"

    # Convert to PNG
    cairosvg "$svg" -o "$png" -W "$PNG_WIDTH"

done <<< "$pen_counts"

echo "Done. Generated SVG + PNG in $OUTDIR/"
