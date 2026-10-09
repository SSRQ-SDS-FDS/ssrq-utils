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
        translations = self._filter_elided_keys(cast(dict[str, dict[str, str]], self.model_dump()))
        lang_keys = translations.keys()
        for lang in lang_keys:
            defined_translations = translations[lang].keys()
            if not all(
                len(translations[other_lang]) == len(defined_translations)
                for other_lang in lang_keys
                if other_lang != lang
            ):
                raise I18nValidationError(
                    f"The given translations for »{lang}« are not equal to the translations of the other languages."
                )
        return self

    def _filter_elided_keys(
        self, translations: dict[str, dict[str, str]]
    ) -> dict[str, dict[str, str]]:
        """Filter optional elided variants out of each language's translations.

        Create a filtered copy for the completeness check. The original
        translations, including their elided variants, remain available for lookup.

        Args:
            translations (dict[str, dict[str, str]]): Translation entries by language.

        Returns:
            dict[str, dict[str, str]]: The language dictionaries without keys
                ending in _elided.

        """
        return {
            lang: dict(filter(lambda entry: not entry[0].endswith("_elided"), entries.items()))
            for lang, entries in translations.items()
        }
