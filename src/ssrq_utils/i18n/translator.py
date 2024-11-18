import threading
from pathlib import Path

import cachebox

from ssrq_utils.i18n.model import I18nMap
from ssrq_utils.lang.display import Lang


class Translator:
    """A utility class to translate various
    values, which are stored in a JSON file. May be
    used to translate strings in the UI of the frontend.
    Implemented as a singleton to avoid multiple
    instances of the same translations.

    Args:
        translation_source (Path): The path to the JSON file containing the translations.

    Returns:
        Translator: The singleton instance of the Translator class.

    """  # noqa: D205

    _instance = None
    _lock = threading.Lock()
    translations: I18nMap

    def __new__(cls, translation_source: Path) -> "Translator":  # noqa: D102
        if cls._instance is None:
            with cls._lock:
                cls._instance = super().__new__(cls)
                cls._instance._load_translations(translation_source)
        return cls._instance

    def _load_translations(self, translation_source: Path) -> None:
        """Load the translations from the given JSON file.

        Args:
            translation_source (Path): The path to the JSON file containing the translations.

        Returns:
            None

        Raises:
            ValueError: If the translations are not valid.
            See the I18nMap class for more information.

        """
        with open(translation_source) as f:
            self.translations = I18nMap.model_validate_json(f.read())

    @cachebox.cachedmethod(cachebox.LRUCache(maxsize=128))
    def translate(self, lang: Lang, key: str) -> str:
        """Tranlates the given key to the given language.

        Will always return a string, even if the key is not found.

        Args:
            lang (Lang): The language to translate to.
            key (str): The key to translate.

        Returns:
            str: The translated value.

        """
        match lang:
            case Lang.DE | Lang.EN | Lang.FR | Lang.IT:
                return self._get_translation_value(getattr(self.translations, lang.value), key)
            case _:
                return f"Unknown language: '{lang}'"

    def _get_translation_value(self, data: dict[str, str], key: str) -> str:
        return data.get(key, f"Unknown key: '{key}'")
