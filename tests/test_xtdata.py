import pandas as pd

from xtquant_compat import xtdata


def test_frames_by_stock_converts_column_dict():
    result = xtdata._frames_by_stock({
        "000779.SZ": {
            "time": [1, 2], "stime": ["20260901100000.000", "20260901100003.000"],
            "lastPrice": [9.9, 10.0], "ignored": [1, 2],
        },
    }, ["time", "lastPrice"], "tick")
    assert isinstance(result["000779.SZ"], pd.DataFrame)
    assert result["000779.SZ"].index.tolist() == ["20260901100000", "20260901100003"]
    assert result["000779.SZ"].columns.tolist() == ["time", "lastPrice"]
    assert result["000779.SZ"].to_dict("records") == [
        {"time": 1, "lastPrice": 9.9},
        {"time": 2, "lastPrice": 10.0},
    ]


def test_default_tick_frame_matches_native_columns_with_documented_placeholders():
    result = xtdata._frames_by_stock({
        "000779.SZ": {
            "time": [1], "stime": ["20260901100000.000"],
            "lastPrice": [10.0], "stockStatus": [0], "openInt": [1],
        },
    }, [], "tick")["000779.SZ"]
    assert result.columns.tolist() == xtdata._TICK_DEFAULT_FIELDS
    assert result.at["20260901100000", "tickvol"] == 0
    assert result.at["20260901100000", "pe"] == 0.0
    assert str(result["stockStatus"].dtype) == "int32"


def test_fields_by_stock_matches_native_get_market_data_orientation():
    result = xtdata._fields_by_stock({
        "000001.SZ": {"time": [100, 200], "amount": [10.0, 20.0]},
        "000002.SZ": {"time": [100, 200], "amount": [30.0, 40.0]},
    }, ["amount"])
    assert list(result) == ["amount"]
    assert result["amount"].to_dict("index") == {
        "000001.SZ": {"100": 10.0, "200": 20.0},
        "000002.SZ": {"100": 30.0, "200": 40.0},
    }


def test_instrument_detail_normalizes_big_qmt_aliases_and_defaults(monkeypatch):
    class StubClient:
        def request(self, method, params):
            assert method == "get_instrument_detail"
            return {
                "FloatVolumn": 123, "TotalVolumn": 456, "PreClose": 10.0,
                "OpenDate": 20200101, "SettlementPrice": None,
            }

    monkeypatch.setattr(xtdata, "get_client", lambda: StubClient())
    detail = xtdata.get_instrument_detail("000001.SZ")
    assert detail["FloatVolume"] == 123
    assert detail["TotalVolume"] == 456
    assert detail["SettlementPrice"] == 10.0
    assert detail["OpenDate"] == "20200101"
