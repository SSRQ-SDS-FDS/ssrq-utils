import re

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
