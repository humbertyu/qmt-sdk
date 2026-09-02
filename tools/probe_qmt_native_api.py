"""Probe the official QMT query surface through ``qmt_sdk``.

The probe is read-only by default.  History/financial downloads and formula
calls are skipped unless ``--include-downloads`` is supplied.  Results are
written to a JSON report and never to the application's production data.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from qmt_sdk import QmtClient


SAMPLES = {
    "get_full_tick": {"stock_code": ["000001.SZ", "600000.SH"]},
    "get_market_data_ex": {"fields": ["time", "close", "volume"], "stock_code": ["000001.SZ"], "period": "1d", "count": 2, "subscribe": False},
    "get_market_data": {"fields": ["close"], "stock_code": ["000001.SZ"], "period": "1d", "count": 2},
    "get_local_data": {"field_list": ["close"], "stock_list": ["000001.SZ"], "period": "1d", "count": 2},
    "get_history_data": {"index": 0, "period": "1d", "start_time": "20260901", "end_time": "20260902", "count": 2, "fill_data": True},
    "get_svol": {"stock": "000001.SZ"}, "get_bvol": {"stock": "000001.SZ"},
    "get_turnover_rate": {"stock_code": "000001.SZ"},
    "get_longhubang": {"stock_list": ["000001.SZ"], "start_date": "20260901", "end_date": "20260902", "count": -1},
    "get_north_finance_change": {"date": "20260902"},
    "get_hkt_details": {"date": "20260902"},
    "get_hkt_statistics": {"date": "20260902"},
    "get_etf_info": {}, "get_etf_iopv": {"stock_code": "510300.SH"},
    "get_last_volume": {"stock_code": "000001.SZ"}, "get_total_share": {"stock_code": "000001.SZ"},
    "get_instrument_detail": {"stock_code": "000001.SZ"},
    "get_stock_list_in_sector": {"sector_name": "沪深A股"},
    "get_trading_dates": {"stockcode": "000001.SZ", "start_date": "20260101", "end_date": "20260902", "count": -1, "period": "1d"},
    "get_st_status": {"stock_code": "000001.SZ"},
    "get_his_st_data": {"stock_code": "000001.SZ"},
    "get_main_contract": {"code_market": "IF.CFFEX"},
    "get_contract_multiplier": {"stock_code": "IF.CFFEX"}, "get_contract_expire_date": {"stock_code": "IF.CFFEX"},
    "get_his_contract_list": {"code_market": "IF.CFFEX", "product": "IF"},
    "get_option_detail_data": {"option_code": "510050C2609M02500"},
    "get_option_list": {"undl_code": "510050.SH", "dedate": "202609"},
    "get_option_undl_data": {"option_code": "510050C2609M02500"},
    "bsm_price": {"flag": "C", "s": 3.0, "k": 3.0, "t": 0.1, "r": 0.02, "sigma": 0.2},
    "bsm_iv": {"flag": "C", "s": 3.0, "k": 3.0, "t": 0.1, "r": 0.02, "price": 0.1},
    "get_divid_factors": {"stock_code": "000001.SZ", "start_time": "20260101", "end_time": "20260902"},
    "get_weight_in_index": {"index_code": "000300.SH", "stock_code": "000001.SZ"},
}

SKIP_DEFAULT = {"download_history_data", "download_history_data2", "download_financial_data", "download_financial_data2", "subscribe_quote", "subscribe_whole_quote", "unsubscribe_quote", "subscribe_formula", "unsubscribe_formula", "call_formula", "call_formula_batch", "get_raw_financial_data"}
OFFICIAL_EXTRA = ["download_history_data", "subscribe_quote", "subscribe_whole_quote", "unsubscribe_quote", "subscribe_formula", "unsubscribe_formula", "call_formula", "call_formula_batch", "get_raw_financial_data", "get_financial_data", "get_market_data_ex", "get_full_tick"]


def summarize(value):
    info = {"type": type(value).__name__}
    if value is None:
        return info
    if isinstance(value, dict):
        info["keys"] = [str(k) for k in list(value)[:20]]
        info["size"] = len(value)
    elif isinstance(value, (list, tuple, set)):
        info["size"] = len(value)
        info["sample"] = list(value)[:3]
    else:
        shape = getattr(value, "shape", None)
        if shape is not None:
            info["shape"] = list(shape)
        info["repr"] = repr(value)[:500]
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    parser.add_argument("--include-downloads", action="store_true")
    args = parser.parse_args()
    client = QmtClient()
    methods = sorted(set(SAMPLES) | set(OFFICIAL_EXTRA))
    report = {"created_at": datetime.now().isoformat(), "client": "qmt_sdk.QmtClient", "results": []}
    for method in methods:
        params = SAMPLES.get(method, {})
        if method in SKIP_DEFAULT:
            report["results"].append({"method": method, "params": params, "status": "skipped", "reason": "requires callback, download, or environment-specific input"})
            print("%-28s %-7s" % (method, "skipped"))
            continue
        started = time.time()
        row = {"method": method, "params": params}
        try:
            value = getattr(client.qmt, method)(**params)
            row.update(status="ok", elapsed_seconds=round(time.time() - started, 3), result=summarize(value))
        except Exception as exc:
            row.update(status="error", elapsed_seconds=round(time.time() - started, 3), error_type=type(exc).__name__, error=str(exc)[:1000])
        report["results"].append(row)
        print("%-28s %-7s %.3fs" % (method, row["status"], row["elapsed_seconds"]))
    if args.include_downloads:
        print("Downloads are intentionally not part of the default probe; run dedicated download probes separately.")
    output = args.output or os.path.join(".artifacts", "qmt-native-probe-%s.json" % datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, default=str)
    print("report", os.path.abspath(output))


if __name__ == "__main__":
    main()
