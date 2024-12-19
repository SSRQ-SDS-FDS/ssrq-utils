from collections.abc import Sequence
from typing import Any, TypeVar, overload

T = TypeVar("T", bound=object)

def uca_simple_sort(inputs: Sequence[str]) -> Sequence[str]:
    """Sort a list of strings using the UCA.

    Uses the unstable sorting mechanism of the Rust
    standard library, so the order of equal elements is
    not preserved.

    Args:
        inputs (Sequence[string]): The input strings.

    Returns:
        Sequence[string]: The sorted strings.

    """

@overload
def uca_complex_sort(inputs: Sequence[T], method_name: str) -> Sequence[T]:  # noqa: D418
    """Sort a list of objects using the UCA.

    Uses the unstable sorting mechanism of the Rust
    standard library, so the order of equal elements is
    not preserved.

    Args:
        inputs (Sequence[T]): The input objects.
        method_name (str): The method name, used to get a value for sorting.
        args (tuple[Any]): The method arguments.

    Returns:
        Sequence[T]: The sorted objects.

    """

@overload
def uca_complex_sort(inputs: Sequence[T], method_name: str, args: tuple[Any] | None) -> Sequence[T]:  # noqa: D418
    """Sort a list of objects using the UCA.

    Uses the unstable sorting mechanism of the Rust
    standard library, so the order of equal elements is
    not preserved.

    Args:
        inputs (Sequence[T]): The input objects.
        method_name (str): The method name, used to get a value for sorting.
        args (tuple[Any]): The method arguments.

    Returns:
        Sequence[T]: The sorted objects.

    """
