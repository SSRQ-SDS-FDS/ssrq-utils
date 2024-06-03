from collections.abc import Sequence

from ssrq_utils.idno.model import IDNO


def get_main_idnos(idnos: Sequence[IDNO]) -> Sequence[IDNO] | None:
    """Filter a sequence of IDNOs.

    The result will only include IDNOs where the
    identification number represents a 'main document'.
    Main document are documents that are not part of
    case.

    Args:
    ----
        idnos: The sequence of IDNOs to filter.

    Returns:
    -------
        The filtered sequence of IDNOs.

    """
    return (
        result
        if (
            result := [
                idno
                for idno in idnos
                if not (idno.case is not None and idno.doc is not None and idno.doc > 0)
            ]
        )
        else None
    )
