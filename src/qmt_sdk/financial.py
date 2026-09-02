class FinancialClient:
    def __init__(self, backend):
        self._backend = backend

    def get(self, *args, **kwargs):
        return self._backend.call("get_financial_data", *args, **kwargs)

    def get_raw(self, *args, **kwargs):
        return self._backend.call("get_financial_data_ori", *args, **kwargs)

    def get_last_volume(self, stock_code):
        return self._backend.call("get_last_volume", stock_code)

    def get_total_share(self, stock_code):
        return self._backend.call("get_total_share", stock_code)

    def get_raw_financial_data(self, field_list, stock_list, start_date="",
                               end_date="", report_type="report_time",
                               result_type="dict", is_detail=False):
        return self._backend.call("get_raw_financial_data", field_list, stock_list,
                                  start_date, end_date, report_type, result_type,
                                  is_detail)
