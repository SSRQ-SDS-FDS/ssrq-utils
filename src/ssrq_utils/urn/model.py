from typing import Self

from pydantic import BaseModel, ConfigDict, Field

from ssrq_utils import idno as idno_utils


class URN(BaseModel):
    """A model to represent SSRQ-urns."""

    idno: idno_utils.model.IDNO | str = Field(description="The IDNO of the URN", frozen=True)
    fragment: str | None = Field(default=None, description="The fragment of the URN", frozen=True)
    model_config = ConfigDict(frozen=True)

    @classmethod
    def model_validate_string(
        cls,
        idno: str,
        cast_to_idno: bool = False,
        urn_prefix: str = "urn:ssrq:",
        fragment_sep: str = "#",
    ) -> Self:
        """Validate an urn string and return an instance of the model.

        Note: The Hashing of the model is only possible if the idno is not cast to an IDNO instance.

        Args:
        ----
            idno: The urn string to validate.
            cast_to_idno: Whether to cast the idno to an IDNO instance.
            urn_prefix: The prefix that the URN should start with.
            fragment_sep: The separator that separates the idno from the fragment.

        Returns:
        -------
            An instance of the model.

        """
        if not idno.startswith(urn_prefix):
            raise ValueError(f"Invalid URN: '{idno}' expected to start with '{urn_prefix}'.")

        idno = idno[len(urn_prefix) :]

        if fragment_sep in idno:
            idno, fragment = idno.split(fragment_sep)
        else:
            fragment = None

        return cls(
            idno=idno_utils.model.IDNO.model_validate_string(idno=idno) if cast_to_idno else idno,
            fragment=fragment,
        )
