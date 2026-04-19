"""vpype-penset: Pen set infrastructure for vpype plotter plugins."""

__version__ = "0.1.0"

from .penset import PEN_SETS, Pen, PenSet, PenSetParamType, load_penset
from .pipeline import PENSET_METADATA_KEY, resolve_penset, store_penset

__all__ = [
    "PEN_SETS",
    "Pen",
    "PenSet",
    "PenSetParamType",
    "load_penset",
    "PENSET_METADATA_KEY",
    "resolve_penset",
    "store_penset",
]
