import inspect
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=("native", "compat"), default="compat")
parser.add_argument("--repeat", type=int, default=1)
args = parser.parse_args()
if args.backend == "native":
    from xtquant import xtdata
else:
    from xtquant_compat import xtdata

print("signature", inspect.signature(xtdata.download_history_data))
print("signature2", inspect.signature(xtdata.download_history_data2))
stock = "000779.SZ"
for period in ("1d", "1m", "tick"):
  for run in range(args.repeat):
    started = time.time()
    result = xtdata.download_history_data(stock, period, "20260901", "20260901")
    downloaded = time.time()
    fields = [] if period == "tick" else ["open", "high", "low", "close", "volume", "amount"]
    data = xtdata.get_market_data_ex(fields, [stock], period, "20260901", "20260901")
    frame = data.get(stock) if isinstance(data, dict) else None
    print(period, "run=%d" % (run + 1), "download=%.3f" % (downloaded - started),
          "query=%.3f" % (time.time() - downloaded), "elapsed=%.3f" % (time.time() - started), "result=%r" % result,
          "shape=%r" % (getattr(frame, "shape", None),))
