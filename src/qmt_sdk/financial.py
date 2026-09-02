from xtquant_compat import xtdata


class FinancialClient:
    get = staticmethod(xtdata.get_financial_data)
    get_raw = staticmethod(xtdata.get_financial_data_ori)
    download = staticmethod(xtdata.download_financial_data2)
    download_basic = staticmethod(xtdata.download_financial_data)

