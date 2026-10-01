import pytest
from pydantic import ValidationError

from ssrq_utils.retro.model import RegisterVolume


def test_register_volume_accepts_multiple_editors() -> None:
    volume = RegisterVolume(
        canton="ZG",
        volume="1.3",
        title="Sachregister und Glossar",
        editors=["Peter Stotz", "Weitere Bearbeiterin"],
    )

    assert volume.editors == ["Peter Stotz", "Weitere Bearbeiterin"]


@pytest.mark.parametrize("canton", ["ZG", "BS/BL", "OW-NW", "AR-AI"])
def test_register_volume_accepts_single_and_double_cantons(canton: str) -> None:
    volume = RegisterVolume(
        canton=canton,
        volume="1.3",
        title="Sachregister und Glossar",
        editors=["Peter Stotz"],
    )

    assert volume.canton == canton


@pytest.mark.parametrize(
    "values",
    [
        {"canton": "Zug", "volume": "1.3", "title": "Register", "editors": ["A"]},
        {"canton": "BS//BL", "volume": "1.3", "title": "Register", "editors": ["A"]},
        {"canton": "BS/BL/AG", "volume": "1.3", "title": "Register", "editors": ["A"]},
        {"canton": "ZG", "volume": "1.3", "title": "Register", "editors": []},
    ],
)
def test_register_volume_rejects_invalid_required_values(values: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RegisterVolume.model_validate(values)
