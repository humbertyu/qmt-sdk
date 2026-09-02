from xtquant_compat import xtdata


class InstrumentClient:
    get = staticmethod(xtdata.get_instrument_detail)
    get_many = staticmethod(xtdata.get_instrument_detail_list)
    list_in_sector = staticmethod(xtdata.get_stock_list_in_sector)

