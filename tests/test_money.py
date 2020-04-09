from __future__ import annotations

import pytest

from philiprehberger_money import Money, CurrencyMismatchError


# --- Creation ---

def test_from_major_float():
    m = Money.from_major(19.99, "USD")
    assert m.amount_cents == 1999

def test_from_major_int():
    m = Money.from_major(10, "USD")
    assert m.amount_cents == 1000

def test_from_major_string():
    m = Money.from_major("19.99", "USD")
    assert m.amount_cents == 1999

def test_zero():
    m = Money.zero("EUR")
    assert m.amount_cents == 0
    assert m.currency == "EUR"

def test_direct_constructor():
    m = Money(amount_cents=500, currency="USD")
    assert m.amount_cents == 500


# --- Precision ---

def test_from_major_string_precision():
    m = Money.from_major("0.10", "USD")
    assert m.amount_cents == 10


# --- Currency ---

def test_uppercase_normalization():
    m = Money.from_major(1, "usd")
    assert m.currency == "USD"

def test_jpy_zero_decimals():
    m = Money.from_major(1000, "JPY")
    assert m.amount_cents == 1000
    assert m.decimals == 0

def test_unknown_currency_defaults_to_2():
    m = Money.from_major(1.50, "XYZ")
    assert m.amount_cents == 150


# --- Arithmetic ---

def test_add():
    a = Money.from_major(10, "USD")
    b = Money.from_major(5, "USD")
    assert a.add(b).amount_cents == 1500

def test_subtract():
    a = Money.from_major(10, "USD")
    b = Money.from_major(3, "USD")
    assert a.subtract(b).amount_cents == 700

def test_multiply_int():
    m = Money.from_major(10, "USD")
    assert m.multiply(3).amount_cents == 3000

def test_multiply_float():
    m = Money.from_major(10, "USD")
    assert m.multiply(1.5).amount_cents == 1500

def test_divide():
    m = Money.from_major(10, "USD")
    assert m.divide(3).amount_cents == 333

def test_operator_add():
    a = Money.from_major(10, "USD")
    b = Money.from_major(5, "USD")
    assert (a + b).amount_cents == 1500

def test_operator_sub():
    a = Money.from_major(10, "USD")
    b = Money.from_major(3, "USD")
    assert (a - b).amount_cents == 700

def test_operator_mul():
    m = Money.from_major(10, "USD")
    assert (m * 2).amount_cents == 2000


# --- Currency mismatch ---

def test_add_different_currencies():
    with pytest.raises(CurrencyMismatchError):
        Money.from_major(10, "USD").add(Money.from_major(10, "EUR"))

def test_subtract_different_currencies():
    with pytest.raises(CurrencyMismatchError):
        Money.from_major(10, "USD").subtract(Money.from_major(10, "EUR"))

def test_compare_different_currencies():
    with pytest.raises(CurrencyMismatchError):
        Money.from_major(10, "USD") < Money.from_major(10, "EUR")


# --- Division by zero ---

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        Money.from_major(10, "USD").divide(0)


# --- Allocate ---

def test_allocate_even():
    m = Money.from_major(10, "USD")
    parts = m.allocate([1, 1])
    assert parts[0].amount_cents == 500
    assert parts[1].amount_cents == 500

def test_allocate_uneven():
    m = Money.from_major(10, "USD")
    parts = m.allocate([1, 1, 1])
    total = sum(p.amount_cents for p in parts)
    assert total == 1000

def test_allocate_ratios():
    m = Money.from_major(100, "USD")
    parts = m.allocate([50, 30, 20])
    assert parts[0].amount_cents == 5000
    assert parts[1].amount_cents == 3000
    assert parts[2].amount_cents == 2000

def test_allocate_sum_equals_original():
    m = Money(amount_cents=1001, currency="USD")
    parts = m.allocate([1, 1, 1])
    assert sum(p.amount_cents for p in parts) == 1001


# --- Allocate edge ---

def test_allocate_zero_ratios():
    with pytest.raises(ValueError):
        Money.from_major(10, "USD").allocate([0, 0, 0])


# --- Comparisons ---

def test_less_than():
    assert Money.from_major(5, "USD") < Money.from_major(10, "USD")

def test_less_equal():
    assert Money.from_major(5, "USD") <= Money.from_major(5, "USD")

def test_greater_than():
    assert Money.from_major(10, "USD") > Money.from_major(5, "USD")

def test_greater_equal():
    assert Money.from_major(10, "USD") >= Money.from_major(10, "USD")

def test_equal():
    assert Money.from_major(10, "USD") == Money.from_major(10, "USD")

def test_equal_different_currency():
    assert Money.from_major(10, "USD") != Money.from_major(10, "EUR")


# --- Predicates ---

def test_is_zero():
    assert Money.zero("USD").is_zero()
    assert not Money.from_major(1, "USD").is_zero()

def test_is_positive():
    assert Money.from_major(1, "USD").is_positive()
    assert not Money(amount_cents=-1, currency="USD").is_positive()

def test_is_negative():
    assert Money(amount_cents=-1, currency="USD").is_negative()
    assert not Money.from_major(1, "USD").is_negative()


# --- abs / negate / __neg__ ---

def test_abs():
    m = Money(amount_cents=-500, currency="USD")
    assert m.abs().amount_cents == 500

def test_negate():
    m = Money.from_major(10, "USD")
    assert m.negate().amount_cents == -1000

def test_neg_operator():
    m = Money.from_major(10, "USD")
    assert (-m).amount_cents == -1000


# --- Format ---

def test_format_without_symbol():
    m = Money.from_major(1234.56, "USD")
    assert m.format() == "1234.56 USD"

def test_format_with_symbol():
    m = Money.from_major(1234.56, "USD")
    assert m.format(symbol="$") == "$1234.56"

def test_format_negative():
    m = Money(amount_cents=-1050, currency="USD")
    assert m.format(symbol="$") == "-$10.50"

def test_format_jpy():
    m = Money.from_major(1000, "JPY")
    assert m.format(symbol="\u00a5") == "\u00a51000"


# --- to_dict / from_dict ---

def test_to_dict():
    m = Money(amount_cents=1999, currency="USD")
    assert m.to_dict() == {"amount_cents": 1999, "currency": "USD"}

def test_from_dict():
    d = {"amount_cents": 1999, "currency": "USD"}
    m = Money.from_dict(d)
    assert m.amount_cents == 1999
    assert m.currency == "USD"

def test_round_trip():
    m = Money.from_major(19.99, "USD")
    assert Money.from_dict(m.to_dict()) == m


# --- repr / str ---

def test_repr():
    m = Money.from_major(10, "USD")
    assert "10.00 USD" in repr(m)

def test_str():
    m = Money.from_major(10, "USD")
    assert str(m) == "10.00 USD"
