class MarketClient:
    def __init__(self, backend):
        self._backend = backend

    def get_market_data(self, *args, **kwargs):
        return self._backend.call("get_market_data", *args, **kwargs)

    def get_market_data_ex(self, *args, **kwargs):
        return self._backend.call("get_market_data_ex", *args, **kwargs)

    def get_full_tick(self, *args, **kwargs):
        return self._backend.call("get_full_tick", *args, **kwargs)

    def get_local_data(self, *args, **kwargs):
        return self._backend.call("get_local_data", *args, **kwargs)

    def subscribe_quote(self, *args, **kwargs):
        return self._backend.call("subscribe_quote", *args, **kwargs)

    def unsubscribe_quote(self, *args, **kwargs):
        return self._backend.call("unsubscribe_quote", *args, **kwargs)
