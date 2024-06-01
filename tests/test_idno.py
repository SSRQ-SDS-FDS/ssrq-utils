import pytest

from ssrq_utils.idno import model


@pytest.mark.parametrize(
    ("idno", "expected"),
    [
        (
            "SSRQ-SG-III_4-58-1",
            model.IDNO(prefix="SSRQ", kanton="SG", volume="III_4", doc=58, num=1),
        ),
        (
            "SSRQ-FR-I_2_8-2.0-1",
            model.IDNO(prefix="SSRQ", kanton="FR", volume="I_2_8", case=2, doc=0, num=1),
        ),
        (
            "SDS-NE-4-1.0-1",
            model.IDNO(prefix="SDS", kanton="NE", volume="4", case=1, doc=0, num=1),
        ),
        (
            "SDS-NE-4-1.A.1-1",
            model.IDNO(prefix="SDS", kanton="NE", volume="4", opening="1.A", doc=1, num=1),
        ),
    ],
)
def test_idno_model_validate_string(idno: str, expected: model.IDNO):
    model_instance = model.IDNO.model_validate_string(idno)
    for k, v in expected.model_dump().items():
        assert getattr(model_instance, k) == v


@pytest.mark.parametrize(
    ("idno", "expected"),
    [
        (
            model.IDNO(prefix="SSRQ", kanton="SG", volume="III_4", doc=58, num=1),
            "SSRQ-SG-III_4-58-1",
        ),
        (
            model.IDNO(prefix="SSRQ", kanton="FR", volume="I_2_8", case=2, doc=0, num=1),
            "SSRQ-FR-I_2_8-2.0-1",
        ),
        (
            model.IDNO(prefix="SDS", kanton="NE", volume="4", case=1, doc=0, num=1),
            "SDS-NE-4-1.0-1",
        ),
        (
            model.IDNO(prefix="SDS", kanton="NE", volume="4", opening="1.A", doc=1, num=1),
            "SDS-NE-4-1.A.1-1",
        ),
    ],
)
def test_idno_repr(idno: model.IDNO, expected: str):
    assert idno.__repr__() == expected


def test_invalid_idno():
    with pytest.raises(ValueError):  # noqa: PT011
        model.IDNO.model_validate_string("SSRQ-SG-III_4-58-1.0-1")


def test_exclusive_fields_set():
    with pytest.raises(ValueError):  # noqa: PT011
        (
            model.IDNO(
                prefix="SSRQ", kanton="SG", volume="III_4", doc=58, num=1, case=1, special="lit"
            ),
        )  # type: ignore