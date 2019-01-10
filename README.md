# philiprehberger-money

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
print(yen.format(symbol="¥"))  # "¥1000"
```

## License

MIT
