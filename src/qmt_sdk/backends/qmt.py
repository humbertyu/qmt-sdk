"""QMT runtime backend using the shared file bridge."""

from .. import data
from ..bridge import get_client


class QmtBackend:
    """Backend that exposes the unified request operations."""

    def call(self, method, *args, **kwargs):
        function = getattr(data, method)
        return function(*args, **kwargs)

    def query(self, method, params=None, timeout=None):
        """Call a query method through the shared bridge without xtquant shaping."""
        return get_client().request(method, params or {}, timeout=timeout)
