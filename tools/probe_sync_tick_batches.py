"""Reproduce blackbox-qmt's tick snapshot sync into an isolated Parquet tree.

The production job uses 50-symbol batches, downloads tick history, waits for the
bridge download to complete, sleeps one second, then calls get_market_data_ex
with field_list=[] and writes <root>/<symbol>/<date>.parquet.
"""
import argparse
import json
import time
from pathlib import Path

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=("native", "compat"), required=True)
parser.add_argument("--date", default="20260901")
parser.add_argument("--batch-size", type=int, default=50)
parser.add_argument("--stocks-file", default=None)
parser.add_argument("--output", default=None)
args = parser.parse_args()

output_root = Path(args.output or (Path(r"D:\Temp") / "xtquant-sync-tick-probe" / args.date))
backend_root = output_root / args.backend
backend_root.mkdir(parents=True, exist_ok=True)

if args.backend == "native":
    from xtquant import xtdata
else:
    from xtquant_compat import xtdata

if args.stocks_file:
    stocks = json.loads(Path(args.stocks_file).read_text(encoding="utf-8"))
else:
    stocks = xtdata.get_stock_list_in_sector("沪深A股")
    (output_root / "stocks.json").write_text(json.dumps(stocks, ensure_ascii=False, indent=2), encoding="utf-8")

manifest = {"backend": args.backend, "period": "tick", "date": args.date,
            "batch_size": args.batch_size, "stock_count": len(stocks),
            "stocks": stocks, "batches": []}
total_started = time.time()
total_rows = total_symbols = 0
total_save_seconds = 0.0

for start in range(0, len(stocks), args.batch_size):
    batch = stocks[start:start + args.batch_size]
    t = time.time()
    download = xtdata.download_history_data2(batch, "tick", args.date, args.date)
    download_seconds = time.time() - t
    time.sleep(1.0)
    t = time.time()
    # This is deliberately field_list=[]: it is the exact blackbox get_tick path.
    data = xtdata.get_market_data_ex([], batch, "tick", args.date, args.date)
    query_seconds = time.time() - t
    save_started = time.time()
    saved = []
    rows = 0
    if isinstance(data, dict):
        for symbol, frame in data.items():
            if not isinstance(frame, pd.DataFrame) or frame.empty:
                continue
            target = backend_root / symbol
            target.mkdir(parents=True, exist_ok=True)
            out = frame.copy()
            out.index.name = "datetime"
            out.reset_index().to_parquet(target / f"{args.date}.parquet", index=False, engine="pyarrow")
            saved.append(symbol)
            rows += len(frame)
    save_seconds = time.time() - save_started
    total_rows += rows
    total_symbols += len(saved)
    total_save_seconds += save_seconds
    manifest["batches"].append({"start": start, "end": start + len(batch),
        "stock_count": len(batch), "download_seconds": download_seconds,
        "query_seconds": query_seconds, "save_seconds": save_seconds,
        "rows": rows, "symbols": len(saved), "saved_symbols": saved})
    (backend_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"batch {start} {start + len(batch)} download={download_seconds:.3f} query={query_seconds:.3f} save={save_seconds:.3f} rows {rows} symbols {len(saved)}", flush=True)

print(f"TOTAL seconds={time.time() - total_started:.3f} rows {total_rows} symbols {total_symbols} save_seconds={total_save_seconds:.3f} output {backend_root}", flush=True)
