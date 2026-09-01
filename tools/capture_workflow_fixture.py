"""Capture canonical xtdata results for native-vs-compat workflow checks.

Run this script once with the native MiniQMT interpreter and once with the
xtquant-compat virtual environment.  Keeping the processes separate avoids
mixing binary pandas/numpy dependencies from the two environments.
"""

import argparse
import json
import math
from pathlib import Path


def _json_scalar(value):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    item = getattr(value, "item", None)
    if callable(item):
        return _json_scalar(item())
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _canonical(value):
    if isinstance(value, dict):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if hasattr(value, "columns") and hasattr(value, "index"):
        return {
            "__type__": "%s.%s" % (type(value).__module__, type(value).__name__),
            "shape": list(value.shape),
            "columns": [_json_scalar(item) for item in value.columns.tolist()],
            "index_name": _json_scalar(value.index.name),
            "index": [_json_scalar(item) for item in value.index.tolist()],
            "dtypes": [str(item) for item in value.dtypes.tolist()],
            "records": [
                {str(key): _canonical(item) for key, item in row.items()}
                for row in value.to_dict("records")
            ],
        }
    return _json_scalar(value)


def _load_xtdata(backend):
    if backend == "native":
        from xtquant import xtdata
    else:
        from xtquant_compat import xtdata
    return xtdata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("native", "compat"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stock", default="000779.SZ")
    parser.add_argument("--date", default="20260901")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()

    xtdata = _load_xtdata(args.backend)
    stock_list = xtdata.get_stock_list_in_sector("沪深A股")
    selected = [args.stock]
    progress = []
    downloads = {}
    if args.download:
        for period in ("1d", "1m", "tick"):
            downloads[period] = xtdata.download_history_data2(
                selected,
                period=period,
                start_time=args.date,
                end_time=args.date,
                callback=progress.append,
            )

    fields = ["open", "high", "low", "close", "volume", "amount"]
    payload = {
        "backend": args.backend,
        "stock": args.stock,
        "date": args.date,
        "stock_list": stock_list,
        "instrument_detail": xtdata.get_instrument_detail(args.stock),
        "market_data_amount_1d": xtdata.get_market_data(
            ["amount"], selected, "1d", args.date, args.date,
        ),
        "market_data_ex_1d": xtdata.get_market_data_ex(
            fields, selected, "1d", args.date, args.date,
        ),
        "market_data_ex_1m": xtdata.get_market_data_ex(
            fields, selected, "1m", args.date, args.date,
        ),
        "market_data_ex_tick": xtdata.get_market_data_ex(
            [], selected, "tick", args.date, args.date,
        ),
        "downloads": downloads,
        "download_progress": progress,
    }
    canonical = _canonical(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print("wrote %s" % args.output)


if __name__ == "__main__":
    main()
