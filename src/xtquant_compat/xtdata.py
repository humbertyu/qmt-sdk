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


def _fields_by_stock(raw, requested_fields=None):
    """Convert Big QMT's stock-first columns to xtdata's field-first DataFrames."""
    if not isinstance(raw, dict):
        return raw
    requested = list(requested_fields or [])
    if not requested:
        field_names = set()
        for value in raw.values():
            if isinstance(value, dict):
                field_names.update(value)
        requested = sorted(field_names - {"time", "stime"})
    result = {}
    for field in requested:
        columns = {}
        for stock, value in raw.items():
            if not isinstance(value, dict) or field not in value:
                continue
            values = value.get(field)
            if not isinstance(values, list):
                values = [values]
            index = value.get("time") or value.get("stime") or list(range(len(values)))
            if not isinstance(index, list) or len(index) != len(values):
                index = list(range(len(values)))
            columns[stock] = pd.Series(values, index=index)
        result[field] = pd.DataFrame(columns)
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


def get_market_data(
    field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1,
    dividend_type="none", fill_data=True,
):
    raw = get_client().request("get_market_data", {
        "field_list": list(field_list),
        "stock_list": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "count": count,
        "dividend_type": dividend_type,
        "fill_data": fill_data,
    })
    return _fields_by_stock(raw, field_list)


def subscribe_quote(stock_code, period="1d", start_time="", end_time="", count=0, callback=None):
    return get_client().subscribe(stock_code, period, start_time, end_time, count, callback)


def unsubscribe_quote(seq):
    return get_client().unsubscribe(seq)


def get_instrument_detail(stock_code, iscomplete=False):
    return get_client().request("get_instrument_detail", {
        "stock_code": stock_code,
        "iscomplete": bool(iscomplete),
    })


def get_stock_list_in_sector(sector_name, real_timetag=-1):
    return get_client().request("get_stock_list_in_sector", {
        "sector_name": sector_name,
        "real_timetag": real_timetag,
    })


def bridge_status():
    return get_client().request("bridge_status", {})


def download_history_data2(
    stock_list, period, start_time="", end_time="", callback=None, incrementally=None,
):
    # Full-market batches can legitimately take longer than an ordinary query.
    result = get_client().request("download_history_data2", {
        "stock_list": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "incrementally": incrementally,
    }, timeout=600)
    if callback is not None:
        callback({"finished": 1, "result": result})
    return result


def download_history_data(stock_code, period, start_time="", end_time="", callback=None):
    return download_history_data2([stock_code], period, start_time, end_time, callback=callback)
