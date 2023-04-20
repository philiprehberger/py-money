from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Self


CURRENCY_DECIMALS: dict[str, int] = {
    "USD": 2, "EUR": 2, "GBP": 2, "JPY": 0, "CHF": 2,
    "CAD": 2, "AUD": 2, "NZD": 2, "SEK": 2, "NOK": 2,
    "DKK": 2, "PLN": 2, "CZK": 2, "HUF": 2, "BRL": 2,
    "MXN": 2, "INR": 2, "CNY": 2, "KRW": 0, "SGD": 2,
    "HKD": 2, "TWD": 2, "THB": 2, "ZAR": 2, "RUB": 2,
}


class CurrencyMismatchError(Exception):
    def __init__(self, a: str, b: str) -> None:
        super().__init__(f"Cannot operate on different currencies: {a} and {b}")


@dataclass(frozen=True)
class Money:
    amount_cents: int
    currency: str

    @classmethod
    def from_major(cls, amount: float | int | str, currency: str) -> Money:
        currency = currency.upper()
        decimals = CURRENCY_DECIMALS.get(currency, 2)
        factor = 10 ** decimals
        if isinstance(amount, str):
            cents = round(Decimal(amount) * factor)
        else:
            cents = round(float(amount) * factor)
        return cls(amount_cents=cents, currency=currency)

    @classmethod
    def zero(cls, currency: str) -> Money:
        return cls(amount_cents=0, currency=currency.upper())

    @property
    def decimals(self) -> int:
        return CURRENCY_DECIMALS.get(self.currency, 2)

    @property
    def amount(self) -> float:
        return self.amount_cents / (10 ** self.decimals)

    def _check_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)

    def add(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(amount_cents=self.amount_cents + other.amount_cents, currency=self.currency)

    def subtract(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(amount_cents=self.amount_cents - other.amount_cents, currency=self.currency)

    def multiply(self, factor: float | int) -> Money:
        return Money(amount_cents=round(self.amount_cents * factor), currency=self.currency)

    def divide(self, divisor: float | int) -> Money:
        if divisor == 0:
            raise ZeroDivisionError("Cannot divide money by zero")
        return Money(amount_cents=round(self.amount_cents / divisor), currency=self.currency)

    def allocate(self, ratios: list[int]) -> list[Money]:
        total = sum(ratios)
        if total == 0:
            raise ValueError("Ratios must sum to a positive number")

        results: list[Money] = []
        remainder = self.amount_cents

        for ratio in ratios:
            share = self.amount_cents * ratio // total
            results.append(Money(amount_cents=share, currency=self.currency))
            remainder -= share

        for i in range(abs(remainder)):
            idx = i % len(results)
            sign = 1 if remainder > 0 else -1
            results[idx] = Money(amount_cents=results[idx].amount_cents + sign, currency=self.currency)

        return results

    def is_zero(self) -> bool:
        return self.amount_cents == 0

    def is_positive(self) -> bool:
        return self.amount_cents > 0

    def is_negative(self) -> bool:
        return self.amount_cents < 0

    def abs(self) -> Money:
        return Money(amount_cents=abs(self.amount_cents), currency=self.currency)

    def negate(self) -> Money:
        return Money(amount_cents=-self.amount_cents, currency=self.currency)

    def to_dict(self) -> dict:
        return {"amount_cents": self.amount_cents, "currency": self.currency}

    @classmethod
    def from_dict(cls, data: dict) -> Money:
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
        return Money(amount_cents=rounded, currency=self.currency)

    def convert(self, target_currency: str, rate: float) -> Money:
        target_currency = target_currency.upper()
        target_decimals = CURRENCY_DECIMALS.get(target_currency, 2)
        source_decimals = self.decimals
        major_value = self.amount_cents / (10 ** source_decimals)
        converted_major = major_value * rate
        target_cents = round(converted_major * (10 ** target_decimals))
        return Money(amount_cents=target_cents, currency=target_currency)

    def __neg__(self) -> Money:
        return self.negate()

    def format(self, symbol: str | None = None) -> str:
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
