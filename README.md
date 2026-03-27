# philiprehberger-money

[![Tests](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-money.svg)](https://pypi.org/project/philiprehberger-money/)
[![License](https://img.shields.io/github/license/philiprehberger/py-money)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Precise monetary calculations using integer cents with currency support and formatting.

## Installation

```bash
pip install philiprehberger-money
```

## Usage

### Creating Money

```python
from philiprehberger_money import Money

price = Money.from_major(19.99, "USD")
free = Money.zero("EUR")
```

### Arithmetic

```python
a = Money.from_major(10.00, "USD")
b = Money.from_major(3.50, "USD")

total = a + b          # $13.50
diff = a - b           # $6.50
doubled = a * 2        # $20.00
split = a.divide(3)    # $3.33 (rounded)
negated = -a           # -$10.00
```

### Safe Currency Handling

```python
usd = Money.from_major(10, "USD")
eur = Money.from_major(10, "EUR")

usd + eur  # raises CurrencyMismatchError
```

### Allocation (Split Without Losing Cents)

```python
total = Money.from_major(100.00, "USD")

# Split 50/30/20
shares = total.allocate([50, 30, 20])
# [Money($50.00), Money($30.00), Money($20.00)]

# Handles remainders correctly
odd = Money.from_major(10.00, "USD")
thirds = odd.allocate([1, 1, 1])
# [Money($3.34), Money($3.33), Money($3.33)]
```

### Formatting

```python
price = Money.from_major(1234.56, "USD")

print(price.format())          # "1234.56 USD"
print(price.format(symbol="$")) # "$1234.56"
```

### Comparisons

```python
a = Money.from_major(10, "USD")
b = Money.from_major(20, "USD")

a < b   # True
a == b  # False
a.is_positive()  # True
a.is_zero()      # False
```

### Zero-Decimal Currencies

```python
yen = Money.from_major(1000, "JPY")
print(yen.format(symbol="\u00a5"))  # "\u00a51000"
```

### Serialization

```python
m = Money.from_major(19.99, "USD")

d = m.to_dict()           # {"amount_cents": 1999, "currency": "USD"}
m2 = Money.from_dict(d)   # Money(19.99 USD)
```

## API Reference

| Method | Description |
|---|---|
| `Money.from_major(amount, currency)` | Create from major units (dollars, euros, etc.) |
| `Money.zero(currency)` | Create zero-value Money |
| `Money.from_dict(data)` | Create from dict |
| `.add(other)` / `+` | Add two Money values (same currency) |
| `.subtract(other)` / `-` | Subtract (same currency) |
| `.multiply(factor)` / `*` | Multiply by number |
| `.divide(divisor)` | Divide by number |
| `.allocate(ratios)` | Split into parts without losing cents |
| `.negate()` / `-m` | Negate amount |
| `.abs()` | Absolute value |
| `.is_zero()` / `.is_positive()` / `.is_negative()` | Predicates |
| `.format(symbol=None)` | Format as string |
| `.to_dict()` | Serialize to dict |
| `.amount` | Major unit value as float |
| `.decimals` | Currency decimal places |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
