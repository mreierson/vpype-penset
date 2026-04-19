"""pensets command — list all available built-in pen sets."""

import click
import vpype as vp
import vpype_cli

from vpype_penset.penset import PEN_SETS


@click.command()
@vpype_cli.global_processor
def pensets(doc: vp.Document) -> vp.Document:
    """List all available built-in pen sets.

    \b
    Examples:
        vpype pensets
    """
    click.echo(f"{'Name':12}  {'Pens':>4}  Colors")
    click.echo("-" * 50)

    for name, ps in PEN_SETS.items():
        colors = " ".join(
            f"#{p.color.red:02x}{p.color.green:02x}{p.color.blue:02x}" for p in ps.pens
        )
        click.echo(f"{name:12}  {len(ps):>4}  {colors}")

    return doc


pensets.help_group = "Pen Set"
