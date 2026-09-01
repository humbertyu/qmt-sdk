"""Measure download + get_market_data_ex for one stock across core periods."""
import argparse
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("native", "compat"), required=True)
    parser.add_argument("--stock", default="000779.SZ")
    parser.add_argument("--date", default="20260901")
    args = parser.parse_args()
    if args.backend == "native":
        from xtquant import xtdata
    else:
        from xtquant_compat import xtdata

    fields = ["open", "high", "low", "close", "volume", "amount"]
    for period in ("1d", "1m", "tick"):
        started = time.time()
        progress = []
        download = xtdata.download_history_data2(
            [args.stock], period, args.date, args.date, callback=progress.append,
        )
        download_seconds = time.time() - started
        started = time.time()
        data = xtdata.get_market_data_ex(
            [] if period == "tick" else fields,
            [args.stock], period, args.date, args.date,
        )
        query_seconds = time.time() - started
        frame = data.get(args.stock) if isinstance(data, dict) else None
        print(period, "download=%.3f" % download_seconds,
              "query=%.3f" % query_seconds,
              "rows=%s" % (getattr(frame, "shape", None),),
              "callback_events=%s" % len(progress),
              "download_result=%r" % download)


if __name__ == "__main__":
    main()
