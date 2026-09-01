import pandas as pd

from xtquant_compat import xtdata


def test_frames_by_stock_converts_column_dict():
    result = xtdata._frames_by_stock({
        "000779.SZ": {"time": [1, 2], "lastPrice": [9.9, 10.0]},
    })
    assert isinstance(result["000779.SZ"], pd.DataFrame)
    assert result["000779.SZ"].to_dict("records") == [
        {"time": 1, "lastPrice": 9.9},
        {"time": 2, "lastPrice": 10.0},
    ]


def test_fields_by_stock_matches_get_market_data_shape():
    result = xtdata._fields_by_stock({
        "000001.SZ": {"time": [100, 200], "amount": [10.0, 20.0]},
        "000002.SZ": {"time": [100, 200], "amount": [30.0, 40.0]},
    }, ["amount"])
    assert list(result) == ["amount"]
    assert result["amount"].iloc[-1].to_dict() == {
        "000001.SZ": 20.0,
        "000002.SZ": 40.0,
    }
