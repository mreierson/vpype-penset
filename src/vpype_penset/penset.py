"""Pen set data model, predefined pen sets, and Click parameter type."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import click
import vpype as vp


@dataclass(frozen=True)
class Pen:
    """A physical pen with color and optional characteristics.

    Attributes:
        color: The pen's ink color.
        width: Tip width in mm (maps to vp_pen_width). None means unspecified.
        name: Human-readable label, e.g. "Blue".
    """

    color: vp.Color
    width: float | None = None
    name: str | None = None


@dataclass(frozen=True)
class PenSet:
    """A named collection of pens for multi-layer plotter output.

    The pen set can be constructed with either Pen objects or bare vp.Color
    objects (which are auto-wrapped in Pen for backwards compatibility).
    """

    name: str
    pens: tuple[Pen, ...]

    def __post_init__(self) -> None:
        # Auto-wrap bare vp.Color objects in Pen.
        # Because frozen=True, we must use object.__setattr__.
        wrapped = tuple(
            Pen(color=item) if isinstance(item, vp.Color) else item
            for item in self.pens
        )
        object.__setattr__(self, "pens", wrapped)

    @property
    def colors(self) -> tuple[vp.Color, ...]:
        """Convenience color access."""
        return tuple(pen.color for pen in self.pens)

    @classmethod
    def from_colors(cls, name: str, colors: tuple[vp.Color, ...]) -> PenSet:
        """Create a pen set from bare colors (no pen metadata)."""
        return cls(name, tuple(Pen(color=c) for c in colors))

    def sample_pens(self, n: int) -> list[Pen]:
        """Evenly sample n pens from the pen set.

        If n <= len(pens), returns the first n pens.
        If n > len(pens), cycles through the pen set.
        """
        if n <= 0:
            return []
        pens = self.pens
        if not pens:
            return [Pen(color=vp.Color(0, 0, 0))] * n
        return [pens[i % len(pens)] for i in range(n)]

    def sample_colors(self, n: int) -> list[vp.Color]:
        """Sample n colors from the pen set (convenience method)."""
        return [pen.color for pen in self.sample_pens(n)]

    def __len__(self) -> int:
        return len(self.pens)


def _c(r: int, g: int, b: int) -> vp.Color:
    return vp.Color(r, g, b)


def _pen(r: int, g: int, b: int, width: float | None = None, name: str | None = None) -> Pen:
    return Pen(color=_c(r, g, b), width=width, name=name)


PEN_SETS: dict[str, PenSet] = {
    # --- Artistic ---
    "warm": PenSet(
        "warm",
        (
            _pen(128, 0, 0),
            _pen(180, 30, 10),
            _pen(220, 80, 20),
            _pen(240, 140, 30),
            _pen(250, 190, 60),
            _pen(255, 220, 100),
        ),
    ),
    "cool": PenSet(
        "cool",
        (
            _pen(10, 20, 80),
            _pen(20, 60, 140),
            _pen(40, 100, 180),
            _pen(80, 160, 200),
            _pen(140, 200, 220),
            _pen(200, 230, 240),
        ),
    ),
    "earth": PenSet(
        "earth",
        (
            _pen(60, 40, 20),
            _pen(120, 80, 40),
            _pen(160, 120, 60),
            _pen(180, 160, 100),
            _pen(140, 160, 80),
            _pen(80, 120, 60),
        ),
    ),
    "rainbow": PenSet(
        "rainbow",
        (
            _pen(255, 0, 0),
            _pen(255, 127, 0),
            _pen(255, 255, 0),
            _pen(0, 200, 0),
            _pen(0, 100, 255),
            _pen(75, 0, 130),
            _pen(148, 0, 211),
        ),
    ),
    "grayscale": PenSet(
        "grayscale",
        (
            _pen(0, 0, 0),
            _pen(50, 50, 50),
            _pen(100, 100, 100),
            _pen(150, 150, 150),
            _pen(200, 200, 200),
        ),
    ),
    "viridis": PenSet(
        "viridis",
        (
            _pen(68, 1, 84),
            _pen(72, 36, 117),
            _pen(65, 68, 135),
            _pen(53, 95, 141),
            _pen(42, 120, 142),
            _pen(33, 145, 140),
            _pen(34, 168, 132),
            _pen(68, 191, 112),
            _pen(122, 209, 81),
            _pen(189, 223, 38),
            _pen(253, 231, 37),
        ),
    ),
    # --- Plotter Pen Sets ---
    "stabilo88": PenSet(
        "stabilo88",
        (
            _pen(0, 0, 0, width=0.4, name="black"),
            _pen(180, 30, 30, width=0.4, name="red"),
            _pen(220, 120, 20, width=0.4, name="orange"),
            _pen(0, 120, 60, width=0.4, name="green"),
            _pen(0, 80, 160, width=0.4, name="blue"),
            _pen(100, 40, 120, width=0.4, name="purple"),
            _pen(180, 50, 100, width=0.4, name="pink"),
            _pen(60, 140, 180, width=0.4, name="light blue"),
        ),
    ),
    "staedtler": PenSet(
        "staedtler",
        (
            _pen(0, 0, 0, width=0.3, name="black"),
            _pen(200, 30, 30, width=0.3, name="red"),
            _pen(0, 100, 180, width=0.3, name="blue"),
            _pen(0, 140, 60, width=0.3, name="green"),
            _pen(240, 180, 0, width=0.3, name="yellow"),
            _pen(140, 40, 120, width=0.3, name="purple"),
            _pen(240, 100, 20, width=0.3, name="orange"),
            _pen(100, 60, 40, width=0.3, name="brown"),
        ),
    ),
    "pilot_g2": PenSet(
        "pilot_g2",
        (
            _pen(0, 0, 0, width=0.5, name="black"),
            _pen(0, 0, 180, width=0.5, name="blue"),
            _pen(200, 0, 0, width=0.5, name="red"),
            _pen(0, 130, 0, width=0.5, name="green"),
            _pen(100, 0, 150, width=0.5, name="purple"),
            _pen(0, 160, 200, width=0.5, name="teal"),
            _pen(220, 100, 0, width=0.5, name="orange"),
            _pen(180, 0, 80, width=0.5, name="burgundy"),
        ),
    ),
}


def _parse_hex_color(hex_str: str) -> vp.Color:
    """Parse a hex color string like '#ff0000' or 'ff0000' into a Color."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex color: #{hex_str}")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return vp.Color(r, g, b)


def _parse_pen_spec(spec: str) -> Pen:
    """Parse a pen specification like '#ff0000' or '#ff0000:0.7' into a Pen.

    Format: <hex_color>[:<width_mm>]
    """
    parts = spec.strip().split(":")
    if len(parts) == 1:
        return Pen(color=_parse_hex_color(parts[0]))
    if len(parts) == 2:
        color = _parse_hex_color(parts[0])
        try:
            width = float(parts[1])
        except ValueError as e:
            raise ValueError(f"Invalid pen width: {parts[1]}") from e
        return Pen(color=color, width=width)
    raise ValueError(f"Invalid pen spec: {spec}")


def load_penset(path: str | Path) -> PenSet:
    """Load a pen set from a TOML file.

    Expected format::

        [penset]
        name = "my-pens"
        pens = [
            { color = "#000000", width = 0.7, name = "Black 0.7" },
            { color = "#ff0000", width = 0.5 },
            { color = "#00ff00" },
        ]

    An equivalent verbose form uses TOML array-of-tables, which is better
    when entries are long or need per-pen comments::

        [penset]
        name = "my-pens"

        [[penset.pens]]
        color = "#000000"
        width = 0.7
        name = "Black 0.7"
    """
    path = Path(path)
    with open(path, "rb") as f:
        data = tomllib.load(f)

    penset = data.get("penset", {})
    name = penset.get("name", path.stem)
    pen_defs = penset.get("pens", [])

    if not pen_defs:
        raise ValueError(f"No pens defined in {path}")

    pens: list[Pen] = []
    for pd in pen_defs:
        color_str = pd.get("color")
        if color_str is None:
            raise ValueError(f"Pen missing 'color' field in {path}")
        color = _parse_hex_color(color_str)
        width = pd.get("width")
        pen_name = pd.get("name")
        pens.append(Pen(color=color, width=width, name=pen_name))

    return PenSet(name, tuple(pens))


class PenSetParamType(click.ParamType):
    """Click parameter type that accepts a pen set name, comma-separated pen specs, or TOML file.

    Examples:
        "warm" -> PEN_SETS["warm"]
        "#ff0000,#00ff00,#0000ff" -> PenSet("custom", (...))
        "#ff0000:0.7,#00ff00:0.5" -> PenSet with pen widths
        "my-pens.toml" -> loaded from TOML file
    """

    name = "penset"

    def convert(
        self,
        value: str | PenSet,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> PenSet:
        if isinstance(value, PenSet):
            return value

        # Try named pen set first
        if value in PEN_SETS:
            return PEN_SETS[value]

        # Try TOML file
        path = Path(value)
        if path.suffix == ".toml" and path.is_file():
            try:
                return load_penset(path)
            except (ValueError, KeyError) as e:
                self.fail(str(e), param, ctx)

        # Try comma-separated pen specs (hex colors with optional width)
        if "#" in value or "," in value:
            try:
                parts = [p.strip() for p in value.split(",") if p.strip()]
                pens = tuple(_parse_pen_spec(p) for p in parts)
                if pens:
                    return PenSet("custom", pens)
            except ValueError:
                pass

        available = ", ".join(sorted(PEN_SETS.keys()))
        self.fail(
            f"Unknown pen set '{value}'. Available: {available}. "
            "Or use comma-separated hex colors: '#ff0000,#00ff00,#0000ff' "
            "(with optional width: '#ff0000:0.7,#00ff00:0.5'), "
            "or a TOML file path.",
            param,
            ctx,
        )
