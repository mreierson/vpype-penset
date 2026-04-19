"""Pipeline infrastructure for pen set metadata flow."""

import vpype as vp

from .penset import PenSet

PENSET_METADATA_KEY = "vpype_penset.active"


def resolve_penset(
    doc: vp.Document,
    penset_arg: PenSet | None = None,
) -> PenSet | None:
    """Get pen set from a CLI argument or from document metadata.

    Args:
        doc: The vpype document (checked for metadata).
        penset_arg: PenSet from CLI option (takes precedence).

    Returns:
        The resolved PenSet, or None if no pen set is active.
    """
    if penset_arg is not None:
        return penset_arg
    return doc.metadata.get(PENSET_METADATA_KEY)


def store_penset(doc: vp.Document, penset: PenSet) -> None:
    """Store a pen set in document metadata for downstream commands.

    Args:
        doc: The vpype document to store the pen set in.
        penset: The pen set to store.
    """
    doc.metadata[PENSET_METADATA_KEY] = penset
