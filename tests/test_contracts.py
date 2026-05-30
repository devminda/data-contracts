from data_contracts.contracts import ContractBase, contract
from data_contracts.registry import SchemaRegistry


class TestContractBase:
    def test_auto_registers_on_definition(self):
        class MySchema(ContractBase):
            name: str
            age: int
        assert "MySchema" in SchemaRegistry.list_schemas()

    def test_fields_extracted_correctly(self):
        class OrderSchema(ContractBase):
            order_id: str
            amount: float
        sv = SchemaRegistry.get_latest("OrderSchema")
        assert sv is not None
        assert sv.fields == {"order_id": str, "amount": float}

    def test_validate_method_attached(self):
        class PriceSchema(ContractBase):
            symbol: str
            price: float
        assert callable(PriceSchema.validate)

    def test_validate_passes_valid_data(self):
        class TickSchema(ContractBase):
            symbol: str
            bid: float
        assert TickSchema.validate({"symbol": "MSFT", "bid": 300.0}).is_valid

    def test_validate_fails_missing_field(self):
        class TickSchema2(ContractBase):
            symbol: str
            ask: float
        result = TickSchema2.validate({"symbol": "MSFT"})
        assert not result.is_valid
        assert any("ask" in e.message for e in result.errors)

    def test_version_defaults_to_1_0_0(self):
        class NoVersionSchema(ContractBase):
            x: int
        sv = SchemaRegistry.get_latest("NoVersionSchema")
        assert sv is not None and sv.version == "1.0.0"

    def test_explicit_version_used(self):
        class VersionedSchema(ContractBase):
            __version__ = "3.0.0"
            x: int
        sv = SchemaRegistry.get_latest("VersionedSchema")
        assert sv is not None and sv.version == "3.0.0"

    def test_private_fields_excluded(self):
        class PrivateSchema(ContractBase):
            symbol: str
            _internal: str = ""  # type: ignore
        sv = SchemaRegistry.get_latest("PrivateSchema")
        assert sv is not None
        assert "_internal" not in sv.fields
        assert "symbol" in sv.fields


class TestContractDecorator:
    def test_registers_schema(self):
        @contract("2.0.0")
        class DecoSchema:
            ticker: str
            close: float
        assert "DecoSchema" in SchemaRegistry.list_schemas()

    def test_without_parentheses(self):
        @contract
        class BareDecoSchema:
            val: int
        assert "BareDecoSchema" in SchemaRegistry.list_schemas()

    def test_validate_works(self):
        @contract("1.0.0")
        class FxSchema:
            pair: str
            rate: float
        assert FxSchema.validate({"pair": "GBPUSD", "rate": 1.27}).is_valid
