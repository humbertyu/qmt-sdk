class FinancialClient:
    def __init__(self, backend):
        self._backend = backend

    def get(self, *args, **kwargs):
        return self._backend.call("get_financial_data", *args, **kwargs)

    def get_raw(self, *args, **kwargs):
        return self._backend.call("get_financial_data_ori", *args, **kwargs)

    def download(self, *args, **kwargs):
        return self._backend.call("download_financial_data2", *args, **kwargs)

    def download_basic(self, *args, **kwargs):
        return self._backend.call("download_financial_data", *args, **kwargs)
