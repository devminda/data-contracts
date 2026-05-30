import pytest
from data_contracts.registry import SchemaRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    SchemaRegistry.clear()
    yield
    SchemaRegistry.clear()


@pytest.fixture
def trade_v1_fields():
    return {"symbol": str, "price": float, "volume": int, "exchange": str}


@pytest.fixture
def trade_v2_fields():
    return {"symbol": str, "close_price": float, "volume": int, "timestamp": str}


@pytest.fixture
def valid_trade_row():
    return {"symbol": "AAPL", "price": 182.5, "volume": 1000, "exchange": "NASDAQ"}


@pytest.fixture
def invalid_trade_row():
    return {"symbol": "AAPL", "price": "not-a-float", "volume": 1000}
