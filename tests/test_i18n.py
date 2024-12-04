import json
from pathlib import Path

import pytest

from ssrq_utils.i18n.model import I18nMap
from ssrq_utils.i18n.text import normalize_punctuation_marks
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
