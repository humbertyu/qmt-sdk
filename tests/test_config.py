from xtquant_compat.config import Config


def test_default_root_is_isolated_from_legacy_bridge(monkeypatch):
    monkeypatch.delenv("XTQUANT_COMPAT_ROOT", raising=False)
    assert Config().root == r"D:\FinTools\QMT\xtquant_compat_bridge"
