"""MiniQMT compatibility facade over the shared qmt_sdk bridge client."""

from qmt_sdk.bridge.client import FileBridgeClient
from qmt_sdk.bridge.client import get_client as _get_client
from qmt_sdk.bridge.client import reset_client as _reset_client


def get_client():
    return _get_client()


def reset_client():
    return _reset_client()


__all__ = ["FileBridgeClient", "get_client", "reset_client"]
