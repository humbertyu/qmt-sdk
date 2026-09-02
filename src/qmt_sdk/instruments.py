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
