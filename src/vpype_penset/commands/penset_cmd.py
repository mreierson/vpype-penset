"""penset command — sets the active pen set from a name, hex colors, or TOML file."""

import click
import vpype as vp
import vpype_cli

from vpype_penset.penset import PenSet, PenSetParamType
from vpype_penset.pipeline import store_penset


@click.command()
@click.argument("penset_source", type=PenSetParamType())
@vpype_cli.global_processor
def penset(doc: vp.Document, penset_source: PenSet) -> vp.Document:
    """Set the active pen set for downstream commands.

    PENSET_SOURCE can be a predefined name (warm, cool, earth, rainbow,
    grayscale, viridis, stabilo88, staedtler, pilot_g2), comma-separated hex
    colors ('#ff0000,#00ff00,#0000ff'), or a TOML file path.

    After setting the pen set, use -l on geometry commands to target
    specific pens. Colorize assigns pen 1 to layer 1, pen 2 to layer 2, etc.

    \b
    Examples:
        vpype penset warm circle -l 1 0 0 5cm circle -l 3 0 0 3cm colorize write out.svg
        vpype penset "#f00,#0f0,#00f" circle -l 1 0 0 3cm circle -l 2 0 0 2cm circle -l 3 0 0 1cm colorize write out.svg
        vpype penset my-pens.toml circle -l 1 0 0 3cm circle -l 2 0 0 2cm colorize write out.svg
    """
    store_penset(doc, penset_source)
    return doc


penset.help_group = "Pen Set"
