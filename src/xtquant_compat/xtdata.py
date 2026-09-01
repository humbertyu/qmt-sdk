"""A focused subset of the public ``xtquant.xtdata`` API."""

import pandas as pd

from .client import get_client
from .config import configure as configure

enable_hello = False


def _frames_by_stock(raw):
    if not isinstance(raw, dict):
        return raw
    result = {}
    for stock, value in raw.items():
        if isinstance(value, pd.DataFrame):
            result[stock] = value
        elif isinstance(value, dict):
            result[stock] = pd.DataFrame(value)
        elif isinstance(value, list):
            result[stock] = pd.DataFrame(value)
        else:
            result[stock] = value
    return result


def get_full_tick(code_list):
    return get_client().request("get_full_tick", {"stock_list": list(code_list)})


def get_market_data_ex(
    field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1,
    dividend_type="none", fill_data=True,
):
    raw = get_client().request("get_market_data_ex", {
        "field_list": list(field_list),
        "stock_list": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "count": count,
        "dividend_type": dividend_type,
        "fill_data": fill_data,
    })
    return _frames_by_stock(raw)


def subscribe_quote(stock_code, period="1d", start_time="", end_time="", count=0, callback=None):
    return get_client().subscribe(stock_code, period, start_time, end_time, count, callback)


def unsubscribe_quote(seq):
    return get_client().unsubscribe(seq)


def get_instrument_detail(stock_code, iscomplete=False):
    return get_client().request("get_instrument_detail", {
        "stock_code": stock_code,
        "iscomplete": bool(iscomplete),
    })


def bridge_status():
    return get_client().request("bridge_status", {})


def download_history_data2(
    stock_list, period, start_time="", end_time="", callback=None, incrementally=None,
):
    result = get_client().request("download_history_data2", {
        "stock_list": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "incrementally": incrementally,
    })
    if callback is not None:
        callback({"finished": 1, "result": result})
    return result


def download_history_data(stock_code, period, start_time="", end_time="", callback=None):
    return download_history_data2([stock_code], period, start_time, end_time, callback=callback)
