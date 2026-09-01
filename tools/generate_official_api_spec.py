"""Generate a public API signature snapshot from an installed official xtquant."""

import inspect
import json
from pathlib import Path

import xtquant
import xtquant.xtdata as xtdata


def json_default(value):
    if isinstance(value, type):
        return {"__type__": value.__name__}
    return {"__repr__": repr(value)}


def main():
    functions = []
    for name, function in inspect.getmembers(xtdata, inspect.isfunction):
        if name.startswith("_"):
            continue
        signature = inspect.signature(function)
        parameters = []
        for parameter in signature.parameters.values():
            item = {"name": parameter.name, "kind": parameter.kind.name}
            if parameter.default is not inspect.Parameter.empty:
                item["default"] = parameter.default
            if parameter.annotation is not inspect.Parameter.empty:
                annotation = parameter.annotation
                item["annotation"] = getattr(annotation, "__name__", str(annotation))
            parameters.append(item)
        functions.append({
            "name": name,
            "signature": str(signature),
            "parameters": parameters,
        })
    payload = {
        "source": "installed official xtquant.xtdata",
        "distribution_version": "250516.1.1",
        "module_version": getattr(xtquant, "__version__", None),
        "snapshot_date": "2026-09-01",
        "function_count": len(functions),
        "functions": functions,
    }
    destination = Path(__file__).parents[1] / "src" / "xtquant_compat" / "official_xtdata_api.json"
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    verified = {
        "get_market_data",
    }
    partial = {
        "download_history_data2", "get_full_tick", "get_instrument_detail",
        "get_market_data_ex", "get_stock_list_in_sector", "subscribe_quote",
        "unsubscribe_quote",
    }
    different = {
        "connect", "disconnect", "reconnect", "get_client", "get_data_dir",
        "get_quote_server_config", "get_quote_server_status", "show_quote_server_status",
        "watch_quote_server_status", "watch_xtquant_status", "read_feather", "write_feather",
        "fetch_quote_server_from_config", "create_array",
    }
    notes = {
        "get_full_tick": (
            "Core quote fields verified against the current three-second feed; complete "
            "field parity remains pending."
        ),
        "download_history_data2": (
            "Two-stock `1d`/`1m`/`tick` workflow passed; strict native callback "
            "timing/fields and full-market load remain unverified."
        ),
        "get_instrument_detail": (
            "All 31 native fields passed for one stock; the result retains four Big "
            "QMT-only fields and other instrument types remain pending."
        ),
        "get_market_data": (
            "Native field-keyed, stock-by-timetag DataFrame orientation and one-day "
            "values verified."
        ),
        "get_market_data_ex": (
            "`1d`/`1m` passed; Tick structure and core data match but `stockStatus`, "
            "`pvolume`, `tickvol`, and `pe` differ or use placeholders."
        ),
        "get_stock_list_in_sector": (
            "Shape verified. Tested Big QMT universe contained all MiniQMT symbols plus "
            "10 newer symbols."
        ),
        "subscribe_quote": (
            "Callback envelope and timestamps verified; complete callback field parity "
            "and native sequence identity differ or remain pending."
        ),
        "unsubscribe_quote": (
            "Real Big QMT unsubscribe action verified; native return-value semantics "
            "remain pending."
        ),
        "get_local_data": "`data_dir` cannot retain its MiniQMT-local cache meaning.",
    }
    rows = []
    for item in functions:
        name = item["name"]
        if name in verified:
            status = "✅"
        elif name in partial:
            status = "⚠️"
        elif name in different:
            status = "➖"
        else:
            status = "🧪"
        note = notes.get(name, "Environment-dependent adapter; real-QMT verification pending.")
        rows.append("| `%s%s` | %s | %s |" % (name, item["signature"], status, note))
    generated = "\n".join([
        "| Official API and signature | Status | Notes |",
        "| --- | --- | --- |",
        *rows,
        "",
        "### Totals",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        "| Public names and signatures | 138 / 138 |",
        "| ✅ Fully verified for the tested scope | %d |" % len(verified),
        "| ⚠️ Operational with known differences | %d |" % len(partial),
        "| 🧪 Verification pending | %d |" % (
            len(functions) - len(verified) - len(partial) - len(different)
        ),
        "| ➖ Different local semantics | %d |" % len(different),
    ])
    matrix_path = Path(__file__).parents[1] / "docs" / "xtdata-api-matrix.md"
    matrix = matrix_path.read_text(encoding="utf-8")
    start_marker = "<!-- GENERATED_API_MATRIX_START -->"
    end_marker = "<!-- GENERATED_API_MATRIX_END -->"
    before, remainder = matrix.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)
    matrix_path.write_text(
        before + start_marker + "\n\n" + generated + "\n" + end_marker + after,
        encoding="utf-8",
    )
    print("wrote %s functions to %s" % (len(functions), destination))
    print("wrote compatibility matrix to %s" % matrix_path)


if __name__ == "__main__":
    main()
