"""peninfo command — diagnostic display of the active pen set."""

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
@vpype_cli.global_processor
def peninfo(doc: vp.Document, penset_arg: PenSet | None) -> vp.Document:
    """Display the active pen set.

    Prints a table of pen index, color, width, and name for the active
    pen set. Useful for debugging pipelines.

    \b
    Examples:
        vpype penset stabilo88 peninfo
        vpype penset my_pens.toml peninfo
        vpype peninfo --penset pilot_g2
    """
    ps = resolve_penset(doc, penset_arg)
    if ps is None:
        raise click.UsageError(
            "No pen set active. Use 'penset <name>' before peninfo, or pass --penset <name>."
        )

    click.echo(f"Pen set: {ps.name} ({len(ps)} pens)")
    click.echo("-" * 50)
    click.echo(f"{'#':>3}  {'Color':8}  {'Width':>7}  Name")
    click.echo("-" * 50)

    for i, pen in enumerate(ps.pens, start=1):
        color_hex = f"#{pen.color.red:02x}{pen.color.green:02x}{pen.color.blue:02x}"
        width_str = f"{pen.width:.1f}mm" if pen.width is not None else "  -"
        name_str = pen.name or "-"
        click.echo(f"{i:>3}  {color_hex:8}  {width_str:>7}  {name_str}")

    return doc


peninfo.help_group = "Pen Set"  # type: ignore[attr-defined]
