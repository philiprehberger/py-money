# philiprehberger-money

[![Tests](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-money/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-money.svg)](https://pypi.org/project/philiprehberger-money/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-money)](https://github.com/philiprehberger/py-money/commits/main)

Precise monetary calculations using integer cents with currency support and formatting.

## Installation

```bash
pip install philiprehberger-money
```

## Usage

```python
from philiprehberger_money import Money

price = Money.from_major(19.99, "USD")
print(price.format(symbol="$"))  # "$19.99"
```

### Creating Money

```python
from philiprehberger_money import Money

price = Money.from_major(19.99, "USD")
free = Money.zero("EUR")
```

### Arithmetic

```python
from philiprehberger_money import Money

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
from philiprehberger_money import Money, CurrencyMismatchError

usd = Money.from_major(10, "USD")
eur = Money.from_major(10, "EUR")

usd + eur  # raises CurrencyMismatchError
```

### Allocation (Split Without Losing Cents)

```python
from philiprehberger_money import Money

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
from philiprehberger_money import Money

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
from philiprehberger_money import Money

usd = Money.from_major(100, "USD")

# Direct rate
eur = usd.convert("EUR", 0.92)
print(eur.format())  # "92.00 EUR"

# Using a rates dictionary
eur = usd.convert(to="EUR", rates={"USD/EUR": 0.92})

# Using a rate provider callable
def get_rate(from_currency: str, to_currency: str) -> float:
    return 0.92  # fetch from API, database, etc.

eur = usd.convert(to="EUR", rate_provider=get_rate)
```

### Locale-Aware Formatting

```python
from philiprehberger_money import Money

price = Money.from_major(1234.56, "USD")

print(price.format())                 # "1234.56 USD"
print(price.format(symbol="$"))       # "$1234.56"
print(price.format(locale="en_US"))   # "$1,234.56"
print(price.format(locale="de_DE"))   # "$1.234,56"
```

### Rounding Modes

```python
from philiprehberger_money import Money, RoundingMode, set_default_rounding_mode

# Per-instance rounding mode
m = Money(amount_cents=5, currency="USD", rounding_mode=RoundingMode.ROUND_HALF_EVEN)
result = m.divide(2)  # 2.5 -> 2 (banker's rounding)

# Change rounding mode on existing instance
m2 = m.with_rounding_mode(RoundingMode.ROUND_UP)

# Set global default (affects all instances without explicit mode)
set_default_rounding_mode(RoundingMode.ROUND_HALF_EVEN)
```

### Comparisons

```python
from philiprehberger_money import Money

a = Money.from_major(10, "USD")
b = Money.from_major(20, "USD")

a < b   # True
a == b  # False
a.is_positive()  # True
a.is_zero()      # False
```

### Zero-Decimal Currencies

```python
from philiprehberger_money import Money

yen = Money.from_major(1000, "JPY")
print(yen.format(symbol="\u00a5"))  # "\u00a51000"
```

### Serialization

```python
from philiprehberger_money import Money

m = Money.from_major(19.99, "USD")

d = m.to_dict()           # {"amount_cents": 1999, "currency": "USD"}
m2 = Money.from_dict(d)   # Money(19.99 USD)
```

### Sum Multiple Values

```python
from philiprehberger_money import Money

items = [Money.from_major(10, "USD"), Money.from_major(20, "USD"), Money.from_major(30, "USD")]
total = Money.sum(items)
print(total.format(symbol="$"))  # "$60.00"
```

### Percentage

```python
from philiprehberger_money import Money

price = Money.from_major(200, "USD")
tip = price.percentage(15)
print(tip.format(symbol="$"))  # "$30.00"
```

### Even Split

```python
from philiprehberger_money import Money

bill = Money.from_major(100, "USD")
shares = bill.split_even(3)
# [Money($33.34), Money($33.33), Money($33.33)]
```

## API

| Function / Class | Description |
|---|---|
| `Money.from_major(amount, currency, *, rounding_mode=None)` | Create from major units (dollars, euros, etc.) |
| `Money.zero(currency, *, rounding_mode=None)` | Create zero-value Money |
| `Money.from_dict(data)` | Create from dict |
| `.add(other)` / `+` | Add two Money values (same currency) |
| `.subtract(other)` / `-` | Subtract (same currency) |
| `.multiply(factor)` / `*` | Multiply by number |
| `.divide(divisor)` | Divide by number |
| `.allocate(ratios)` | Split into parts without losing cents |
| `.round_to_nearest(step)` | Round minor units to nearest multiple |
| `.convert(to, rate=None, *, rates=None, rate_provider=None)` | Convert to another currency using a rate, rates dict, or callable |
| `.format(symbol=None, *, locale=None)` | Format as string, optionally locale-aware |
| `.with_rounding_mode(mode)` | Return copy with specified rounding mode |
| `.negate()` / `-m` | Negate amount |
| `.abs()` | Absolute value |
| `.is_zero()` / `.is_positive()` / `.is_negative()` | Predicates |
| `.to_dict()` | Serialize to dict |
| `.amount` | Major unit value as float |
| `.decimals` | Currency decimal places |
| `Money.sum(moneys)` | Sum a list of Money values (same currency) |
| `.percentage(pct)` | Calculate a percentage of this money value |
| `.split_even(n)` | Split evenly into n parts, distributing remainders |
| `RoundingMode` | Enum: ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP |
| `set_default_rounding_mode(mode)` | Set global default rounding mode |
| `get_default_rounding_mode()` | Get current global default rounding mode |
| `CurrencyMismatchError` | Raised on mixed-currency operations |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-money)

🐛 [Report issues](https://github.com/philiprehberger/py-money/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-money/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
