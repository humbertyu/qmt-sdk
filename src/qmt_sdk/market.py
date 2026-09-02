from xtquant_compat import xtdata


class MarketClient:
    get_market_data = staticmethod(xtdata.get_market_data)
    get_market_data_ex = staticmethod(xtdata.get_market_data_ex)
    get_full_tick = staticmethod(xtdata.get_full_tick)
    get_local_data = staticmethod(xtdata.get_local_data)
    subscribe_quote = staticmethod(xtdata.subscribe_quote)
    unsubscribe_quote = staticmethod(xtdata.unsubscribe_quote)

