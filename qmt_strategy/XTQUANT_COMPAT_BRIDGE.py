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
EVENTS = os.path.join(ROOT, "events")
PROTOCOL_VERSION = 1

_scheduled = False
_last_scan = 0.0
_subscriptions = {}
_next_subscription_id = 1
_bridge_instance_id = uuid.uuid4().hex


def _mkdirs():
    for path in (REQUESTS, PROCESSING, RESPONSES, ERRORS, EVENTS):
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


def _download_history(params):
    download = globals().get("down_history_data")
    if not callable(download):
        raise NotImplementedError("QMT global down_history_data unavailable")
    results = {}
    for stock in params.get("stock_list", []):
        results[stock] = download(
            stock, params.get("period", "1d"),
            params.get("start_time", ""), params.get("end_time", ""),
        )
    return results


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
    if method == "get_stock_list_in_sector":
        get_sector = getattr(ContextInfo, "get_stock_list_in_sector", None)
        if not callable(get_sector):
            context = _raw_context(ContextInfo)
            get_sector = getattr(context, "get_stock_list_in_sector", None) if context else None
        if not callable(get_sector):
            raise NotImplementedError("get_stock_list_in_sector unavailable")
        return get_sector(params.get("sector_name", ""))
    if method == "subscribe_quote":
        return _subscribe(ContextInfo, request, params)
    if method == "unsubscribe_quote":
        return _unsubscribe(ContextInfo, params)
    if method == "download_history_data2":
        return _download_history(params)
    raise ValueError("unsupported method: %s" % method)


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
        data = _jsonable(_handle(ContextInfo, request))
        result = {"request_id": request.get("request_id"), "ok": True, "data": data}
        _atomic_write(os.path.join(RESPONSES, name), result)
    except Exception as exc:
        result = {
            "request_id": request.get("request_id") if request else "",
            "ok": False, "error": repr(exc), "traceback": traceback.format_exc(),
        }
        _atomic_write(os.path.join(ERRORS, name), result)
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
