from __future__ import annotations

import pytest

from philiprehberger_money import (
    Money,
    CurrencyMismatchError,
    RoundingMode,
    get_default_rounding_mode,
    set_default_rounding_mode,
)


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


# --- round_to_nearest ---

def test_round_to_nearest_5_cents():
    m = Money.from_major("1.23", "USD")
    assert m.round_to_nearest(5).amount_cents == 125

def test_round_to_nearest_10_cents():
    m = Money.from_major("1.23", "USD")
    assert m.round_to_nearest(10).amount_cents == 120

def test_round_to_nearest_already_exact():
    m = Money.from_major("1.25", "USD")
    assert m.round_to_nearest(5).amount_cents == 125

def test_round_to_nearest_invalid_step():
    with pytest.raises(ValueError):
        Money.from_major(10, "USD").round_to_nearest(0)


# --- convert (basic, positional rate) ---

def test_convert_usd_to_eur():
    m = Money.from_major(100, "USD")
    eur = m.convert("EUR", 0.92)
    assert eur.amount_cents == 9200
    assert eur.currency == "EUR"

def test_convert_to_zero_decimal():
    m = Money.from_major(100, "USD")
    jpy = m.convert("JPY", 149.5)
    assert jpy.amount_cents == 14950
    assert jpy.currency == "JPY"


# --- convert with rates dict ---

def test_convert_with_rates_dict():
    m = Money.from_major(100, "USD")
    eur = m.convert(to="EUR", rates={"USD/EUR": 0.92})
    assert eur.amount_cents == 9200
    assert eur.currency == "EUR"

def test_convert_with_rates_dict_missing_key():
    m = Money.from_major(100, "USD")
    with pytest.raises(KeyError, match="USD/GBP"):
        m.convert(to="GBP", rates={"USD/EUR": 0.92})


# --- convert with rate_provider callable ---

def test_convert_with_rate_provider():
    def provider(from_cur: str, to_cur: str) -> float:
        if from_cur == "USD" and to_cur == "EUR":
            return 0.92
        raise ValueError("Unknown pair")

    m = Money.from_major(100, "USD")
    eur = m.convert(to="EUR", rate_provider=provider)
    assert eur.amount_cents == 9200

def test_convert_rate_provider_error():
    def provider(from_cur: str, to_cur: str) -> float:
        raise ValueError("No rate")

    m = Money.from_major(100, "USD")
    with pytest.raises(ValueError, match="No rate"):
        m.convert(to="GBP", rate_provider=provider)


# --- convert validation ---

def test_convert_no_rate_source():
    m = Money.from_major(100, "USD")
    with pytest.raises(ValueError, match="exactly one"):
        m.convert(to="EUR")

def test_convert_multiple_rate_sources():
    m = Money.from_major(100, "USD")
    with pytest.raises(ValueError, match="exactly one"):
        m.convert(to="EUR", rate=0.92, rates={"USD/EUR": 0.92})


# --- Locale-aware formatting ---

def test_format_locale_en_us():
    m = Money.from_major(1234.56, "USD")
    result = m.format(locale="en_US")
    # Should contain a currency symbol and the number with grouping.
    assert "$" in result
    assert "1" in result and "234" in result

def test_format_locale_de_de():
    m = Money.from_major(1234.56, "EUR")
    result = m.format(locale="de_DE")
    # German locale uses comma as decimal separator.
    assert "\u20ac" in result

def test_format_locale_negative():
    m = Money(amount_cents=-100050, currency="USD")
    result = m.format(locale="en_US")
    assert result.startswith("-")

def test_format_locale_jpy():
    m = Money.from_major(10000, "JPY")
    result = m.format(locale="en_US")
    assert "\u00a5" in result


# --- Rounding modes ---

def test_rounding_mode_half_up():
    m = Money(amount_cents=5, currency="USD", rounding_mode=RoundingMode.ROUND_HALF_UP)
    result = m.divide(2)
    # 5 / 2 = 2.5 -> rounds to 3 with HALF_UP
    assert result.amount_cents == 3

def test_rounding_mode_half_even():
    m = Money(amount_cents=5, currency="USD", rounding_mode=RoundingMode.ROUND_HALF_EVEN)
    result = m.divide(2)
    # 5 / 2 = 2.5 -> rounds to 2 with HALF_EVEN (banker's rounding)
    assert result.amount_cents == 2

def test_rounding_mode_down():
    m = Money(amount_cents=7, currency="USD", rounding_mode=RoundingMode.ROUND_DOWN)
    result = m.divide(2)
    # 7 / 2 = 3.5 -> rounds to 3 with DOWN
    assert result.amount_cents == 3

def test_rounding_mode_up():
    m = Money(amount_cents=7, currency="USD", rounding_mode=RoundingMode.ROUND_UP)
    result = m.divide(2)
    # 7 / 2 = 3.5 -> rounds to 4 with UP
    assert result.amount_cents == 4

def test_rounding_mode_on_multiply():
    m = Money(amount_cents=10, currency="USD", rounding_mode=RoundingMode.ROUND_DOWN)
    result = m.multiply(0.33)
    # 10 * 0.33 = 3.3 -> rounds to 3 with DOWN
    assert result.amount_cents == 3

def test_rounding_mode_on_multiply_up():
    m = Money(amount_cents=10, currency="USD", rounding_mode=RoundingMode.ROUND_UP)
    result = m.multiply(0.33)
    # 10 * 0.33 = 3.3 -> rounds to 4 with UP
    assert result.amount_cents == 4

def test_with_rounding_mode():
    m = Money.from_major(10, "USD")
    m2 = m.with_rounding_mode(RoundingMode.ROUND_DOWN)
    assert m2.rounding_mode == RoundingMode.ROUND_DOWN
    assert m2.amount_cents == m.amount_cents

def test_from_major_with_rounding_mode():
    m = Money.from_major(10, "USD", rounding_mode=RoundingMode.ROUND_DOWN)
    assert m.rounding_mode == RoundingMode.ROUND_DOWN

def test_allocate_with_rounding_mode():
    m = Money(amount_cents=10, currency="USD", rounding_mode=RoundingMode.ROUND_DOWN)
    parts = m.allocate([1, 1, 1])
    assert sum(p.amount_cents for p in parts) == 10


# --- Global default rounding mode ---

def test_global_default_rounding_mode():
    original = get_default_rounding_mode()
    try:
        set_default_rounding_mode(RoundingMode.ROUND_DOWN)
        m = Money(amount_cents=7, currency="USD")
        result = m.divide(2)
        assert result.amount_cents == 3
    finally:
        set_default_rounding_mode(original)

def test_instance_rounding_overrides_global():
    original = get_default_rounding_mode()
    try:
        set_default_rounding_mode(RoundingMode.ROUND_DOWN)
        m = Money(amount_cents=7, currency="USD", rounding_mode=RoundingMode.ROUND_UP)
        result = m.divide(2)
        assert result.amount_cents == 4
    finally:
        set_default_rounding_mode(original)


# --- Hash support ---

def test_hash_equal_values():
    a = Money.from_major(10, "USD")
    b = Money.from_major(10, "USD")
    assert hash(a) == hash(b)

def test_money_in_set():
    a = Money.from_major(10, "USD")
    b = Money.from_major(10, "USD")
    s = {a, b}
    assert len(s) == 1


def test_sum_money():
    items = [
        Money.from_major(10, "USD"),
        Money.from_major(20, "USD"),
        Money.from_major(30, "USD"),
    ]
    result = Money.sum(items)
    assert result.amount_cents == 6000
    assert result.currency == "USD"


def test_sum_empty():
    try:
        Money.sum([])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_sum_currency_mismatch():
    items = [Money.from_major(10, "USD"), Money.from_major(10, "EUR")]
    try:
        Money.sum(items)
        assert False, "Should have raised CurrencyMismatchError"
    except CurrencyMismatchError:
        pass


def test_percentage():
    price = Money.from_major(200, "USD")
    tip = price.percentage(15)
    assert tip.amount_cents == 3000  # $30.00


def test_percentage_small():
    price = Money.from_major(10, "USD")
    tax = price.percentage(8.5)
    assert tax.amount_cents == 85  # $0.85


def test_split_even():
    total = Money.from_major(10, "USD")
    parts = total.split_even(3)
    assert len(parts) == 3
    assert sum(p.amount_cents for p in parts) == 1000


def test_split_even_one():
    total = Money.from_major(50, "USD")
    parts = total.split_even(1)
    assert len(parts) == 1
    assert parts[0].amount_cents == 5000


def test_split_even_invalid():
    total = Money.from_major(10, "USD")
    try:
        total.split_even(0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
