"""End-to-end demo: price -> close_price API change scenario."""
import sys
sys.path.insert(0, "src")

from data_contracts import ContractBase, SchemaDiff
from data_contracts.notifications import Consumer, NotificationBus
from data_contracts.registry import SchemaRegistry


class TradeSchemaV1(ContractBase):
    __version__ = "1.0.0"
    symbol: str
    price: float
    volume: int
    exchange: str


print("=== Validation ===\n")
good = {"symbol": "AAPL", "price": 182.5, "volume": 1000, "exchange": "NASDAQ"}
bad  = {"symbol": "AAPL", "price": "one-eighty", "volume": 1000}
print(f"Good: {TradeSchemaV1.validate(good).summary()}")
print(f"Bad:  {TradeSchemaV1.validate(bad).summary()}")


class TradeSchemaV2(ContractBase):
    __version__ = "2.0.0"
    symbol: str
    close_price: float   # renamed from price (BREAKING)
    volume: int
    timestamp: str       # added (SAFE)
    # exchange removed   # also BREAKING


print("\n=== Schema diff ===")
old = SchemaRegistry.get_latest("TradeSchemaV1")
new = SchemaRegistry.get_latest("TradeSchemaV2")
assert old and new
report = SchemaDiff(old, new).generate_report()
report.print_report()


print("=== Notifications ===\n")
bus = NotificationBus()
bus.register(Consumer("Quant team",  "quant@firm.com", ["TradeSchemaV1"]))
bus.register(Consumer("Risk system", "risk@firm.com",  ["TradeSchemaV1"]))
bus.register(Consumer("ML pipeline", "ml@firm.com",    ["TradeSchemaV1"]))
bus.notify(report)
print(f"\n{len(bus.get_log())} notification(s) sent.")
