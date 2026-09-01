# xtquant.xtdata API compatibility matrix

Reference snapshot: the locally installed official `xtquant.xtdata` module inspected on
2026-09-01. That installation exposes 41 public Python functions but provides no package
version metadata. Signatures may differ in other QMT releases; contributions containing
additional official signatures are welcome.

Status definitions:

- ✅ Implemented: public entry and return-shape conversion are implemented and tested.
- 🧪 Experimental: the public entry and bridge adapter exist, but real-QMT behavioral verification is incomplete.
- ➖ Different semantics: a Big QMT file bridge cannot reproduce the MiniQMT-local meaning exactly.

Calling an absent API raises Python's normal `AttributeError`; the project never silently returns
empty data for an unimplemented API.

## Market data and subscriptions

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `get_full_tick(code_list)` | ✅ | Big QMT snapshot verified against the existing three-second feed. |
| `get_market_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ✅ | Converted to field-keyed DataFrames with stock columns. |
| `get_market_data_ex(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ✅ | Converted to stock-keyed DataFrames. |
| `get_local_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, data_dir=None)` | ➖ | `data_dir` is a MiniQMT-local cache concept; a Big QMT query fallback is planned. |
| `subscribe_quote(stock_code, period='1d', start_time='', end_time='', count=0, callback=None)` | ✅ | Durable file events; callback normalized to `{stock: [tick]}`. |
| `subscribe_quote2(stock_code, period='1d', start_time='', end_time='', count=0, dividend_type=None, callback=None)` | 🧪 | Dividend-aware subscription variant. |
| `subscribe_whole_quote(code_list, callback=None)` | 🧪 | Big QMT callable exists; durable event fan-out is not implemented. |
| `unsubscribe_quote(seq)` | ✅ | Cancels the underlying Big QMT subscription. |
| `run()` | 🧪 | External event reader currently starts automatically after subscription. |

## Historical downloads

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `download_history_data(stock_code, period, start_time='', end_time='', incrementally=None, dividend_type='none')` | 🧪 | Uses Big QMT `down_history_data`; extra flags are not yet behaviorally matched. |
| `download_history_data2(stock_list, period, start_time='', end_time='', callback=None, incrementally=None, dividend_type='none')` | 🧪 | Sequential Big QMT downloads; completion callback and 600-second timeout implemented. |
| `submit_download_history_data(stock_code, period, start_time='', end_time='', incrementally=None)` | 🧪 | Asynchronous job API. |
| `submit_download_history_data2(stock_list, period, start_time='', end_time='', incrementally=None)` | 🧪 | Asynchronous batch job API. |
| `get_download_status(job_id)` | 🧪 | Requires a durable file-job registry. |
| `wait_download(job_id, timeout=None, poll_interval=None, callback=None)` | 🧪 | Requires a durable file-job registry. |

## Instruments, sectors, and calendars

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `get_instrument_detail(stock_code, is_detail=False)` | ✅ | Big QMT details verified; `is_detail` is accepted as a compatibility parameter. |
| `get_instrumentdetail(stock_code)` | 🧪 | Legacy spelling alias. |
| `get_instrument_type(stock_code, variety_list=None)` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `get_stock_type(stock)` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `get_stock_list_in_sector(sector_name, real_timetag=-1)` | ✅ | `real_timetag` is accepted; current Big QMT call uses the sector name. |
| `get_sector_info(sector_name='')` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `get_sector_list()` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `get_trading_dates(market, start_time='', end_time='', count=-1)` | 🧪 | Generic calendar adapter; verification pending. |
| `get_holidays()` | 🧪 | Generic calendar adapter; verification pending. |
| `download_holiday_data(incrementally=True)` | 🧪 | Generic download adapter; verification pending. |
| `get_ipo_info(start_time='', end_time='')` | 🧪 | Generic ContextInfo adapter; verification pending. |

## Corporate actions and financial data

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `get_divid_factors(stock_code, start_time='', end_time='')` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `getDividFactors(*args, **kwargs)` | 🧪 | Legacy alias for dividend factors. |
| `get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')` | 🧪 | Must avoid Big QMT's pandas-dependent wrapper. |
| `download_financial_data(stock_list, table_list=[], start_time='', end_time='', incrementally=None)` | 🧪 | Depends on callable availability in the QMT build. |
| `download_financial_data2(stock_list, table_list=[], start_time='', end_time='', callback=None)` | 🧪 | Depends on callable availability in the QMT build. |

## ETF and options

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `get_etf_info()` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `download_etf_info()` | 🧪 | Generic download adapter; verification pending. |
| `get_option_list(undl_code, dedate, opttype='', isavailavle=False)` | 🧪 | Signature preserves the official `isavailavle` spelling. |
| `get_his_option_list(undl_code, dedate)` | 🧪 | Generic ContextInfo adapter; verification pending. |
| `get_his_option_list_batch(undl_code, start_time='', end_time='')` | 🧪 | Generic ContextInfo adapter; verification pending. |

## Formula system

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `call_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={})` | 🧪 | Requires request/result lifecycle support. |
| `get_formula_result(request_id, start_time='', end_time='', count=-1, timeout_second=-1)` | 🧪 | Requires request/result lifecycle support. |
| `subscribe_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={}, callback=None)` | 🧪 | Requires durable formula events. |
| `unsubscribe_formula(request_id)` | 🧪 | Requires formula subscription registry. |
| `gen_factor_index(data_name, formula_name, vars, sector_list, start_time='', end_time='', period='1d', dividend_type='none')` | 🧪 | Generic formula adapter; verification pending. |

## Current totals

| Status | Count |
| --- | ---: |
| ✅ Implemented | 7 |
| 🧪 Experimental | 33 |
| ➖ Different semantics | 1 |
| Total official functions in reference snapshot | 41 |
