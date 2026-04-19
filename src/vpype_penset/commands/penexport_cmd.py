"""penexport command -- export the active pen set to a TOML file."""

import click
import vpype as vp
import vpype_cli

from vpype_penset.penset import PenSet, PenSetParamType, export_penset
from vpype_penset.pipeline import resolve_penset


@click.command()
@click.argument("output", type=click.Path(dir_okay=False))
@click.option(
    "--penset",
    "penset_arg",
    type=PenSetParamType(),
    default=None,
    help="Override the active pen set. Accepts a name, hex colors, or TOML file.",
)
@vpype_cli.global_processor
def penexport(doc: vp.Document, output: str, penset_arg: PenSet | None) -> vp.Document:
    """Export the active pen set to a TOML file for sharing.

    Writes the pen set (colors, widths, names) to a TOML file that can be
    loaded with ``penset <file.toml>`` or shared with other users.

    \b
    Examples:
        vpype penset stabilo88 penexport my-pens.toml
        vpype penexport --penset warm warm-palette.toml
    """
    ps = resolve_penset(doc, penset_arg)
    if ps is None:
        raise click.UsageError(
            "No pen set active. Use 'penset <name>' before penexport, or pass --penset <name>."
        )

    export_penset(ps, output)
    click.echo(f"Exported pen set '{ps.name}' ({len(ps)} pens) to {output}")
    return doc


penexport.help_group = "Pen Set"  # type: ignore[attr-defined]
