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
    assert amounts["amount"].iloc[:, -1].to_dict() == {
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
    assert result == {}
    assert progress == [{"finished": 1, "total": 1, "stockcode": "", "message": ""}]
    assert client.calls[-1][2] == 600


def test_async_download_job_lifecycle(monkeypatch):
    monkeypatch.setattr(xtdata, "download_history_data", lambda *args: {"ok": True})
    job_id = xtdata.submit_download_history_data("000001.SZ", "1d")
    status = xtdata.wait_download(job_id, timeout=2, poll_interval=0.01)
    assert status["status"] == "finished"
    assert status["result"] == {"ok": True}
