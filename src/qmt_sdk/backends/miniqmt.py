"""MiniQMT backend.

The initial implementation shares the same client contract. A direct native
MiniQMT transport can be added later without changing domain clients.
"""

from .qmt import QmtBackend


class MiniQmtBackend(QmtBackend):
    pass
