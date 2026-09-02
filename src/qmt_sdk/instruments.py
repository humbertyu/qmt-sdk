class InstrumentClient:
    def __init__(self, backend):
        self._backend = backend

    def get(self, *args, **kwargs):
        return self._backend.call("get_instrument_detail", *args, **kwargs)

    def get_many(self, *args, **kwargs):
        return self._backend.call("get_instrument_detail_list", *args, **kwargs)

    def list_in_sector(self, *args, **kwargs):
        return self._backend.call("get_stock_list_in_sector", *args, **kwargs)

    def get_sector_list(self, *args, **kwargs):
        return self._backend.call("get_sector_list", *args, **kwargs)

    def get_sector_info(self, *args, **kwargs):
        return self._backend.call("get_sector_info", *args, **kwargs)

    def get_trading_dates(self, *args, **kwargs):
        return self._backend.call("get_trading_dates", *args, **kwargs)

    def get_holidays(self, *args, **kwargs):
        return self._backend.call("get_holidays", *args, **kwargs)

    def get_markets(self, *args, **kwargs):
        return self._backend.call("get_markets", *args, **kwargs)

    def get_ipo_info(self, *args, **kwargs):
        return self._backend.call("get_ipo_info", *args, **kwargs)

    def get_etf_info(self, *args, **kwargs):
        return self._backend.call("get_etf_info", *args, **kwargs)

    def get_st_status(self, stock_code):
        return self._backend.call("get_st_status", stock_code)

    def get_his_st_data(self, stock_code):
        return self._backend.call("get_his_st_data", stock_code)

    def get_main_contract(self, code_market, start_time="", end_time=""):
        return self._backend.call("get_main_contract", code_market, start_time, end_time)

    def get_contract_multiplier(self, stock_code):
        return self._backend.call("get_contract_multiplier", stock_code)

    def get_contract_expire_date(self, stock_code):
        return self._backend.call("get_contract_expire_date", stock_code)

    def get_his_contract_list(self, code_market):
        return self._backend.call("get_his_contract_list", code_market)

    def get_weight_in_index(self, index_code, stock_code):
        return self._backend.call("get_weight_in_index", index_code, stock_code)

    def get_option_detail_data(self, option_code):
        return self._backend.call("get_option_detail_data", option_code)

    def get_option_list(self, undl_code, dedate, opttype="", isavailable=False):
        return self._backend.call("get_option_list", undl_code, dedate, opttype, isavailable)

    def get_option_undl_data(self, undl_code_ref=""):
        return self._backend.call("get_option_undl_data", undl_code_ref)

    def get_divid_factors(self, stockcode, date=""):
        return self._backend.call("get_divid_factors", stockcode, date)

    def get_etf_info(self, stockcode):
        return self._backend.call("get_etf_info", stockcode)

    def get_etf_iopv(self, stock_code):
        return self._backend.call("get_etf_iopv", stock_code)
