import threading
from pathlib import Path

import cachebox

from ssrq_utils.i18n.model import I18nMap
from ssrq_utils.i18n.text import needs_french_elision
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

    def translate_before(
        self,
        lang: Lang,
        key: str,
        following: str,
        *,
        elide: bool | None = None,
    ) -> str:
        """Translate a prefix and include the separator before the following name.

        Select the appropriate translation key, translate it, and add the
        separator. Join the result directly to the name without extra whitespace:
        ``de `` + ``Bernard`` or ``d'`` + ``Anna``.

        Args:
            lang (Lang): The display language.
            key (str): The ordinary prefix key in the translation source.
            following (str): The first name displayed after the prefix.
            elide (bool | None): Override French elision when pronunciation is
                known, e.g. True for a mute h or False for an aspirated h.
                None detects vowel-initial full names automatically.

        Returns:
            str: The translated prefix with its separator, without the name.

        """
        selected_key = self._select_prefix_key(lang, key, following, elide=elide)
        prefix = self.translate(lang, selected_key)
        return self._add_prefix_separator(prefix, elided=selected_key != key)

    def _select_prefix_key(
        self,
        lang: Lang,
        key: str,
        following: str,
        *,
        elide: bool | None,
    ) -> str:
        """Select the ordinary prefix key or its French elided variant.

        Only French uses the optional ``<key>_elided`` translation. Keep the
        ordinary key when the name is empty, elision is unnecessary, or the
        translation source has no elided variant. No translated text is rewritten.

        Args:
            lang (Lang): The display language.
            key (str): The ordinary prefix key.
            following (str): The first name displayed after the prefix.
            elide (bool | None): An explicit French elision decision, or None
                to detect it from the name.

        Returns:
            str: The key to pass to translate.

        """
        if lang != Lang.FR or not following.strip():
            return key

        should_elide = needs_french_elision(following) if elide is None else elide
        if not should_elide:
            return key

        variant_key = f"{key}_elided"
        return variant_key if variant_key in self.translations.fr else key

    @staticmethod
    def _add_prefix_separator(prefix: str, *, elided: bool) -> str:
        """Add the separator that joins a translated prefix to the following name.

        An elided variant ending in a straight or typographic apostrophe joins
        directly to the name. All other prefixes use one space. Remove trailing
        whitespace from the translation before applying this rule.

        Args:
            prefix (str): The translated prefix.
            elided (bool): Whether the selected key is an elided variant.

        Returns:
            str: The prefix with either no separator or one trailing space.

        """
        prefix = prefix.rstrip()
        if elided and prefix.endswith(("\u2019", "'")):
            return prefix
        return f"{prefix} "

    def _get_translation_value(self, data: dict[str, str], key: str) -> str:
        return data.get(key, f"Unknown key: '{key}'")
