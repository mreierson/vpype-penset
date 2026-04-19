"""colorize command — applies the active pen set to document layers."""

import click
import vpype as vp
import vpype_cli

from vpype_penset.penset import PenSet, PenSetParamType
from vpype_penset.pipeline import resolve_penset


@click.command()
@click.option(
    "--penset",
    "penset_arg",
    type=PenSetParamType(),
    default=None,
    help="Override the active pen set. Accepts a name, hex colors, or TOML file.",
)
@click.option(
    "--reverse",
    is_flag=True,
    default=False,
    help="Reverse the pen set color order.",
)
@vpype_cli.global_processor
def colorize(
    doc: vp.Document,
    penset_arg: PenSet | None,
    reverse: bool,
) -> vp.Document:
    """Apply the active pen set to document layers.

    Assigns colors (and pen widths, when defined) from the pen set to each
    layer's properties.

    The pen set can be set upstream with the 'penset' command, or
    overridden with --penset.

    Layers are assigned pens in order: layer 1 gets pen 1, layer 2 gets
    pen 2, and so on. Use -l on geometry commands to target a specific pen.

    \b
    Examples:
        vpype penset warm circle -l 1 0 0 5cm circle -l 2 0 0 4cm circle -l 3 0 0 3cm colorize write out.svg
        vpype penset cool circle -l 3 0 0 5cm circle -l 1 0 0 3cm colorize write out.svg
        vpype penset stabilo88 circle -l 1 0 0 5cm circle -l 2 0 0 4cm circle -l 3 0 0 3cm colorize write out.svg
    """
    ps = resolve_penset(doc, penset_arg)
    if ps is None:
        raise click.UsageError(
            "No pen set active. Use 'penset <name>' before colorize, "
            "or pass --penset <name>."
        )

    layer_ids = sorted(doc.layers)
    if not layer_ids:
        return doc

    pens = ps.sample_pens(len(layer_ids))
    if reverse:
        pens = list(reversed(pens))

    for layer_id, pen in zip(layer_ids, pens, strict=False):
        doc[layer_id].set_property("vp_color", pen.color)
        if pen.width is not None:
            doc[layer_id].set_property("vp_pen_width", pen.width)

    return doc


colorize.help_group = "Pen Set"
