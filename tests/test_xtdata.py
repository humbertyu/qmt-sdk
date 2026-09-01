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
