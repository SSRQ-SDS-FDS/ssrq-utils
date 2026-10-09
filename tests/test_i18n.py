import json
from pathlib import Path

import pytest

from ssrq_utils.i18n.model import I18nMap
from ssrq_utils.i18n.text import needs_french_elision, normalize_punctuation_marks
from ssrq_utils.i18n.translator import Translator
from ssrq_utils.lang.display import Lang


@pytest.fixture(scope="module")
def valid_translations():
    return {
        "de": {"foo": "bar"},
        "en": {"foo": "bar"},
        "fr": {"foo": "bar"},
        "it": {"foo": "bar"},
    }


@pytest.fixture
def translation_file(tmp_path, valid_translations):
    translation_file = tmp_path / "translations.json"
    translation_file.write_text(json.dumps(valid_translations))
    return translation_file


def test_model_validates(valid_translations):
    assert isinstance(I18nMap.model_validate(valid_translations), I18nMap)


def test_model_raises_error_on_different_number_of_translations():
    invalid_translations = {
        "de": {"foo": "bar"},
        "en": {"foo": "bar"},
        "fr": {"foo": "bar"},
        "it": {"foo": "bar", "baz": "qux"},
    }

    with pytest.raises(ValueError):  # noqa: PT011
        I18nMap.model_validate(invalid_translations)


@pytest.mark.parametrize("lang", ["de", "en", "fr", "it"])
def test_model_allows_language_specific_elided_variants(valid_translations, lang):
    translations = {language: entries.copy() for language, entries in valid_translations.items()}
    translations[lang]["foo_elided"] = "optional variant"
    translations[lang]["by_elided"] = "another optional variant"

    model = I18nMap.model_validate(translations)

    assert getattr(model, lang)["foo_elided"] == "optional variant"
    assert getattr(model, lang)["by_elided"] == "another optional variant"


def test_model_elided_variant_does_not_replace_missing_ordinary_translation(valid_translations):
    translations = {lang: entries.copy() for lang, entries in valid_translations.items()}
    translations["fr"] = {"foo_elided": "optional variant"}

    with pytest.raises(ValueError, match="are not equal"):
        I18nMap.model_validate(translations)


def test_model_only_excludes_keys_with_elided_suffix(valid_translations):
    translations = {lang: entries.copy() for lang, entries in valid_translations.items()}
    translations["fr"]["foo_elided_label"] = "ordinary translation"

    with pytest.raises(ValueError, match="are not equal"):
        I18nMap.model_validate(translations)


def test_translator_can_be_created(translation_file: Path):
    translator = Translator(translation_file)
    assert translator is not None
    assert isinstance(translator, Translator)


@pytest.mark.parametrize(
    ("lang", "key", "expected"),
    [
        (Lang.DE, "foo", "bar"),
        (Lang.EN, "foo", "bar"),
        (Lang.FR, "foo", "bar"),
        (Lang.IT, "foo", "bar"),
        (Lang.DE, "baz", "Unknown key: 'baz'"),
    ],
)
def test_translator_can_translate(translation_file: Path, lang: Lang, key: str, expected: str):
    translator = Translator(translation_file)
    assert translator.translate(lang, key) == expected


@pytest.mark.parametrize(
    ("lang", "text", "expected"),
    [
        (Lang.DE, "foo: bar", "foo: bar"),
        (Lang.EN, "foo: bar", "foo: bar"),
        (Lang.FR, "foo: bar", "foo : bar"),
    ],
)
def test_normalize_punctuation_mark(lang: Lang, text: str, expected: str):
    assert normalize_punctuation_marks(text, lang) == expected


@pytest.mark.parametrize(
    ("following", "expected"),
    [
        ("Anna Dupont", True),
        ("émilie Dupont", True),
        ("E\u0301milie Dupont", True),
        ("  Émile Dupont", True),
        ("Örs Dupont", True),
        ("Yves Dupont", True),
        ("Bernard Dupont", False),
        ("Henri Dupont", False),
        ("Hans Müller", False),
        ("A. Dupont", False),
        ("É. Dupont", False),
        ("A.-M. Dupont", False),
        ("A.", False),
        ("", False),
        ("   ", False),
    ],
)
def test_needs_french_elision(following, expected):
    assert needs_french_elision(following) is expected


@pytest.fixture
def prefix_translator(tmp_path):
    translations = {
        "de": {"collaboration": "unter Mitarbeit von", "by": "von"},
        "en": {"collaboration": "with contributions from", "by": "by"},
        "fr": {"collaboration": "avec la collaboration de", "by": "par"},
        "it": {"collaboration": "con la collaborazione di", "by": "a cura di"},
    }
    translations["fr"]["collaboration_elided"] = "avec la collaboration d\u2019"
    source = tmp_path / "prefixes.json"
    source.write_text(json.dumps(translations), encoding="utf-8")
    # Isolate these translations from the singleton used by other tests.
    translator = object.__new__(Translator)
    translator._load_translations(source)
    return translator


@pytest.mark.parametrize(
    ("lang", "key", "following", "elide", "expected"),
    [
        (Lang.FR, "collaboration", "Anna Dupont", None, "avec la collaboration d\u2019"),
        (Lang.FR, "collaboration", "Émilie Dupont", None, "avec la collaboration d\u2019"),
        (Lang.FR, "collaboration", "Bernard Dupont", None, "avec la collaboration de "),
        (Lang.FR, "collaboration", "A. Dupont", None, "avec la collaboration de "),
        (Lang.FR, "collaboration", "Henri Dupont", True, "avec la collaboration d\u2019"),
        (Lang.FR, "collaboration", "Hans Müller", False, "avec la collaboration de "),
        (Lang.FR, "collaboration", "Anna Dupont", False, "avec la collaboration de "),
        (Lang.FR, "collaboration", "", True, "avec la collaboration de "),
        (Lang.FR, "by", "Anna Dupont", None, "par "),
        (Lang.DE, "collaboration", "Anna Dupont", True, "unter Mitarbeit von "),
        (Lang.EN, "collaboration", "Anna Dupont", None, "with contributions from "),
        (Lang.IT, "collaboration", "Anna Dupont", None, "con la collaborazione di "),
        (Lang.FR, "missing", "Anna Dupont", None, "Unknown key: 'missing' "),
    ],
)
def test_translate_before(prefix_translator, lang, key, following, elide, expected):  # noqa: PLR0913
    assert prefix_translator.translate_before(lang, key, following, elide=elide) == expected


def test_translate_before_keeps_context_out_of_cached_translation(prefix_translator):
    assert prefix_translator.translate_before(Lang.FR, "collaboration", "Anna") == (
        "avec la collaboration d\u2019"
    )
    assert prefix_translator.translate_before(Lang.FR, "collaboration", "Bernard") == (
        "avec la collaboration de "
    )
    assert prefix_translator.translate(Lang.FR, "collaboration") == "avec la collaboration de"


@pytest.mark.parametrize("variant", ["avec la collaboration d'", "with "])
def test_translate_before_uses_variant_separator(prefix_translator, variant):
    key = "apostrophe" if variant.endswith("'") else "space"
    prefix_translator.translations.fr[key] = "normal"
    prefix_translator.translations.fr[f"{key}_elided"] = variant
    expected = variant.rstrip() if variant.endswith("'") else variant
    assert prefix_translator.translate_before(Lang.FR, key, "Anna") == expected
