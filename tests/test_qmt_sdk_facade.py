import sys

sys.path.insert(0, "src")

from qmt_sdk import QmtClient


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def call(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))
        return method


def test_domain_clients_share_one_backend():
    backend = RecordingBackend()
    client = QmtClient(backend=backend)
    assert client.market.get_full_tick(["000001.SZ"]) == "get_full_tick"
    assert client.financial.get(["000001.SZ"], ["balance"]) == "get_financial_data"
    assert client.instruments.get("000001.SZ") == "get_instrument_detail"
    assert client.jobs.bridge_status() == "bridge_status"
    assert [call[0] for call in backend.calls] == [
        "get_full_tick", "get_financial_data", "get_instrument_detail", "bridge_status",
    ]

