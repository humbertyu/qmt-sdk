#coding:gbk
"""Pure-file Big QMT bridge. Keep this script compatible with Python 3.6."""
import json
import os
import time
import traceback
import uuid

ROOT = os.environ.get("XTQUANT_COMPAT_ROOT", r"D:\FinTools\QMT\xtquant_compat_bridge")
REQUESTS = os.path.join(ROOT, "requests")
PROCESSING = os.path.join(ROOT, "processing")
RESPONSES = os.path.join(ROOT, "responses")
ERRORS = os.path.join(ROOT, "errors")
CANCELLATIONS = os.path.join(ROOT, "cancellations")
STATUS = os.path.join(ROOT, "status")
EVENTS = os.path.join(ROOT, "events")
PROTOCOL_VERSION = 1

_scheduled = False
_last_scan = 0.0
_subscriptions = {}
_next_subscription_id = 1
_bridge_instance_id = uuid.uuid4().hex


def _mkdirs():
    for path in (REQUESTS, PROCESSING, RESPONSES, ERRORS, EVENTS, CANCELLATIONS, STATUS):
        if not os.path.isdir(path):
            os.makedirs(path)


def _jsonable(value, depth=0):
    if depth > 10:
        return repr(value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item, depth + 1) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item, depth + 1) for item in value]
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        try:
            return _jsonable(tolist(), depth + 1)
        except Exception:
            pass
    return repr(value)


def _atomic_write(path, payload):
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    temp = "%s.%s.tmp" % (path, uuid.uuid4().hex)
    with open(temp, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
        stream.flush()
    try:
        os.remove(path)
    except OSError:
        pass
    os.rename(temp, path)


def _unwrap_one(value):
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def _native_quote_shape(stock_code, raw):
    """Convert Big QMT column arrays into xtdata's {symbol: [tick]} callback."""
    raw = _jsonable(raw)
    if isinstance(raw, dict) and stock_code in raw:
        nested = raw.get(stock_code)
        if isinstance(nested, list):
            return {stock_code: nested}
        raw = nested
    if isinstance(raw, dict):
        tick = {key: _unwrap_one(value) for key, value in raw.items()}
        return {stock_code: [tick]}
    if isinstance(raw, list):
        return {stock_code: raw}
    return {stock_code: [raw]}


def _raw_context(ContextInfo):
    return getattr(ContextInfo, "context", None)


def _call_available(ContextInfo, names, args):
    if isinstance(names, str):
        names = (names,)
    objects = (_raw_context(ContextInfo), ContextInfo)
    for name in names:
        injected = globals().get(name)
        if callable(injected):
            return injected(*args)
        for obj in objects:
            function = getattr(obj, name, None) if obj is not None else None
            if callable(function):
                return function(*args)
    raise NotImplementedError("QMT callable unavailable: %s" % ", ".join(names))


def _call_shapes(ContextInfo, names, shapes):
    last_error = None
    for args in shapes:
        try:
            return _call_available(ContextInfo, names, args)
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise NotImplementedError("no call shapes for %s" % names)


def _get_market_data(ContextInfo, params):
    fields = params.get("field_list", [])
    stocks = params.get("stock_list", [])
    context = _raw_context(ContextInfo)
    if context is not None and hasattr(context, "get_market_data2"):
        return context.get_market_data2(
            fields, stocks, params.get("period", "1d"),
            params.get("start_time", ""), params.get("end_time", ""),
            params.get("count", -1), params.get("dividend_type", "none"),
            params.get("fill_data", True), False,
        )
    raise NotImplementedError("ContextInfo.context.get_market_data2 unavailable")


def _subscribe(ContextInfo, request, params):
    global _next_subscription_id
    stock = str(params.get("stock_code", "")).upper()
    period = params.get("period", "1d")
    client_id = request.get("client_id") or "anonymous"
    context = _raw_context(ContextInfo)
    subscribe = getattr(context, "subscribe_quote", None) if context is not None else None
    if not callable(subscribe):
        raise NotImplementedError("ContextInfo.context.subscribe_quote unavailable")
    subscription_id = _next_subscription_id
    _next_subscription_id += 1
    state = {
        "client_id": client_id, "stock_code": stock, "sequence": 0,
        "qmt_sequence": None, "callback": None,
    }

    def on_quote(raw):
        state["sequence"] += 1
        sequence = state["sequence"]
        filename = "%020d.json" % sequence
        path = os.path.join(EVENTS, client_id, str(subscription_id), filename)
        event = {
            "protocol_version": PROTOCOL_VERSION,
            "bridge_instance_id": _bridge_instance_id,
            "subscription_id": subscription_id,
            "sequence": sequence,
            "created_at": time.time(),
            "data": _native_quote_shape(stock, raw),
        }
        _atomic_write(path, event)

    qmt_sequence = subscribe(stock, period, params.get("start_time", ""), on_quote)
    state["qmt_sequence"] = qmt_sequence
    state["callback"] = on_quote
    _subscriptions[subscription_id] = state
    return {"subscription_id": subscription_id, "qmt_sequence": qmt_sequence}


def _unsubscribe(ContextInfo, params):
    subscription_id = int(params.get("subscription_id"))
    state = _subscriptions.pop(subscription_id, None)
    if state is None:
        return False
    context = _raw_context(ContextInfo)
    unsubscribe = getattr(context, "unsubscribe_quote", None) if context is not None else None
    if callable(unsubscribe):
        unsubscribe(state.get("qmt_sequence"))
    return True


def _subscribe_whole(ContextInfo, request, params):
    global _next_subscription_id
    client_id = request.get("client_id") or "anonymous"
    code_list = params.get("code_list", [])
    subscription_id = _next_subscription_id
    _next_subscription_id += 1
    state = {
        "client_id": client_id, "stock_code": "*", "sequence": 0,
        "qmt_sequence": None, "callback": None,
    }

    def on_quote(raw):
        state["sequence"] += 1
        sequence = state["sequence"]
        path = os.path.join(
            EVENTS, client_id, str(subscription_id), "%020d.json" % sequence,
        )
        _atomic_write(path, {
            "protocol_version": PROTOCOL_VERSION,
            "bridge_instance_id": _bridge_instance_id,
            "subscription_id": subscription_id,
            "sequence": sequence,
            "created_at": time.time(),
            "data": _jsonable(raw),
        })

    qmt_sequence = _call_available(
        ContextInfo, "subscribe_whole_quote", (code_list, on_quote),
    )
    state["qmt_sequence"] = qmt_sequence
    state["callback"] = on_quote
    _subscriptions[subscription_id] = state
    return {"subscription_id": subscription_id, "qmt_sequence": qmt_sequence}


def _subscribe_formula(ContextInfo, request, params):
    global _next_subscription_id
    client_id = request.get("client_id") or "anonymous"
    subscription_id = _next_subscription_id
    _next_subscription_id += 1
    state = {
        "client_id": client_id, "stock_code": params.get("stock_code", ""),
        "sequence": 0, "qmt_sequence": None, "callback": None,
    }

    def on_formula(raw):
        state["sequence"] += 1
        sequence = state["sequence"]
        path = os.path.join(
            EVENTS, client_id, str(subscription_id), "%020d.json" % sequence,
        )
        _atomic_write(path, {
            "protocol_version": PROTOCOL_VERSION,
            "bridge_instance_id": _bridge_instance_id,
            "subscription_id": subscription_id,
            "sequence": sequence,
            "created_at": time.time(),
            "data": _jsonable(raw),
        })

    args = (
        params.get("formula_name"), params.get("stock_code"), params.get("period"),
        params.get("start_time", ""), params.get("end_time", ""),
        params.get("count", -1), params.get("dividend_type"),
        params.get("extend_param", {}), on_formula,
    )
    qmt_sequence = _call_available(ContextInfo, "subscribe_formula", args)
    state["qmt_sequence"] = qmt_sequence
    state["callback"] = on_formula
    _subscriptions[subscription_id] = state
    return {"subscription_id": subscription_id, "qmt_sequence": qmt_sequence}


def _write_status(request_id, state, processed=0, total=0, failed=0, error=None):
    if not request_id:
        return
    existing = {}
    path = os.path.join(STATUS, str(request_id) + ".json")
    try:
        with open(path, "r", encoding="utf-8") as stream:
            existing = json.load(stream)
    except Exception:
        pass
    payload = {"request_id": request_id, "bridge_instance_id": _bridge_instance_id,
               "state": state, "processed": processed, "total": total,
               "failed": failed, "updated_at": time.time()}
    if total == 0 and existing:
        payload["processed"] = existing.get("processed", processed)
        payload["total"] = existing.get("total", total)
    if error:
        payload["error"] = error
    _atomic_write(os.path.join(STATUS, str(request_id) + ".json"), payload)


def _download_history(params, request_id=None):
    download = globals().get("down_history_data")
    if not callable(download):
        raise NotImplementedError("QMT global down_history_data unavailable")
    results = {}
    stocks = params.get("stock_list", [])
    for index, stock in enumerate(stocks, 1):
        if _cancelled(request_id):
            raise RuntimeError("request cancelled")
        _write_status(request_id, "running", index - 1, len(stocks))
        results[stock] = download(
            stock, params.get("period", "1d"),
            params.get("start_time", ""), params.get("end_time", ""),
        )
    return results


def _cancelled(request_id):
    path = os.path.join(CANCELLATIONS, str(request_id) + ".json")
    if not os.path.exists(path):
        return False
    try:
        os.remove(path)
    except OSError:
        pass
    return True


def _instrument_detail_list(ContextInfo, request):
    params = request.get("params") or {}
    result = {}
    stocks = params.get("stock_list", [])
    _write_status(request.get("request_id"), "running", 0, len(stocks))
    for index, stock in enumerate(stocks, 1):
        if _cancelled(request.get("request_id")):
            raise RuntimeError("request cancelled")
        result[stock] = ContextInfo.get_instrument_detail(stock)
        _write_status(request.get("request_id"), "running", index, len(stocks))
    return result


def _handle(ContextInfo, request):
    method = request.get("method")
    params = request.get("params") or {}
    if method == "bridge_status":
        return {
            "protocol_version": PROTOCOL_VERSION,
            "bridge_instance_id": _bridge_instance_id,
            "subscriptions": len(_subscriptions),
            "time": time.time(),
        }
    if method == "get_full_tick":
        return ContextInfo.get_full_tick(params.get("stock_list", []))
    if method == "get_market_data_ex":
        return _get_market_data(ContextInfo, params)
    if method == "get_market_data":
        return _get_market_data(ContextInfo, params)
    if method == "get_instrument_detail":
        return ContextInfo.get_instrument_detail(params.get("stock_code", ""))
    if method == "get_instrument_detail_list":
        return _instrument_detail_list(ContextInfo, request)
    if method == "get_stock_list_in_sector":
        get_sector = getattr(ContextInfo, "get_stock_list_in_sector", None)
        if not callable(get_sector):
            context = _raw_context(ContextInfo)
            get_sector = getattr(context, "get_stock_list_in_sector", None) if context is not None else None
        if not callable(get_sector):
            raise NotImplementedError("get_stock_list_in_sector unavailable")
        return get_sector(params.get("sector_name", ""))
    if method == "get_sector_list":
        return _call_shapes(ContextInfo, "get_sector_list", ((), ("",)))
    if method == "get_trading_dates":
        base = (
            params.get("market"), params.get("start_time", ""),
            params.get("end_time", ""), params.get("count", -1),
        )
        return _call_shapes(ContextInfo, "get_trading_dates", (base, base + ("",)))
    if method == "get_divid_factors":
        stock = params.get("stock_code")
        date = params.get("end_time", "") or params.get("start_time", "")
        return _call_shapes(
            ContextInfo, ("get_divid_factors", "getDividFactors"),
            ((stock, params.get("start_time", ""), params.get("end_time", "")),
             (stock, date), (stock,)),
        )
    if method == "get_etf_info":
        return _call_shapes(ContextInfo, "get_etf_info", ((), ("",)))
    if method == "get_stock_type":
        stock = params.get("stock_code")
        variety = params.get("variety_list")
        return _call_shapes(ContextInfo, "get_stock_type", ((stock, variety), (stock,)))
    if method == "subscribe_quote":
        return _subscribe(ContextInfo, request, params)
    if method == "subscribe_quote2":
        return _subscribe(ContextInfo, request, params)
    if method == "subscribe_whole_quote":
        return _subscribe_whole(ContextInfo, request, params)
    if method == "unsubscribe_quote":
        return _unsubscribe(ContextInfo, params)
    if method == "subscribe_formula":
        return _subscribe_formula(ContextInfo, request, params)
    if method == "unsubscribe_formula":
        formula_id = params.get("request_id")
        state = _subscriptions.pop(int(formula_id), None)
        qmt_id = state.get("qmt_sequence") if state else formula_id
        return _call_available(ContextInfo, "unsubscribe_formula", (qmt_id,))
    if method == "download_history_data2":
        return _download_history(params, request.get("request_id"))
    if method == "get_local_data":
        return _get_market_data(ContextInfo, params)

    simple_calls = {
        "get_instrument_type": (("get_instrument_type",), (params.get("stock_code"), params.get("variety_list"))),
        "get_stock_type": (("get_stock_type",), (params.get("stock_code"), params.get("variety_list"))),
        "get_sector_info": (("get_sector_info",), (params.get("sector_name", ""),)),
        "get_sector_list": (("get_sector_list",), ()),
        "get_trading_dates": (("get_trading_dates",), (params.get("market"), params.get("start_time", ""), params.get("end_time", ""), params.get("count", -1))),
        "get_holidays": (("get_holidays",), ()),
        "download_holiday_data": (("download_holiday_data",), (params.get("incrementally", True),)),
        "get_ipo_info": (("get_ipo_info",), (params.get("start_time", ""), params.get("end_time", ""))),
        "get_divid_factors": (("get_divid_factors", "getDividFactors"), (params.get("stock_code"), params.get("start_time", ""), params.get("end_time", ""))),
        "get_financial_data": (("get_financial_data",), (params.get("stock_list", []), params.get("table_list", []), params.get("start_time", ""), params.get("end_time", ""), params.get("report_type", "report_time"))),
        "download_financial_data": (("download_financial_data",), (params.get("stock_list", []), params.get("table_list", []), params.get("start_time", ""), params.get("end_time", ""), params.get("incrementally"))),
        "download_financial_data2": (("download_financial_data2", "download_financial_data"), (params.get("stock_list", []), params.get("table_list", []), params.get("start_time", ""), params.get("end_time", ""))),
        "get_etf_info": (("get_etf_info",), ()),
        "download_etf_info": (("download_etf_info",), ()),
        "get_option_list": (("get_option_list",), (params.get("undl_code"), params.get("dedate"), params.get("opttype", ""), params.get("isavailavle", False))),
        "get_his_option_list": (("get_his_option_list",), (params.get("undl_code"), params.get("dedate"))),
        "get_his_option_list_batch": (("get_his_option_list_batch",), (params.get("undl_code"), params.get("start_time", ""), params.get("end_time", ""))),
        "call_formula": (("call_formula",), (params.get("formula_name"), params.get("stock_code"), params.get("period"), params.get("start_time", ""), params.get("end_time", ""), params.get("count", -1), params.get("dividend_type"), params.get("extend_param", {}))),
        "get_formula_result": (("get_formula_result",), (params.get("request_id"), params.get("start_time", ""), params.get("end_time", ""), params.get("count", -1), params.get("timeout_second", -1))),
        "gen_factor_index": (("gen_factor_index",), (params.get("data_name"), params.get("formula_name"), params.get("vars"), params.get("sector_list"), params.get("start_time", ""), params.get("end_time", ""), params.get("period", "1d"), params.get("dividend_type", "none"))),
    }
    if method in simple_calls:
        names, args = simple_calls[method]
        return _call_available(ContextInfo, names, args)
    # Generic fallback for the remaining official API surface. The external
    # adapter serializes parameters in signature order, and Python 3.6 keeps
    # JSON object insertion order. Availability still depends on this QMT build.
    return _call_available(ContextInfo, method, tuple(params.values()))


def _process_one(ContextInfo, name):
    source = os.path.join(REQUESTS, name)
    processing = os.path.join(PROCESSING, name)
    try:
        os.rename(source, processing)
    except OSError:
        return
    request = None
    try:
        with open(processing, "r", encoding="utf-8") as stream:
            request = json.load(stream)
        _write_status(request.get("request_id"), "running", 0, 0)
        data = _jsonable(_handle(ContextInfo, request))
        result = {"request_id": request.get("request_id"), "ok": True, "data": data}
        _atomic_write(os.path.join(RESPONSES, name), result)
        _write_status(request.get("request_id"), "finished", 1, 1)
    except Exception as exc:
        result = {
            "request_id": request.get("request_id") if request else "",
            "ok": False, "error": repr(exc), "traceback": traceback.format_exc(),
        }
        _atomic_write(os.path.join(ERRORS, name), result)
        _write_status(request.get("request_id"), "cancelled" if "cancel" in str(exc).lower() else "failed", 0, 0, error=repr(exc))
    try:
        os.remove(processing)
    except OSError:
        pass


def init(ContextInfo):
    global _scheduled
    _mkdirs()
    print("[xtquant_compat] started root=%s instance=%s" % (ROOT, _bridge_instance_id))
    if not _scheduled and hasattr(ContextInfo, "run_time"):
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 1))
        try:
            ContextInfo.run_time("adjust", "100nMilliSecond", start)
            _scheduled = True
            print("[xtquant_compat] scheduled adjust interval=100nMilliSecond")
        except Exception as exc:
            print("[xtquant_compat] 100ms schedule failed: %s" % exc)
            ContextInfo.run_time("adjust", "500nMilliSecond", start)
            _scheduled = True
            print("[xtquant_compat] scheduled adjust interval=500nMilliSecond")


def adjust(ContextInfo):
    global _last_scan
    now = time.time()
    if now - _last_scan < 0.05:
        return
    _last_scan = now
    _mkdirs()
    names = [name for name in os.listdir(REQUESTS) if name.endswith(".json")]
    for name in sorted(names)[:50]:
        _process_one(ContextInfo, name)


def handlebar(ContextInfo):
    adjust(ContextInfo)
