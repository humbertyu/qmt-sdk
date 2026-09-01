"""Compare canonical workflow fixtures captured from native and compat APIs."""

import argparse
import json
from pathlib import Path


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _frame_summary(frame):
    if not isinstance(frame, dict) or frame.get("__type__") is None:
        return None
    return {
        "shape": frame.get("shape"),
        "columns": frame.get("columns"),
        "index_name": frame.get("index_name"),
        "dtypes": frame.get("dtypes"),
        "index_equal": None,
        "records_equal": None,
    }


def _compare_value(native, compat):
    native_frame = _frame_summary(native)
    compat_frame = _frame_summary(compat)
    if native_frame is not None or compat_frame is not None:
        result = {"native": native_frame, "compat": compat_frame}
        if native_frame is not None and compat_frame is not None:
            result["index_equal"] = native.get("index") == compat.get("index")
            result["records_equal"] = native.get("records") == compat.get("records")
        return result
    if isinstance(native, dict) and isinstance(compat, dict):
        keys = sorted(set(native) | set(compat))
        return {key: _compare_value(native.get(key), compat.get(key)) for key in keys}
    return {"equal": native == compat, "native": native, "compat": compat}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("native", type=Path)
    parser.add_argument("compat", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    native = _load(args.native)
    compat = _load(args.compat)
    sections = (
        "stock_list", "instrument_detail", "market_data_amount_1d",
        "market_data_ex_1d", "market_data_ex_1m", "market_data_ex_tick",
        "downloads", "download_progress",
    )
    report = {section: _compare_value(native.get(section), compat.get(section)) for section in sections}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
        print("wrote %s" % args.output)
    else:
        print(rendered)


if __name__ == "__main__":
    main()
