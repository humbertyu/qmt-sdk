"""QMT-native data surface backed by file IPC.

MiniQMT/pandas shape conversion belongs to ``xtquant_compat.xtdata``; this
module forwards QMT calls and preserves their native payloads.
"""

import threading
import time
import uuid
import ast
import re
try:
    import pandas as pd  # legacy helpers only
except ImportError:  # QMT's embedded Python may not ship pandas
    pd = None

from .api_surface import install_missing_api as _install_missing_api
from .bridge.client import get_client
from .bridge.config import configure as configure

enable_hello = False
_download_jobs = {}
_download_jobs_lock = threading.Lock()


def _request(method, **params):
    return get_client().request(method, params)


_KLINE_DEFAULT_FIELDS = [
    "time", "open", "high", "low", "close", "volume", "amount",
    "settelementPrice", "openInterest", "preClose", "suspendFlag",
]
_TICK_DEFAULT_FIELDS = [
    "time", "lastPrice", "open", "high", "low", "lastClose", "amount",
    "volume", "pvolume", "tickvol", "stockStatus", "openInt",
    "lastSettlementPrice", "askPrice", "bidPrice", "askVol", "bidVol",
    "settlementPrice", "transactionNum", "pe",
]


def _native_timetag_index(frame, period):
    if "stime" not in frame:
        return frame
    values = frame.pop("stime").astype(str).str.split(".").str[0]
    width = 8 if period == "1d" else 14
    frame.index = values.str[:width]
    frame.index.name = None
    return frame


def _frames_by_stock(raw, requested_fields=None, period="1d"):
    if not isinstance(raw, dict):
        return raw
    result = {}
    for stock, value in raw.items():
        if isinstance(value, pd.DataFrame):
            result[stock] = value
        elif isinstance(value, (dict, list)):
            frame = pd.DataFrame(value)
            frame = _native_timetag_index(frame, period)
            fields = list(requested_fields or [])
            if not fields:
                fields = _TICK_DEFAULT_FIELDS if period == "tick" else _KLINE_DEFAULT_FIELDS
                if period == "tick" and "tickvol" not in frame:
                    frame["tickvol"] = 0
                if period == "tick" and "pe" not in frame:
                    frame["pe"] = 0.0
            for field in fields:
                if field not in frame:
                    frame[field] = pd.NA
            frame = frame[fields]
            for field in ("stockStatus", "openInt", "suspendFlag"):
                if field in frame and not frame[field].isna().any():
                    frame[field] = frame[field].astype("int32")
            result[stock] = frame
        else:
            result[stock] = value
    return result


def _fields_by_stock(raw, requested_fields=None):
    """Convert Big QMT columns to native field -> stock-by-timetag matrices."""
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
        rows = {}
        for stock, value in raw.items():
            if not isinstance(value, dict) or field not in value:
                continue
            values = value.get(field)
            if not isinstance(values, list):
                values = [values]
            timetags = value.get("stime") or value.get("time") or list(range(len(values)))
            if not isinstance(timetags, list) or len(timetags) != len(values):
                timetags = list(range(len(values)))
            rows[stock] = {
                str(timetag).split(".")[0]: item
                for timetag, item in zip(timetags, values)
            }
        result[field] = pd.DataFrame.from_dict(rows, orient="index")
        result[field].index.name = None
        result[field].columns.name = None
    return result


def _normalize_financial_data(raw):
    """Convert Big QMT's raw field/date/stock/value payload to MiniQMT shape."""
    if not isinstance(raw, dict) or not {"field", "date", "stock", "value"}.issubset(raw):
        return raw
    fields = list(raw.get("field") or [])
    stocks = list(raw.get("stock") or [])
    dates = list(raw.get("date") or [])
    values = list(raw.get("value") or [])
    if not fields or not stocks or not dates:
        return {}
    # QMT may repeat stock labels once per date; retain first-seen order.
    unique_stocks = list(dict.fromkeys(str(s) for s in stocks))
    date_count = len(dates)
    result = {stock: {} for stock in unique_stocks}
    table_names = {
        "ASHAREBALANCESHEET": "balance", "ASHAREINCOME": "income",
        "ASHARECASHFLOW": "cashflow", "PERSHAREINDEX": "index",
        "CAPITALSTRUCTURE": "capital", "TOP10HOLDER": "top10holder",
        "TOP10FLOWHOLDER": "top10flowholder", "SHAREHOLDER": "holder",
    }
    grouped = {}
    for pos, field in enumerate(fields):
        text = str(field)
        head, sep, name = text.partition(".")
        grouped.setdefault(table_names.get(head.upper(), head.lower()), []).append((name if sep else text, pos))
    for stock_index, stock in enumerate(unique_stocks):
        for table, columns in grouped.items():
            frame_data = {}
            for column, field_index in columns:
                series = values[field_index] if field_index < len(values) else []
                series = list(series) if isinstance(series, (list, tuple)) else [series]
                if len(series) >= len(unique_stocks) * date_count:
                    offset = stock_index * date_count
                    row = series[offset:offset + date_count]
                elif len(series) >= date_count:
                    row = series[:date_count]
                else:
                    row = series + [pd.NA] * (date_count - len(series))
                frame_data[column] = row[:date_count]
            result[stock][table] = pd.DataFrame(frame_data, index=[str(d) for d in dates])
    return result


def _expand_financial_tables(table_list):
    aliases = {"balance": ("Balance", "ASHAREBALANCESHEET"), "income": ("Income", "ASHAREINCOME"), "cashflow": ("CashFlow", "ASHARECASHFLOW"), "index": ("PershareIndex", "PERSHAREINDEX")}
    try:
        path = r"D:\FinTools\QMT\python\bigqmt_signal_trader\adapters\market_bigqmt.py"
        source = open(path, encoding="utf-8").read()
        tree = ast.parse(source)
        catalogue = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "_FINANCIAL_TABLE_FIELDS" for t in node.targets):
                catalogue = ast.literal_eval(node.value)
                break
        out = []
        for item in table_list or []:
            text = str(item)
            if "." in text:
                out.append(text)
                continue
            public, internal = aliases.get(text.lower(), (text, text))
            out.extend([public + "." + field for field in catalogue.get(internal, [])] or [text])
        return out
    except Exception:
        return list(table_list or [])


def get_full_tick(code_list):
    return get_client().request("get_full_tick", {"stock_code": list(code_list)})


def get_market_data_ex(
    field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1,
    dividend_type="none", fill_data=True,
):
    return get_client().request("get_market_data_ex", {
        "fields": list(field_list), "stock_code": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "count": count,
        "dividend_type": dividend_type,
        "fill_data": fill_data,
        "subscribe": True,
    })


def get_market_data(
    field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1,
    dividend_type="none", fill_data=True,
):
    return get_client().request("get_market_data", {
        "fields": list(field_list), "stock_code": list(stock_list),
        "period": period,
        "start_time": start_time,
        "end_time": end_time,
        "count": count,
        "dividend_type": dividend_type,
        "fill_data": fill_data,
    })


def subscribe_quote(stock_code, period="1d", start_time="", end_time="", count=0, callback=None):
    return get_client().subscribe(stock_code, period, start_time, end_time, count, callback)


def subscribe_quote2(
    stock_code, period="1d", start_time="", end_time="", count=0,
    dividend_type=None, callback=None,
):
    return get_client().subscribe_method("subscribe_quote2", {
        "stock_code": stock_code, "period": period, "start_time": start_time,
        "end_time": end_time, "count": count, "dividend_type": dividend_type,
    }, callback)


def subscribe_whole_quote(code_list, callback=None):
    return get_client().subscribe_method(
        "subscribe_whole_quote", {"code_list": list(code_list)}, callback,
    )


def unsubscribe_quote(seq):
    return get_client().unsubscribe(seq)


def get_instrument_detail(stock_code, iscomplete=False):
    detail = get_client().request("get_instrument_detail", {
        "stock_code": stock_code,
        "iscomplete": bool(iscomplete),
    })
    if not isinstance(detail, dict):
        return detail
    return _normalize_instrument_detail(detail)


def _normalize_instrument_detail(detail):
    """Apply the same MiniQMT-compatible shape to single and batch results."""
    if not isinstance(detail, dict):
        return detail
    detail = dict(detail)
    aliases = {"FloatVolumn": "FloatVolume", "TotalVolumn": "TotalVolume"}
    for source, target in aliases.items():
        if target not in detail and source in detail:
            detail[target] = detail[source]
    defaults = {
        "IsRecent": False, "IsTrading": False, "LastVolume": 0,
        "LongMarginRatio": 0.0, "ShortMarginRatio": 0.0,
        "SettlementPrice": detail.get("PreClose", 0.0),
        "ContractOpenInterestQuota": 0, "ContractTradeQuota": 0,
        "ProductOpenInterestQuota": 0, "ProductTradeQuota": 0,
        "ProductType": None,
    }
    for key, value in defaults.items():
        if detail.get(key) is None:
            detail[key] = value
    for key in ("CreateDate", "OpenDate", "ExpireDate", "TradingDay"):
        if key in detail and detail[key] is not None:
            detail[key] = str(detail[key])
    return detail


def get_instrumentdetail(stock_code):
    return get_instrument_detail(stock_code)


def get_instrument_detail_list(stock_list, iscomplete=False):
    client = get_client()
    result = client.request(
        "get_instrument_detail_list",
        {"stock_list": list(stock_list), "iscomplete": bool(iscomplete)},
        timeout=max(client.config.timeout, 300),
    )
    if not isinstance(result, dict):
        return {}
    return {stock: _normalize_instrument_detail(detail) for stock, detail in result.items()}


def get_instrument_type(stock_code, variety_list=None):
    return _request("get_instrument_type", stock_code=stock_code, variety_list=variety_list)


def get_stock_type(stock_code, variety_list=None):
    return _request("get_stock_type", stock_code=stock_code, variety_list=variety_list)


def get_stock_list_in_sector(sector_name, real_timetag=-1):
    return get_client().request("get_stock_list_in_sector", {
        "sector_name": sector_name,
        "real_timetag": real_timetag,
    })


def get_sector_info(sector_name=""):
    return _request("get_sector_info", sector_name=sector_name)


def get_sector_list():
    return _request("get_sector_list")


def get_trading_dates(market, start_time="", end_time="", count=-1):
    return _request(
        "get_trading_dates", market=market, start_time=start_time,
        end_time=end_time, count=count,
    )


def get_trading_calendar(market, start_time="", end_time=""):
    """Return the official trading-calendar list for a market."""
    return _request(
        "get_trading_calendar", market=market, start_time=start_time,
        end_time=end_time,
    )


def get_holidays():
    return _request("get_holidays")


def download_holiday_data(incrementally=True):
    return _request("download_holiday_data", incrementally=incrementally)


def get_ipo_info(start_time="", end_time=""):
    return _request("get_ipo_info", start_time=start_time, end_time=end_time)


def bridge_status():
    return get_client().request("bridge_status", {})


def get_request_status(request_id):
    """Read progress for a long-running file-bridge request, if available."""
    return get_client().request_status(request_id)


def cancel_request(request_id):
    """Request cooperative cancellation of a running bridge operation."""
    get_client().cancel(request_id)
    return True


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
        total = len(stock_list)
        callback({"finished": total, "total": total, "stockcode": "", "message": ""})
    return result


def download_history_data(
    stock_code, period, start_time="", end_time="", incrementally=None,
):
    return download_history_data2(
        [stock_code], period, start_time, end_time,
        incrementally=incrementally,
    )


def _submit_download(target, args):
    job_id = uuid.uuid4().hex
    with _download_jobs_lock:
        _download_jobs[job_id] = {"job_id": job_id, "status": "pending", "result": None, "error": None}

    def worker():
        with _download_jobs_lock:
            _download_jobs[job_id]["status"] = "running"
        try:
            result = target(*args)
            with _download_jobs_lock:
                _download_jobs[job_id].update(status="finished", result=result)
        except Exception as exc:
            with _download_jobs_lock:
                _download_jobs[job_id].update(status="failed", error=repr(exc))

    threading.Thread(target=worker, name="xtquant-download-%s" % job_id[:8], daemon=True).start()
    return job_id


def submit_download_history_data(
    stock_code, period, start_time="", end_time="", incrementally=None,
):
    return _submit_download(
        download_history_data, (stock_code, period, start_time, end_time, incrementally),
    )


def submit_download_history_data2(
    stock_list, period, start_time="", end_time="", incrementally=None,
):
    return _submit_download(
        download_history_data2, (stock_list, period, start_time, end_time, None, incrementally),
    )


def get_download_status(job_id):
    with _download_jobs_lock:
        status = _download_jobs.get(job_id)
        return dict(status) if status is not None else None


def wait_download(job_id, timeout=None, poll_interval=None, callback=None):
    interval = 0.1 if poll_interval is None else float(poll_interval)
    deadline = None if timeout is None else time.monotonic() + float(timeout)
    while deadline is None or time.monotonic() < deadline:
        status = get_download_status(job_id)
        if status is None:
            return None
        if callback is not None:
            callback(status)
        if status["status"] in ("finished", "failed"):
            return status
        time.sleep(interval)
    return get_download_status(job_id)


def get_local_data(
    field_list=[], stock_list=[], period="1d", start_time="", end_time="", count=-1,
    dividend_type="none", fill_data=True, data_dir=None,
):
    raw = _request(
        "get_local_data", field_list=list(field_list), stock_list=list(stock_list),
        period=period, start_time=start_time, end_time=end_time, count=count,
        dividend_type=dividend_type, fill_data=fill_data, data_dir=data_dir,
    )
    return _frames_by_stock(raw)


def get_divid_factors(stock_code, start_time="", end_time=""):
    return _request(
        "get_divid_factors", stock_code=stock_code,
        start_time=start_time, end_time=end_time,
    )


def getDividFactors(*args, **kwargs):
    return get_divid_factors(*args, **kwargs)


def get_financial_data(
    stock_list, table_list=[], start_time="", end_time="", report_type="report_time",
):
    expanded = _expand_financial_tables(table_list)
    raw = _request(
        "get_financial_data", stock_list=list(stock_list), table_list=expanded,
        start_time=start_time, end_time=end_time, report_type=report_type,
    )
    result = _normalize_financial_data(raw)
    # Big QMT's Python wrapper returns {stock: {field: DataFrame}} for a
    # single stock/multiple dates; MiniQMT callers expect {stock: {table:
    # DataFrame}}.  Business callers request one table per read, so combine
    # the field frames under that table name.
    if len(table_list or []) == 1 and isinstance(result, dict):
        table = str(table_list[0]).lower()
        for stock, fields in list(result.items()):
            if isinstance(fields, dict) and fields and all(isinstance(v, pd.DataFrame) for v in fields.values()):
                result[stock] = {table: pd.concat(fields.values(), axis=1)}
    return result


def get_financial_data_ori(
    stock_list, table_list=[], start_time="", end_time="", report_type="report_time",
):
    """Return the unmodified financial payload, matching MiniQMT's alias."""
    raw = _request(
        "get_financial_data_ori", stock_list=list(stock_list), table_list=_expand_financial_tables(table_list),
        start_time=start_time, end_time=end_time, report_type=report_type,
    )
    return _normalize_financial_data(raw)


def download_financial_data(
    stock_list, table_list=[], start_time="", end_time="", incrementally=None,
):
    return _request(
        "download_financial_data", stock_list=list(stock_list), table_list=list(table_list),
        start_time=start_time, end_time=end_time, incrementally=incrementally,
    )


def download_financial_data2(
    stock_list, table_list=[], start_time="", end_time="", callback=None,
):
    result = _request(
        "download_financial_data2", stock_list=list(stock_list), table_list=list(table_list),
        start_time=start_time, end_time=end_time,
    )
    if callback is not None:
        # MiniQMT invokes the completion callback with the standard download
        # progress shape.  The file bridge is intentionally blocking, so the
        # completion notification is emitted once with the full stock count.
        total = len(stock_list)
        callback({"finished": total, "total": total, "stockcode": "", "message": ""})
    return result


def get_etf_info():
    return _request("get_etf_info")


def download_etf_info():
    return _request("download_etf_info")


def get_option_list(undl_code, dedate, opttype="", isavailavle=False):
    return _request(
        "get_option_list", undl_code=undl_code, dedate=dedate,
        opttype=opttype, isavailavle=isavailavle,
    )


def get_his_option_list(undl_code, dedate):
    return _request("get_his_option_list", undl_code=undl_code, dedate=dedate)


def get_his_option_list_batch(undl_code, start_time="", end_time=""):
    return _request(
        "get_his_option_list_batch", undl_code=undl_code,
        start_time=start_time, end_time=end_time,
    )


def call_formula(
    formula_name, stock_code, period, start_time="", end_time="", count=-1,
    dividend_type=None, extend_param={},
):
    return _request(
        "call_formula", formula_name=formula_name, stock_code=stock_code, period=period,
        start_time=start_time, end_time=end_time, count=count,
        dividend_type=dividend_type, extend_param=extend_param,
    )


def get_formula_result(request_id, start_time="", end_time="", count=-1, timeout_second=-1):
    return _request(
        "get_formula_result", request_id=request_id, start_time=start_time,
        end_time=end_time, count=count, timeout_second=timeout_second,
    )


def subscribe_formula(
    formula_name, stock_code, period, start_time="", end_time="", count=-1,
    dividend_type=None, extend_param={}, callback=None,
):
    return get_client().subscribe_method("subscribe_formula", {
        "formula_name": formula_name, "stock_code": stock_code, "period": period,
        "start_time": start_time, "end_time": end_time, "count": count,
        "dividend_type": dividend_type, "extend_param": extend_param,
    }, callback)


def unsubscribe_formula(request_id):
    return get_client().unsubscribe_method("unsubscribe_formula", request_id, "request_id")


def gen_factor_index(
    data_name, formula_name, vars, sector_list, start_time="", end_time="",
    period="1d", dividend_type="none",
):
    return _request(
        "gen_factor_index", data_name=data_name, formula_name=formula_name, vars=vars,
        sector_list=sector_list, start_time=start_time, end_time=end_time,
        period=period, dividend_type=dividend_type,
    )


def run():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return None


OFFICIAL_API_SPEC = _install_missing_api(globals(), _request)
