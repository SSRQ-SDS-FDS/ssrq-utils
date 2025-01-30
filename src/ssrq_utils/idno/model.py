import re
from functools import cached_property
from typing import Self, TypeVar

from pydantic import BaseModel, Field, computed_field, model_validator

SCHEMA = (
    r"^"
    r"(?P<prefix>SSRQ|SDS|FDS)-"
    r"(?P<kanton>[A-Z]{2})-"
    r"(?P<volume>[A-Za-z0-9_]+)-"
    r"(?:"
    r"(?:(?P<caseOrOpening>(?:[A-Za-z0-9]+\.)*)(?P<doc>[0-9]+)-(?P<num>1))|"
    r"(?P<special>lit|intro|bailiffs)"
    r")$"
)
SCHEMA_RE = re.compile(SCHEMA)

T = TypeVar("T", int, str)


class IDNO(BaseModel):
    """A model to represent an SSRQ identifier."""

    prefix: str = Field(description="The prefix of the IDNO e.g. SSRQ, SDS, FDS", frozen=True)
    kanton: str = Field(description="The two letter canton code e.g. ZH, BE, LU", frozen=True)
    volume: str = Field(description="The volume the article is part of", frozen=True)
    case: int | None = Field(
        default=None, description="The number of the case, the 'Mantelstück'", frozen=True
    )
    opening: str | None = Field(default=None, description="Identifier for an opening", frozen=True)
    doc: int | None = Field(default=None, description="Identifier for a document", frozen=True)
    num: int | None = Field(
        default=None, gt=0, lt=2, description="The tradition number of the document", frozen=True
    )
    special: str | None = Field(
        default=None, description="Marker for a special document like an introduction", frozen=True
    )

    @computed_field  # type: ignore[misc]
    @cached_property
    def sort_key(self) -> float:
        """Get a key to sort the ID.

        Returns
        -------
            A float key to sort the IDNO.

        """
        if self.case and self.doc and self.doc > 0:
            return float(f"{self.case}.{self.doc}")

        return float(next(filter(None, (self.case, self.doc, 99999))))

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> Self:
        """Validate that parts of the idno are exclusive (should be ensured by the RegEx already)."""
        if self.special is not None and any(
            getattr(self, x) is not None for x in ["case", "opening", "doc", "num"]
        ):
            raise ValueError("Special documents cannot have a case, opening, doc or num")
        if self.case is not None and self.opening is not None:
            raise ValueError("Case and opening cannot be set at the same time")
        return self

    @classmethod
    def model_validate_string(cls, idno: str, schema: re.Pattern = SCHEMA_RE) -> Self:
        """Validate an IDNO string against the schema and return an instance of the model."""

        def check_and_cast(value: str, caster: type[T]) -> T | None:
            if value is None:
                return None
            value = value.removesuffix(".")
            if caster is int and value.isdigit():
                return caster(value)
            if caster is str and value.strip():
                return caster(value)
            return None

        if (m := schema.match(idno)) is None:
            raise ValueError(f"IDNO {idno} does not match the schema {schema.pattern}")

        case = check_and_cast(m.group("caseOrOpening"), int)
        return cls(
            prefix=m.group("prefix"),
            kanton=m.group("kanton"),
            volume=m.group("volume"),
            case=case,
            opening=None if case is not None else check_and_cast(m.group("caseOrOpening"), str),
            doc=check_and_cast(m.group("doc"), caster=int),
            num=check_and_cast(m.group("num"), caster=int),
            special=check_and_cast(m.group("special"), caster=str),
        )

    def is_main(self) -> bool:
        """Check if an IDNO represents a 'main document'.

        Returns
        -------
            True if the IDNO represents a 'main document'.

        """
        return not (self.case is not None and self.doc is not None and self.doc > 0)

    def __repr__(self) -> str:
        """Produce the original string of the IDNO."""
        start = f"{self.prefix}-{self.kanton}-{self.volume}"
        if self.special is not None:
            return f"{start}-{self.special}"
        if self.opening is not None:
            return f"{start}-{self.opening}.{self.doc}-{self.num}"
        if self.case is not None:
            return f"{start}-{self.case}.{self.doc}-{self.num}"
        return f"{start}-{self.doc}-{self.num}"
