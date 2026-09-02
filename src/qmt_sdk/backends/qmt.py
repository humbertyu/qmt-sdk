"""QMT runtime backend using the shared file bridge."""

from .. import data
from ..bridge import get_client


class QmtBackend:
    """Backend that exposes the unified request operations."""

    def call(self, method, *args, **kwargs):
        # Typed market methods use the native query path directly.  This
        # avoids legacy xtdata wrappers in the embedded runtime (some builds
        # import pandas there) and preserves QMT's raw payload.
        if method in ("get_market_data_ex", "get_market_data") and args:
            names = ("fields", "stock_code", "period", "start_time", "end_time",
                     "count", "dividend_type", "fill_data")
            if method == "get_market_data_ex":
                names += ("subscribe",)
            params = dict(zip(names, args))
            params.update(kwargs)
            return self.query(method, params)
        function = getattr(data, method)
        return function(*args, **kwargs)

    def query(self, method, params=None, timeout=None):
        """Call a query method through the shared bridge without xtquant shaping."""
        return get_client().request(method, params or {}, timeout=timeout)
