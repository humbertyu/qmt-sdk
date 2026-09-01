import inspect
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=("native", "compat"), default="compat")
args = parser.parse_args()
if args.backend == "native":
    from xtquant import xtdata
else:
    from xtquant_compat import xtdata

print("signature", inspect.signature(xtdata.download_history_data))
print("signature2", inspect.signature(xtdata.download_history_data2))
stock = "000779.SZ"
for period in ("1d", "1m", "tick"):
    started = time.time()
    result = xtdata.download_history_data(stock, period, "20260901", "20260901")
    fields = [] if period == "tick" else ["open", "high", "low", "close", "volume", "amount"]
    data = xtdata.get_market_data_ex(fields, [stock], period, "20260901", "20260901")
    frame = data.get(stock) if isinstance(data, dict) else None
    print(period, "elapsed=%.3f" % (time.time() - started), "result=%r" % result,
          "shape=%r" % (getattr(frame, "shape", None),))
