import re
import unicodedata

from ssrq_utils.lang.display import Lang


def create_punctuation_mark(mark: str, lang: Lang) -> str:
    """Create a punctuation mark in the given language.

    Args:
        mark (str): The punctuation mark.
        lang (Lang): The language.

    Returns:
        str: The punctuation mark.

    """
    match mark:
        case ":" | ";" | "!" | "?" if lang == Lang.FR:
            return f" {mark}"
        case _:
            return mark


def normalize_punctuation_marks(text: str, lang: Lang):
    """Normalize punctuation marks in a string.

    Args:
        text (str): The text.
        lang (Lang): The language.

    Returns:
        str: The text with normalized punctuation marks.

    """
    return re.sub(
        r"\s*(:|\?|;|!)", lambda match: create_punctuation_mark(match.group(1), lang), text
    )


def needs_french_elision(following: str) -> bool:
    """Detect whether a full name begins with a vowel for French elision.

    Ignore leading whitespace, case, and accents for detection only; the original
    name remains unchanged. Initials such as A. Dupont do not trigger elision.
    Names beginning with h return False because spelling alone cannot distinguish
    a mute h from an aspirated h. The caller must decide these cases explicitly.

    Args:
        following (str): The first name displayed after a French prefix.

    Returns:
        bool: True for a vowel-initial full name, including y; False for initials,
            empty text, and other beginnings.

    """
    # Decompose accented letters so É and E followed by an accent behave alike.
    normalized = unicodedata.normalize("NFD", following.lstrip().casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    if not normalized or re.match(r"^[a-z]\.(?:[\s-]|$)", normalized):
        return False
    return normalized[0] in "aeiouy"
