"""Read-only acceptance probe for the two APIs used by instrument workflows."""
import inspect
import time

from xtquant_compat import xtdata


def call(label, function, *args, **kwargs):
    started = time.time()
    try:
        value = function(*args, **kwargs)
        print(label, "OK", "seconds=%.3f" % (time.time() - started))
        return value
    except Exception as exc:
        print(label, "ERROR", type(exc).__name__, repr(exc), "seconds=%.3f" % (time.time() - started))
        return None


print("stock_signature", inspect.signature(xtdata.get_stock_list_in_sector))
print("market_signature", inspect.signature(xtdata.get_market_data))
stocks = call("sector_hs_a", xtdata.get_stock_list_in_sector, "沪深A股") or []
print("sector_count", len(stocks), "unique", len(set(stocks)), "duplicates", len(stocks) - len(set(stocks)))
print("sector_first5", stocks[:5], "sector_last5", stocks[-5:])
for label, sector in (("sector_empty", ""), ("sector_unknown", "__XTQUANT_COMPAT_UNKNOWN__")):
    value = call(label, xtdata.get_stock_list_in_sector, sector)
    print(label + "_result", type(value).__name__, len(value) if value is not None else None)

sample = stocks[:2]
data = call(
    "market_two",
    xtdata.get_market_data,
    ["amount"], sample, "1d", "20260831", "20260831",
)
if isinstance(data, dict):
    frame = data.get("amount")
    print("market_two_shape", getattr(frame, "shape", None), "index", list(getattr(frame, "index", [])))
    print("market_two_columns", list(getattr(frame, "columns", [])))

full_started = time.time()
full = call(
    "market_full",
    xtdata.get_market_data,
    ["amount"], stocks, "1d", "20260831", "20260831",
)
if isinstance(full, dict):
    frame = full.get("amount")
    print("market_full_shape", getattr(frame, "shape", None))
for label, args in (("market_empty_stocks", (["amount"], [], "1d", "20260831", "20260831")),
                    ("market_no_data_date", (["amount"], sample, "1d", "19000101", "19000101")),
                    ("market_count_one", (["amount"], sample, "1d", "20260831", "20260831", 1))):
    value = call(label, xtdata.get_market_data, *args)
    print(label + "_result", type(value).__name__, list(value) if isinstance(value, dict) else None)
print("bridge", xtdata.bridge_status())
