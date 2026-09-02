import importlib.util
import json
import pickle
from pathlib import Path


BRIDGE_PATH = Path(__file__).parents[1] / "qmt_strategy" / "XTQUANT_COMPAT_BRIDGE.py"


class FakeRawContext:
    def __init__(self):
        self.quote_callback = None
        self.unsubscribed = None

    def get_market_data2(self, *args):
        return {"000001.SZ": {"time": [1], "close": [10.0]}}

    def subscribe_quote(self, stock, period, start_time, callback):
        self.quote_callback = callback
        return 88

    def unsubscribe_quote(self, sequence):
        self.unsubscribed = sequence
        return True

    def get_sector_list(self):
        return ["沪深A股"]


class FakeContextInfo:
    def __init__(self):
        self.context = FakeRawContext()

    def get_full_tick(self, stocks):
        return {stocks[0]: {"time": 1}}


def load_bridge(monkeypatch, tmp_path):
    monkeypatch.setenv("XTQUANT_COMPAT_ROOT", str(tmp_path))
    spec = importlib.util.spec_from_file_location("test_xtquant_compat_qmt_bridge", BRIDGE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._mkdirs()
    return module


def test_generic_context_dispatch(monkeypatch, tmp_path):
    bridge = load_bridge(monkeypatch, tmp_path)
    context = FakeContextInfo()
    result = bridge._handle(context, {
        "method": "get_sector_list", "params": {}, "client_id": "test-client",
    })
    assert result == ["沪深A股"]


def test_large_market_result_pickle_round_trip(monkeypatch, tmp_path):
    bridge = load_bridge(monkeypatch, tmp_path)
    target = tmp_path / "responses" / "market.pkl"
    payload = {"000001.SZ": {"time": [1, 2], "close": [10.0, 10.1]}}
    bridge._atomic_write_pickle(str(target), payload)
    with target.open("rb") as stream:
        assert pickle.load(stream) == payload


def test_quote_subscription_writes_native_callback_event(monkeypatch, tmp_path):
    bridge = load_bridge(monkeypatch, tmp_path)
    context = FakeContextInfo()
    result = bridge._handle(context, {
        "method": "subscribe_quote", "client_id": "test-client",
        "params": {"stock_code": "000001.SZ", "period": "tick"},
    })
    assert result["qmt_sequence"] == 88
    context.context.quote_callback({"time": [123], "lastPrice": [10.1]})
    event_path = next((tmp_path / "events" / "test-client" / "1").glob("*.json"))
    event = json.loads(event_path.read_text(encoding="utf-8"))
    assert event["data"] == {
        "000001.SZ": [{"time": 123, "lastPrice": 10.1}],
    }
    assert bridge._handle(context, {
        "method": "unsubscribe_quote", "params": {"subscription_id": 1},
    }) is None
    assert context.context.unsubscribed == 88
