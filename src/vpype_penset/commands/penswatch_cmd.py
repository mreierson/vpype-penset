"""penswatch command -- generate a visual swatch sheet for the active pen set."""

import click
import numpy as np
import vpype as vp
import vpype_cli

from vpype_penset.penset import PenSet, PenSetParamType
from vpype_penset.pipeline import resolve_penset, store_penset

# Swatch layout constants (in CSS pixels, 96 dpi).
_SWATCH_W = 150  # swatch rectangle width
_SWATCH_H = 40  # swatch rectangle height
_GAP = 15  # vertical gap between swatches
_MARGIN = 20  # left/top margin
_FILL_LINES = 8  # number of horizontal fill lines per swatch


def _swatch_rect(x: float, y: float, w: float, h: float) -> np.ndarray:
    """Return a closed rectangle as a complex-valued polyline."""
    return np.array(
        [
            complex(x, y),
            complex(x + w, y),
            complex(x + w, y + h),
            complex(x, y + h),
            complex(x, y),
        ]
    )


def _swatch_fill(x: float, y: float, w: float, h: float, n_lines: int) -> list[np.ndarray]:
    """Return horizontal fill lines inside a rectangle."""
    lines = []
    for i in range(n_lines):
        t = (i + 1) / (n_lines + 1)
        ly = y + t * h
        lines.append(np.array([complex(x, ly), complex(x + w, ly)]))
    return lines


@click.command()
@click.option(
    "--penset",
    "penset_arg",
    type=PenSetParamType(),
    default=None,
    help="Override the active pen set. Accepts a name, hex colors, or TOML file.",
)
@vpype_cli.global_processor
def penswatch(doc: vp.Document, penset_arg: PenSet | None) -> vp.Document:
    """Generate a visual swatch sheet for the active pen set.

    Creates a document with one layer per pen, each containing a colored
    swatch rectangle. Use with ``colorize`` and ``write`` to produce an
    SVG swatch sheet.

    \b
    Examples:
        vpype penset stabilo88 penswatch colorize write swatch.svg
        vpype penswatch --penset copic colorize write copic-swatch.svg
    """
    ps = resolve_penset(doc, penset_arg)
    if ps is None:
        raise click.UsageError(
            "No pen set active. Use 'penset <name>' before penswatch, "
            "or pass --penset <name>."
        )

    # Create a fresh document for the swatch sheet.
    swatch_doc = vp.Document()
    # Preserve penset metadata so colorize works downstream.
    swatch_doc.metadata.update(doc.metadata)
    store_penset(swatch_doc, ps)

    for i, _pen in enumerate(ps.pens):
        layer_id = i + 1
        lc = vp.LineCollection()

        x = _MARGIN
        y = _MARGIN + i * (_SWATCH_H + _GAP)

        # Outline rectangle
        lc.append(_swatch_rect(x, y, _SWATCH_W, _SWATCH_H))

        # Fill lines to make color visible
        for line in _swatch_fill(x, y, _SWATCH_W, _SWATCH_H, _FILL_LINES):
            lc.append(line)

        swatch_doc.add(lc, layer_id=layer_id)

    return swatch_doc


penswatch.help_group = "Pen Set"  # type: ignore[attr-defined]
