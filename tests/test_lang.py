import pytest

from ssrq_utils.lang.display import Lang as DisplayLang


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("deu", DisplayLang.DE),
        ("eng", DisplayLang.EN),
        ("ita", DisplayLang.IT),
        ("fra", DisplayLang.FR),
        ("roh", DisplayLang.DE),
    ],
)
def test_display_lang_from_string(lang, expected):
    assert DisplayLang.from_string(lang) == expected
