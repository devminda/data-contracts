from data_contracts.validation import Severity, validate_data

SCHEMA = {"symbol": str, "price": float, "volume": int}


class TestValidData:
    def test_exact_match_passes(self):
        assert validate_data(SCHEMA, {"symbol": "AAPL", "price": 182.5, "volume": 1000}).is_valid

    def test_int_fills_float_field(self):
        assert validate_data(SCHEMA, {"symbol": "AAPL", "price": 182, "volume": 1000}).is_valid


class TestMissingFields:
    def test_single_missing_field(self):
        result = validate_data(SCHEMA, {"symbol": "AAPL", "price": 100.0})
        assert not result.is_valid
        assert any("volume" in e.message for e in result.errors)

    def test_all_missing(self):
        assert len(validate_data(SCHEMA, {}).errors) == 3


class TestWrongTypes:
    def test_string_for_float(self):
        result = validate_data(SCHEMA, {"symbol": "AAPL", "price": "oops", "volume": 100})
        assert not result.is_valid and any(e.field_name == "price" for e in result.errors)

    def test_float_for_int(self):
        assert not validate_data(SCHEMA, {"symbol": "AAPL", "price": 100.0, "volume": 99.5}).is_valid


class TestExtraFields:
    def test_extra_is_warning_not_error(self):
        result = validate_data(SCHEMA, {"symbol": "AAPL", "price": 100.0, "volume": 50, "new_field": "x"})
        assert result.is_valid and len(result.warnings) == 1
        assert result.warnings[0].severity == Severity.WARNING
