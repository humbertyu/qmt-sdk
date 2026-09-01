import argparse
import json
from pathlib import Path
import time

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=("native", "compat"), required=True)
parser.add_argument("--date", default="20260901")
parser.add_argument("--batch-size", type=int, default=1000)
parser.add_argument(
    "--output",
    default=None,
    help="独立输出根目录；默认 D:\\Temp\\xtquant-sync-1d-probe\\<date>",
)
parser.add_argument(
    "--stocks-file",
    default=None,
    help="可选：使用 JSON 股票列表文件，确保 native/compat 使用完全相同的样本",
)
args = parser.parse_args()

output_root = Path(args.output or (Path(r"D:\Temp\xtquant-sync-1d-probe") / args.date))
backend_root = output_root / args.backend
backend_root.mkdir(parents=True, exist_ok=True)

if args.backend == "native":
    from xtquant import xtdata
else:
    from xtquant_compat import xtdata

if args.stocks_file:
    stocks = json.loads(Path(args.stocks_file).read_text(encoding="utf-8"))
    if not isinstance(stocks, list) or not all(isinstance(item, str) for item in stocks):
        raise ValueError("--stocks-file must contain a JSON string array")
else:
    stocks = xtdata.get_stock_list_in_sector("沪深A股")
    # Make the native list reusable by the compat run without querying a
    # potentially different sector universe.
    (output_root / "stocks.json").write_text(
        json.dumps(stocks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
print("backend", args.backend, "stocks", len(stocks), "batch_size", args.batch_size, flush=True)
total_started = time.time()
total_rows = 0
total_symbols = 0
total_save_seconds = 0.0
manifest = {
    "backend": args.backend,
    "date": args.date,
    "batch_size": args.batch_size,
    "stock_count": len(stocks),
    "stocks": stocks,
    "batches": [],
}


def save_frames(data, batch, target_root):
    """Save one production-shaped parquet per symbol without touching production data.

    Current xtdata implementations return {symbol: DataFrame}.  The fallback also
    accepts the official field-oriented shape {field: DataFrame}, splitting rows
    by symbol where possible.
    """
    saved = []
    if not isinstance(data, dict):
        return saved
    for key, value in data.items():
        if not isinstance(value, pd.DataFrame):
            continue
        if key in batch:
            frame = value
            if not frame.empty:
                frame.to_parquet(target_root / f"{key}.parquet", index=True)
                saved.append(key)
            continue
        # Field-oriented result: index/columns may contain symbols.
        for symbol in batch:
            if symbol in value.columns:
                frame = value[[symbol]].copy()
                frame.columns = [key]
                target = target_root / f"{symbol}.parquet"
                if target.exists():
                    old = pd.read_parquet(target)
                    frame = old.join(frame, how="outer")
                frame.to_parquet(target, index=True)
                if symbol not in saved:
                    saved.append(symbol)
    return saved


for start in range(0, len(stocks), args.batch_size):
    batch = stocks[start:start + args.batch_size]
    started = time.time()
    download = xtdata.download_history_data2(batch, "1d", args.date, args.date)
    download_seconds = time.time() - started
    started = time.time()
    data = xtdata.get_market_data_ex(
        ["open", "high", "low", "close", "volume", "amount"],
        batch, "1d", args.date, args.date,
    )
    query_seconds = time.time() - started
    # Each symbol is written as a production-shaped parquet directly under the
    # isolated backend directory.  The manifest retains batch boundaries.
    save_started = time.time()
    saved_symbols = save_frames(data, batch, backend_root)
    save_seconds = time.time() - save_started
    rows = sum(len(frame) for frame in data.values() if isinstance(frame, pd.DataFrame))
    symbols = sum(1 for frame in data.values() if isinstance(frame, pd.DataFrame) and not frame.empty)
    total_rows += rows
    total_symbols += symbols
    total_save_seconds += save_seconds
    manifest["batches"].append({
        "start": start,
        "end": start + len(batch),
        "stock_count": len(batch),
        "download_seconds": download_seconds,
        "query_seconds": query_seconds,
        "save_seconds": save_seconds,
        "rows": rows,
        "symbols": symbols,
        "saved_symbols": saved_symbols,
    })
    (backend_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("batch", start, start + len(batch), "download=%.3f" % download_seconds,
          "query=%.3f" % query_seconds, "rows", rows, "symbols", symbols,
          "result_type", type(download).__name__, flush=True)
print("TOTAL seconds=%.3f" % (time.time() - total_started), "rows", total_rows,
      "symbols", total_symbols, "save_seconds=%.3f" % total_save_seconds,
      "output", backend_root, flush=True)
