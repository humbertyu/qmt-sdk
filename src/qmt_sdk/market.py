class MarketClient:
    def __init__(self, backend):
        self._backend = backend

    def get_market_data(self, fields=None, stock_code=None, period="follow",
                        start_time="", end_time="", count=-1,
                        dividend_type="follow", fill_data=True):
        return self._backend.call("get_market_data", fields, stock_code, period,
                                  start_time, end_time, count, dividend_type,
                                  fill_data)

    def get_market_data_ex(self, fields=None, stock_code=None, period="follow",
                           start_time="", end_time="", count=-1,
                           dividend_type="follow", fill_data=True, subscribe=True):
        return self._backend.call("get_market_data_ex", fields, stock_code, period,
                                  start_time, end_time, count, dividend_type,
                                  fill_data, subscribe)

    def get_full_tick(self, stock_code):
        return self._backend.call("get_full_tick", stock_code)

    def get_local_data(self, fields=None, stock_code=None, period="follow",
                       start_time="", end_time="", count=-1,
                       dividend_type="follow", fill_data=True, data_dir=None):
        return self._backend.call("get_local_data", fields, stock_code, period,
                                  start_time, end_time, count, dividend_type,
                                  fill_data, data_dir)

    def subscribe_quote(self, stock_code, period="tick", start_time="", end_time="",
                        count=0, callback=None):
        return self._backend.call("subscribe_quote", stock_code, period, start_time,
                                  end_time, count, callback)

    def subscribe_whole_quote(self, code_list, callback=None):
        return self._backend.call("subscribe_whole_quote", code_list, callback)

    def subscribe_formula(self, formula_name, stock_code, period, start_time="",
                          end_time="", count=-1, dividend_type=None,
                          extend_param=None, callback=None):
        return self._backend.call("subscribe_formula", formula_name, stock_code,
                                  period, start_time, end_time, count,
                                  dividend_type, extend_param or {}, callback)

    def unsubscribe_quote(self, subscription_id):
        return self._backend.call("unsubscribe_quote", subscription_id)

    def unsubscribe_formula(self, request_id):
        return self._backend.call("unsubscribe_formula", request_id)

    def call_formula(self, formula_name, stock_code, period, start_time="",
                     end_time="", count=-1, dividend_type=None, extend_param=None):
        return self._backend.call("call_formula", formula_name, stock_code, period,
                                  start_time, end_time, count, dividend_type,
                                  extend_param or {})

    def call_formula_batch(self, *args, **kwargs):
        return self._backend.call("call_formula_batch", *args, **kwargs)

    def download_history_data2(self, *args, **kwargs):
        return self._backend.call("download_history_data2", *args, **kwargs)

    def download_history_data(self, *args, **kwargs):
        return self._backend.call("download_history_data", *args, **kwargs)

    def get_divid_factors(self, *args, **kwargs):
        return self._backend.call("get_divid_factors", *args, **kwargs)
