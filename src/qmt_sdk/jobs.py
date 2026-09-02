from xtquant_compat import xtdata


class JobClient:
    status = staticmethod(xtdata.get_request_status)
    cancel = staticmethod(xtdata.cancel_request)
    bridge_status = staticmethod(xtdata.bridge_status)

