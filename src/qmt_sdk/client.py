"""High-level QMT client facade backed by the existing bridge client."""

from .financial import FinancialClient
from .instruments import InstrumentClient
from .jobs import JobClient
from .market import MarketClient


class QmtClient:
    """Unified domain-oriented client.

    ``backend`` is reserved for future direct MiniQMT/QMT selection; the
    current implementation uses the configured file bridge for both.
    """

    def __init__(self, backend="auto"):
        self.backend = backend
        self.market = MarketClient()
        self.financial = FinancialClient()
        self.instruments = InstrumentClient()
        self.jobs = JobClient()

