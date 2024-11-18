from typing import Self, cast

from pydantic import BaseModel, Field, model_validator

from ssrq_utils.i18n.error import I18nValidationError


class I18nMap(BaseModel):
    """A i18n map with translations for SSRQ display languages."""

    de: dict[str, str] = Field(..., description="The German i18n entry")
    en: dict[str, str] = Field(..., description="The English i18n entry")
    fr: dict[str, str] = Field(..., description="The French i18n entry")
    it: dict[str, str] = Field(..., description="The Italian i18n entry")

    @model_validator(mode="after")
    def check_entries(self) -> Self:
        """Check if the given translations are equals."""
        lang_keys = self.model_dump().keys()
        for lang in lang_keys:
            defined_translations = cast(dict[str, str], getattr(self, lang)).keys()
            if not all(
                len(cast(dict[str, str], getattr(self, other_lang).keys()))
                == len(defined_translations)
                for other_lang in lang_keys
                if other_lang != lang
            ):
                raise I18nValidationError(
                    f"The given translations for »{lang}« are not equal to the translations of the other languages."
                )
        return self
