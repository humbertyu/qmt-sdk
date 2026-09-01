from xtquant_compat import xtdata


class StubClient:
    def __init__(self):
        self.calls = []

    def request(self, method, params, timeout=None):
        self.calls.append((method, params, timeout))
        if method == "get_stock_list_in_sector":
            return ["000001.SZ", "000002.SZ"]
        if method == "get_market_data":
            return {
                "000001.SZ": {"time": [1], "amount": [10.0]},
                "000002.SZ": {"time": [1], "amount": [20.0]},
            }
        if method == "download_history_data2":
            return {"000001.SZ": True}
        raise AssertionError(method)


def test_update_instruments_contract(monkeypatch):
    client = StubClient()
    monkeypatch.setattr(xtdata, "get_client", lambda: client)
    stocks = xtdata.get_stock_list_in_sector("沪深A股")
    amounts = xtdata.get_market_data(
        field_list=["amount"], stock_list=stocks, period="1d",
        start_time="20260901", end_time="20260901",
    )
    assert stocks == ["000001.SZ", "000002.SZ"]
    assert amounts["amount"].iloc[-1].to_dict() == {
        "000001.SZ": 10.0, "000002.SZ": 20.0,
    }


def test_sync_auto_download_contract(monkeypatch):
    client = StubClient()
    progress = []
    monkeypatch.setattr(xtdata, "get_client", lambda: client)
    result = xtdata.download_history_data2(
        ["000001.SZ"], period="tick", start_time="20260901", end_time="20260901",
        callback=progress.append,
    )
    assert result == {"000001.SZ": True}
    assert progress == [{"finished": 1, "result": result}]
    assert client.calls[-1][2] == 600
