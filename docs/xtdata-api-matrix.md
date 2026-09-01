# xtquant.xtdata API compatibility matrix

Reference: official `xtquant.xtdata` installed locally; distribution `250516.1.1`,
module version `xtquant_250516`, inspected on 2026-09-01.

- ✅ Behavior verified against real Big QMT.
- 🧪 Public name/signature and generic file adapter exist; behavior verification is pending.
- ➖ Public name/signature exists, but MiniQMT-local connection/file semantics differ.

API surface coverage and behavioral compatibility are intentionally reported separately.

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `add_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bind_formula(request_id, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_amount_change(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_call_info(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_conversion_price(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_put_info(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `call_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={})` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `compute_coming_trading_calendar(market, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `connect(ip='', port=None, remember_if_success=True)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `create_array(shape, dtype_tuple, capsule, size)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `create_formula(formula_name, formula_content, formula_params={})` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `create_sector(parent_node, sector_name, overwrite=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `create_sector_folder(parent_node, folder_name, overwrite=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `datetime_to_timetag(datetime, format='%Y%m%d%H%M%S')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `del_formula(formula_name)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `disconnect()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `download_cb_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_etf_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_financial_data(stock_list, table_list=[], start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_financial_data2(stock_list, table_list=[], start_time='', end_time='', callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_his_st_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_contracts(incrementally=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_data(stock_code, period, start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_data2(stock_list, period, start_time='', end_time='', callback=None, incrementally=None)` | 🧪 | Sequential Big QMT download adapter; full-market verification pending. |
| `download_holiday_data(incrementally=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_index_weight()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_metatable_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_sector_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_tabular_data(stock_list, period, start_time='', end_time='', incrementally=None, download_type='validationbypage', source='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `fetch_quote_server_from_config(root_path, key_list)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `gen_factor_index(data_name, formula_name, vars, sector_list, start_time='', end_time='', period='1d', dividend_type='none')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `generate_index_data(formula_name, formula_param={}, stock_list=[], period='1d', dividend_type='none', start_time='', end_time='', fill_mode='fixed', fill_value=nan, result_path=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `getDividFactors(*args, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_kline_trading_periods()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_sub_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_trading_periods()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_authorized_market_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_broker_queue_data(stock_list=[], start_time='', end_time='', count=-1, show_broker_name=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_cb_info(stockcode)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_client()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_current_connect_sub_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_data_dir()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_divid_factors(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_etf_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_field_list(metaid)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_financial_data_ori(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_formula_result(request_id, start_time='', end_time='', count=-1, timeout_second=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_formulas()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_full_kline(field_list=[], stock_list=[], period='1m', start_time='', end_time='', count=1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_full_tick(code_list)` | ✅ | Verified against the current Big QMT three-second quote feed. |
| `get_fullspeed_orderbook(code_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_option_list(undl_code, dedate)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_option_list_batch(undl_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_st_data(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_hk_broker_dict()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_holidays()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_index_weight(index_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_instrument_detail(stock_code, iscomplete=False)` | ✅ | Environment-dependent adapter; real-QMT verification pending. |
| `get_instrument_detail_list(stock_list, iscomplete=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_instrument_type(stock_code, variety_list=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_ipo_info(start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_kline_trading_period(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_order(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_quote(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_transaction(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2thousand_queue(stock_code, gear_num=None, price=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_local_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, data_dir=None)` | 🧪 | `data_dir` cannot retain its MiniQMT-local cache meaning. |
| `get_main_contract(code_market: str, start_time: str = '', end_time: str = '')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ✅ | Field-keyed DataFrame conversion verified. |
| `get_market_data3(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data_ex(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ✅ | Stock-keyed DataFrame conversion verified. |
| `get_market_data_ex_ori(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data_ori(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_last_trade_date(market)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_markets()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_config(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_fields(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_info(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_detail_data(optioncode)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_list(undl_code, dedate, opttype='', isavailavle=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_undl_data(undl_code_ref)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_order_rank(code, order_time, order_type, order_price, order_volume, order_left_volume)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_period_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_quote_server_config()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_quote_server_status()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_sec_main_contract(code_market: str, start_time: str = '', end_time: str = '')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_sector_info(sector_name='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_sector_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_stock_list_in_sector(sector_name, real_timetag=-1)` | ✅ | Environment-dependent adapter; real-QMT verification pending. |
| `get_stock_type(stock_code, variety_list=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_bson(codes: list, fields: list, period: str, start_time: str, end_time: str, count: int = -1, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_formula(codes: list, fields: list, period: str, start_time: str, end_time: str, count: int = -1, dividend_type='none', **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_calendar(market, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_contract_list(stockcode, date=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_dates(market, start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_period(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_transactioncount(code_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_wp_market_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gld(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd2(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd3(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gsl(sector_name, real_timetag=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `hello()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `import_formula(formula_name, file_path)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `is_stock_type(stock, tag)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `push_custom_data(meta, datas, coverall=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `read_feather(file_path)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `reconnect(ip='', port=None, remember_if_success=True)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `remove_sector(sector_name)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `remove_stock_from_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_market_stock_list(market, datas)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_market_trading_day_list(market, datas)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `run()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `show_quote_server_status()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper(callback)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper_1820(callback)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper_convert(callback, metaid)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={}, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_l2thousand(stock_code, gear_num=None, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_l2thousand_queue(stock_code, callback=None, gear_num=None, price=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_quote(stock_code, period='1d', start_time='', end_time='', count=0, callback=None)` | ✅ | Durable callback files verified with real Big QMT. |
| `subscribe_quote2(stock_code, period='1d', start_time='', end_time='', count=0, dividend_type=None, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_whole_quote(code_list, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `supply_history_data(stock_code, period, start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `t2d(timetag, format)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `timetagToDateTime(*args, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `timetag_to_datetime(timetag, format)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `try_except(func)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `unsubscribe_formula(request_id)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `unsubscribe_quote(seq)` | ✅ | Environment-dependent adapter; real-QMT verification pending. |
| `watch_quote_server_status(callback)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `watch_xtquant_status(callback)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `write_feather(dest_path, param, df)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |

## Totals

| Metric | Count |
| --- | ---: |
| Public names and signatures | 138 / 138 |
| ✅ Behavior verified | 7 |
| 🧪 Verification pending | 117 |
| ➖ Different local semantics | 14 |
