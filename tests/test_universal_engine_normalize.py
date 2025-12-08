import pytest

from services.universal_engine import _normalize_col_key


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (None, ""),
        (" Ct ", "ct"),
        ("Сt", "ct"),  # cirílico C + t
        ("тarget", "target"),  # cirílico t
        ("с_sample", "csample"),  # cirílico c + underscore removido
        ("WELL", "well"),
        (" Target", "target"),
        ("CT", "ct"),
        ("Ct_mean", "ctmean"),
        ("Cт", "ct"),  # C + cirílico t
    ],
)
def test_normalize_col_key_variants(input_val, expected):
    assert _normalize_col_key(input_val) == expected
