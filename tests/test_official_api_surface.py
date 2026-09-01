import inspect

from xtquant_compat import xtdata


OFFICIAL_XTDATA_FUNCTIONS = {
    "call_formula", "download_etf_info", "download_financial_data",
    "download_financial_data2", "download_history_data", "download_history_data2",
    "download_holiday_data", "gen_factor_index", "getDividFactors",
    "get_divid_factors", "get_download_status", "get_etf_info",
    "get_financial_data", "get_formula_result", "get_full_tick",
    "get_his_option_list", "get_his_option_list_batch", "get_holidays",
    "get_instrument_detail", "get_instrument_type", "get_instrumentdetail",
    "get_ipo_info", "get_local_data", "get_market_data", "get_market_data_ex",
    "get_option_list", "get_sector_info", "get_sector_list",
    "get_stock_list_in_sector", "get_stock_type", "get_trading_dates", "run",
    "submit_download_history_data", "submit_download_history_data2",
    "subscribe_formula", "subscribe_quote", "subscribe_quote2",
    "subscribe_whole_quote", "unsubscribe_formula", "unsubscribe_quote",
    "wait_download",
}


def test_all_official_xtdata_functions_have_public_entries():
    missing = sorted(name for name in OFFICIAL_XTDATA_FUNCTIONS if not callable(getattr(xtdata, name, None)))
    assert missing == []
    assert len(OFFICIAL_XTDATA_FUNCTIONS) == 41


def test_important_native_signatures_are_preserved():
    assert str(inspect.signature(xtdata.get_instrument_detail)) == "(stock_code, is_detail=False)"
    assert str(inspect.signature(xtdata.download_history_data2)) == (
        "(stock_list, period, start_time='', end_time='', callback=None, "
        "incrementally=None, dividend_type='none')"
    )
    assert str(inspect.signature(xtdata.subscribe_quote2)) == (
        "(stock_code, period='1d', start_time='', end_time='', count=0, "
        "dividend_type=None, callback=None)"
    )

