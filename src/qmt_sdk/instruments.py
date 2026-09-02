class InstrumentClient:
    def __init__(self, backend):
        self._backend = backend

    def get(self, *args, **kwargs):
        return self._backend.call("get_instrument_detail", *args, **kwargs)

    def get_many(self, *args, **kwargs):
        return self._backend.call("get_instrument_detail_list", *args, **kwargs)

    def list_in_sector(self, *args, **kwargs):
        return self._backend.call("get_stock_list_in_sector", *args, **kwargs)
