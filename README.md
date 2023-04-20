# philiprehberger-money

[![Tests](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-money.svg)](https://pypi.org/project/philiprehberger-money/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-money)](https://github.com/philiprehberger/py-money/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-money)](https://github.com/philiprehberger/py-money/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-money)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-money/bug)](https://github.com/philiprehberger/py-money/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-money/enhancement)](https://github.com/philiprehberger/py-money/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
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

### Denomination Rounding

```python
price = Money.from_major(1.23, "USD")

# Round to nearest 5 cents
rounded = price.round_to_nearest(5)
print(rounded.format(symbol="$"))  # "$1.25"

# Round to nearest 10 cents
rounded = price.round_to_nearest(10)
print(rounded.format(symbol="$"))  # "$1.20"
```

### Currency Conversion

```python
usd = Money.from_major(100, "USD")

# Convert USD to EUR at rate 0.92
eur = usd.convert("EUR", 0.92)
print(eur.format())  # "92.00 EUR"

# Convert to zero-decimal currency
jpy = usd.convert("JPY", 149.5)
print(jpy.format(symbol="\u00a5"))  # "\u00a514950"
```

### Formatting

```python
price = Money.from_major(1234.56, "USD")

print(price.format())           # "1234.56 USD"
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

## API

| Function / Class | Description |
|---|---|
| `Money.from_major(amount, currency)` | Create from major units (dollars, euros, etc.) |
| `Money.zero(currency)` | Create zero-value Money |
| `Money.from_dict(data)` | Create from dict |
| `.add(other)` / `+` | Add two Money values (same currency) |
| `.subtract(other)` / `-` | Subtract (same currency) |
| `.multiply(factor)` / `*` | Multiply by number |
| `.divide(divisor)` | Divide by number |
| `.allocate(ratios)` | Split into parts without losing cents |
| `.round_to_nearest(step)` | Round minor units to nearest multiple |
| `.convert(target_currency, rate)` | Convert to another currency at given rate |
| `.negate()` / `-m` | Negate amount |
| `.abs()` | Absolute value |
| `.is_zero()` / `.is_positive()` / `.is_negative()` | Predicates |
| `.format(symbol=None)` | Format as string |
| `.to_dict()` | Serialize to dict |
| `.amount` | Major unit value as float |
| `.decimals` | Currency decimal places |
| `CurrencyMismatchError` | Raised on mixed-currency operations |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
