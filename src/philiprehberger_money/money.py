from __future__ import annotations

import locale as _locale_mod
from dataclasses import dataclass, field
from decimal import ROUND_DOWN as _ROUND_DOWN
from decimal import ROUND_HALF_EVEN as _ROUND_HALF_EVEN
from decimal import ROUND_HALF_UP as _ROUND_HALF_UP
from decimal import ROUND_UP as _ROUND_UP
from decimal import Decimal
from enum import Enum
from typing import Any, Callable


__all__ = [
    "Money",
    "CurrencyMismatchError",
    "RoundingMode",
    "CURRENCY_DECIMALS",
]


CURRENCY_DECIMALS: dict[str, int] = {
    "USD": 2, "EUR": 2, "GBP": 2, "JPY": 0, "CHF": 2,
    "CAD": 2, "AUD": 2, "NZD": 2, "SEK": 2, "NOK": 2,
    "DKK": 2, "PLN": 2, "CZK": 2, "HUF": 2, "BRL": 2,
    "MXN": 2, "INR": 2, "CNY": 2, "KRW": 0, "SGD": 2,
    "HKD": 2, "TWD": 2, "THB": 2, "ZAR": 2, "RUB": 2,
}

# Mapping of currency codes to their symbols for locale formatting.
_CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5",
    "CHF": "CHF", "CAD": "CA$", "AUD": "A$", "NZD": "NZ$",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "z\u0142",
    "CZK": "K\u010d", "HUF": "Ft", "BRL": "R$", "MXN": "MX$",
    "INR": "\u20b9", "CNY": "\u00a5", "KRW": "\u20a9", "SGD": "S$",
    "HKD": "HK$", "TWD": "NT$", "THB": "\u0e3f", "ZAR": "R",
    "RUB": "\u20bd",
}


class RoundingMode(Enum):
    """Rounding modes for monetary arithmetic."""

    ROUND_HALF_UP = "ROUND_HALF_UP"
    ROUND_HALF_EVEN = "ROUND_HALF_EVEN"
    ROUND_DOWN = "ROUND_DOWN"
    ROUND_UP = "ROUND_UP"


_ROUNDING_MAP = {
    RoundingMode.ROUND_HALF_UP: _ROUND_HALF_UP,
    RoundingMode.ROUND_HALF_EVEN: _ROUND_HALF_EVEN,
    RoundingMode.ROUND_DOWN: _ROUND_DOWN,
    RoundingMode.ROUND_UP: _ROUND_UP,
}

# Module-level default rounding mode.
_default_rounding_mode: RoundingMode = RoundingMode.ROUND_HALF_UP


def set_default_rounding_mode(mode: RoundingMode) -> None:
    """Set the global default rounding mode for all Money operations."""
    global _default_rounding_mode  # noqa: PLW0603
    _default_rounding_mode = mode


def get_default_rounding_mode() -> RoundingMode:
    """Get the current global default rounding mode."""
    return _default_rounding_mode


class CurrencyMismatchError(Exception):
    def __init__(self, a: str, b: str) -> None:
        super().__init__(f"Cannot operate on different currencies: {a} and {b}")


def _round_cents(value: Decimal, mode: RoundingMode) -> int:
    """Round a Decimal value to the nearest integer using the given mode."""
    return int(value.to_integral_value(rounding=_ROUNDING_MAP[mode]))


@dataclass(frozen=True)
class Money:
    amount_cents: int
    currency: str
    rounding_mode: RoundingMode | None = field(default=None, repr=False, compare=False)

    @property
    def _effective_rounding(self) -> RoundingMode:
        """Return the instance rounding mode, falling back to global default."""
        if self.rounding_mode is not None:
            return self.rounding_mode
        return _default_rounding_mode

    @classmethod
    def from_major(
        cls,
        amount: float | int | str,
        currency: str,
        *,
        rounding_mode: RoundingMode | None = None,
    ) -> Money:
        currency = currency.upper()
        decimals = CURRENCY_DECIMALS.get(currency, 2)
        factor = 10 ** decimals
        if isinstance(amount, str):
            cents = round(Decimal(amount) * factor)
        else:
            cents = round(float(amount) * factor)
        return cls(amount_cents=cents, currency=currency, rounding_mode=rounding_mode)

    @classmethod
    def zero(cls, currency: str, *, rounding_mode: RoundingMode | None = None) -> Money:
        return cls(amount_cents=0, currency=currency.upper(), rounding_mode=rounding_mode)

    @property
    def decimals(self) -> int:
        return CURRENCY_DECIMALS.get(self.currency, 2)

    @property
    def amount(self) -> float:
        return self.amount_cents / (10 ** self.decimals)

    def with_rounding_mode(self, mode: RoundingMode) -> Money:
        """Return a new Money instance with the specified rounding mode."""
        return Money(
            amount_cents=self.amount_cents,
            currency=self.currency,
            rounding_mode=mode,
        )

    def _check_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)

    def _make(self, cents: int) -> Money:
        """Create a new Money with same currency and rounding mode."""
        return Money(amount_cents=cents, currency=self.currency, rounding_mode=self.rounding_mode)

    def add(self, other: Money) -> Money:
        self._check_currency(other)
        return self._make(self.amount_cents + other.amount_cents)

    def subtract(self, other: Money) -> Money:
        self._check_currency(other)
        return self._make(self.amount_cents - other.amount_cents)

    def multiply(self, factor: float | int) -> Money:
        result = Decimal(str(self.amount_cents)) * Decimal(str(factor))
        return self._make(_round_cents(result, self._effective_rounding))

    def divide(self, divisor: float | int) -> Money:
        if divisor == 0:
            raise ZeroDivisionError("Cannot divide money by zero")
        result = Decimal(str(self.amount_cents)) / Decimal(str(divisor))
        return self._make(_round_cents(result, self._effective_rounding))

    def allocate(self, ratios: list[int]) -> list[Money]:
        total = sum(ratios)
        if total == 0:
            raise ValueError("Ratios must sum to a positive number")

        rounding = self._effective_rounding
        results: list[Money] = []
        remainder = self.amount_cents

        for ratio in ratios:
            share_dec = Decimal(str(self.amount_cents)) * Decimal(str(ratio)) / Decimal(str(total))
            share = _round_cents(share_dec, rounding)
            results.append(self._make(share))
            remainder -= share

        # Distribute any remaining cents to the first buckets.
        for i in range(abs(remainder)):
            idx = i % len(results)
            sign = 1 if remainder > 0 else -1
            results[idx] = self._make(results[idx].amount_cents + sign)

        return results

    def is_zero(self) -> bool:
        return self.amount_cents == 0

    def is_positive(self) -> bool:
        return self.amount_cents > 0

    def is_negative(self) -> bool:
        return self.amount_cents < 0

    def abs(self) -> Money:
        return self._make(abs(self.amount_cents))

    def negate(self) -> Money:
        return self._make(-self.amount_cents)

    def to_dict(self) -> dict[str, Any]:
        return {"amount_cents": self.amount_cents, "currency": self.currency}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Money:
        return cls(amount_cents=data["amount_cents"], currency=data["currency"])

    def round_to_nearest(self, step: int) -> Money:
        if step <= 0:
            raise ValueError("step must be a positive integer")
        remainder = self.amount_cents % step
        if remainder == 0:
            rounded = self.amount_cents
        elif remainder >= step / 2:
            rounded = self.amount_cents + (step - remainder)
        else:
            rounded = self.amount_cents - remainder
        return self._make(rounded)

    def convert(
        self,
        to: str,
        rate: float | None = None,
        *,
        rates: dict[str, float] | None = None,
        rate_provider: Callable[[str, str], float] | None = None,
    ) -> Money:
        """Convert to another currency.

        Supports three ways to supply the exchange rate:
        - ``rate``: a direct numeric rate (positional or keyword)
        - ``rates``: a dict mapping ``"FROM/TO"`` strings to float rates
        - ``rate_provider``: a callable ``(from_currency, to_currency) -> float``

        Exactly one of the three must be provided.
        """
        target_currency = to.upper()

        # Resolve the effective rate from the provided source.
        sources_given = sum(x is not None for x in (rate, rates, rate_provider))
        if sources_given != 1:
            raise ValueError("Provide exactly one of: rate, rates, or rate_provider")

        effective_rate: float
        if rate is not None:
            effective_rate = rate
        elif rates is not None:
            key = f"{self.currency}/{target_currency}"
            if key not in rates:
                raise KeyError(f"Exchange rate not found for {key}")
            effective_rate = rates[key]
        else:
            assert rate_provider is not None
            effective_rate = rate_provider(self.currency, target_currency)

        target_decimals = CURRENCY_DECIMALS.get(target_currency, 2)
        source_decimals = self.decimals
        major_value = Decimal(str(self.amount_cents)) / Decimal(str(10 ** source_decimals))
        converted_major = major_value * Decimal(str(effective_rate))
        target_cents = _round_cents(
            converted_major * Decimal(str(10 ** target_decimals)),
            self._effective_rounding,
        )
        return Money(amount_cents=target_cents, currency=target_currency, rounding_mode=self.rounding_mode)

    def format(
        self,
        symbol: str | None = None,
        *,
        locale: str | None = None,
    ) -> str:
        """Format the money value as a string.

        Args:
            symbol: Currency symbol to prepend (e.g. ``"$"``).
            locale: Locale string (e.g. ``"en_US"``, ``"de_DE"``). When provided,
                formats with locale-appropriate thousands separator, decimal
                separator, and currency symbol. The ``symbol`` parameter is
                ignored when ``locale`` is set.
        """
        if locale is not None:
            return self._format_locale(locale)

        decimals = self.decimals
        if decimals == 0:
            formatted = str(abs(self.amount_cents))
        else:
            major = abs(self.amount_cents) // (10 ** decimals)
            minor = abs(self.amount_cents) % (10 ** decimals)
            formatted = f"{major}.{str(minor).zfill(decimals)}"

        prefix = "-" if self.amount_cents < 0 else ""

        if symbol:
            return f"{prefix}{symbol}{formatted}"
        return f"{prefix}{formatted} {self.currency}"

    def _format_locale(self, locale_str: str) -> str:
        """Format using stdlib locale conventions."""
        decimals = self.decimals
        abs_cents = abs(self.amount_cents)

        # Try to get locale conventions; fall back to C locale if unavailable.
        saved_locale = _locale_mod.getlocale(_locale_mod.LC_NUMERIC)
        try:
            try:
                _locale_mod.setlocale(_locale_mod.LC_NUMERIC, locale_str + ".UTF-8")
            except _locale_mod.Error:
                try:
                    _locale_mod.setlocale(_locale_mod.LC_NUMERIC, locale_str)
                except _locale_mod.Error:
                    _locale_mod.setlocale(_locale_mod.LC_NUMERIC, "C")
            conv = _locale_mod.localeconv()
        finally:
            try:
                _locale_mod.setlocale(_locale_mod.LC_NUMERIC, saved_locale)
            except (_locale_mod.Error, TypeError):
                _locale_mod.setlocale(_locale_mod.LC_NUMERIC, "C")

        thousands_sep: str = conv.get("thousands_sep") or ","  # type: ignore[assignment]
        decimal_point: str = conv.get("decimal_point") or "."  # type: ignore[assignment]

        if decimals == 0:
            major_str = str(abs_cents)
        else:
            major = abs_cents // (10 ** decimals)
            minor = abs_cents % (10 ** decimals)
            major_str = str(major)

        # Insert thousands separators.
        grouping_spec: list[int] = conv.get("grouping") or [3, 0]  # type: ignore[assignment]
        digits = list(major_str)
        grouped: list[str] = []
        group_idx = 0
        while digits:
            if group_idx < len(grouping_spec):
                group_size = grouping_spec[group_idx]
            else:
                group_size = grouping_spec[-1]
            if group_size == 0:
                # 0 means use the last group size for all remaining digits.
                if group_idx > 0:
                    group_size = grouping_spec[group_idx - 1]
                else:
                    group_size = 3
            # _CHAR_MAX (127) means no more grouping.
            if group_size == 127:
                grouped.insert(0, "".join(digits))
                digits = []
            else:
                chunk = digits[-group_size:]
                grouped.insert(0, "".join(chunk))
                digits = digits[:-group_size]
                group_idx += 1
        formatted_major = thousands_sep.join(grouped)

        if decimals == 0:
            number_str = formatted_major
        else:
            number_str = f"{formatted_major}{decimal_point}{str(minor).zfill(decimals)}"

        currency_symbol = _CURRENCY_SYMBOLS.get(self.currency, self.currency)

        prefix = "-" if self.amount_cents < 0 else ""
        return f"{prefix}{currency_symbol}{number_str}"

    def __neg__(self) -> Money:
        return self.negate()

    def __add__(self, other: Money) -> Money:
        return self.add(other)

    def __sub__(self, other: Money) -> Money:
        return self.subtract(other)

    def __mul__(self, factor: float | int) -> Money:
        return self.multiply(factor)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_cents == other.amount_cents and self.currency == other.currency

    def __lt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_cents < other.amount_cents

    def __le__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_cents <= other.amount_cents

    def __gt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_cents > other.amount_cents

    def __ge__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_cents >= other.amount_cents

    def __repr__(self) -> str:
        return f"Money({self.format()})"

    def __str__(self) -> str:
        return self.format()

    def __hash__(self) -> int:
        return hash((self.amount_cents, self.currency))
