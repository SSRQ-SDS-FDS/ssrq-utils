import pytest

from ssrq_utils.idno import model as idno_model
from ssrq_utils.urn import model


@pytest.mark.parametrize(
    ("idno", "expected"),
    [
        (
            "urn:ssrq:SSRQ-SG-III_4-58-1",
            model.URN(idno="SSRQ-SG-III_4-58-1", fragment=None),
        ),
        (
            "urn:ssrq:SSRQ-SG-III_4-58-1#123",
            model.URN(idno="SSRQ-SG-III_4-58-1", fragment="123"),
        ),
    ],
)
def test_urn_model_validate_string(idno: str, expected: model.URN):
    model_instance = model.URN.model_validate_string(idno)
    for k, v in expected.model_dump().items():
        assert getattr(model_instance, k) == v


def test_urn_model_validate_string_with_casting():
    model_instance = model.URN.model_validate_string(
        "urn:ssrq:SSRQ-SG-III_4-58-1", cast_to_idno=True
    )
    assert isinstance(model_instance.idno, idno_model.IDNO)


def test_urn_model_validate_string_fails_for_invalid_urn():
    with pytest.raises(ValueError):  # noqa: PT011
        model.URN.model_validate_string("urn:ssrq:SSRQ-SG-III_4-58-1.0-1", urn_prefix="urn:foo:")
