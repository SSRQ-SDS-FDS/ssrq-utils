import maturin_import_hook
from maturin_import_hook.settings import MaturinSettings

maturin_import_hook.install(settings=MaturinSettings(uv=True))

from ssrq_utils.uca import uca_complex_sort, uca_simple_sort  # noqa: E402


def test_uca_simple_sort():
    data = ["Apfel", "Äpfel", "apfel", "Banane"]
    result = uca_simple_sort(data)
    assert result == ["apfel", "Apfel", "Äpfel", "Banane"]


def test_uca_complex_sort():
    data = [{"name": "Apfel"}, {"name": "Äpfel"}, {"name": "apfel"}, {"name": "Banane"}]
    result = uca_complex_sort(data, "get", ("name",))
    assert result == [{"name": "apfel"}, {"name": "Apfel"}, {"name": "Äpfel"}, {"name": "Banane"}]
