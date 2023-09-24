# Changelog

## 0.4.0 (2026-03-28)

- Add locale-aware formatting via `money.format(locale="en_US")` with proper currency symbols, thousands separators, and decimal places
- Add currency exchange with pluggable rate providers: `rates` dict and `rate_provider` callable support on `convert()`
- Add `RoundingMode` enum (ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP) configurable per-instance or globally
- Add `with_rounding_mode()` method to create Money with a different rounding mode
- Add `set_default_rounding_mode()` and `get_default_rounding_mode()` for global rounding configuration
- Rounding modes affect `multiply()`, `divide()`, `allocate()`, and `convert()`

## 0.3.0 (2026-03-27)

- Add `round_to_nearest(step)` for denomination rounding (e.g., nearest 5 cents)
- Add `convert(target_currency, rate)` for currency conversion
- Add 8 badges, Support section, and issue templates to README
- Add `[tool.pytest.ini_options]` and `[tool.mypy]` to pyproject.toml

## 0.2.3

- Add Development section to README
- Add wheel build target to pyproject.toml

## 0.2.0

- Fix `from_major` string precision using `Decimal` instead of float conversion
- Add `to_dict()` and `from_dict()` for serialization
- Add `__neg__` operator for `-money` syntax
- Add comprehensive test suite (~30 tests)
- Add API reference table to README

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0
- Initial release
