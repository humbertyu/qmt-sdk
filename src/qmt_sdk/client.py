"""High-level QMT client facade backed by the existing bridge client."""

from .backends import MiniQmtBackend, QmtBackend
from .financial import FinancialClient
from .instruments import InstrumentClient
from .jobs import JobClient
from .market import MarketClient


class QmtClient:
    """Unified domain-oriented client.

    ``backend`` is reserved for future direct MiniQMT/QMT selection; the
    current implementation uses the configured file bridge for both.
    """

    def __init__(self, backend="qmt"):
        if hasattr(backend, "call"):
            self.backend_name = "custom"
            self.backend = backend
        elif backend in ("qmt", "auto"):
            self.backend_name = "qmt"
            self.backend = QmtBackend()
        elif backend in ("mini", "miniqmt"):
            self.backend_name = "miniqmt"
            self.backend = MiniQmtBackend()
        else:
            raise ValueError("unsupported backend: %s" % backend)
        self.market = MarketClient(self.backend)
        self.financial = FinancialClient(self.backend)
        self.instruments = InstrumentClient(self.backend)
        self.jobs = JobClient(self.backend)
