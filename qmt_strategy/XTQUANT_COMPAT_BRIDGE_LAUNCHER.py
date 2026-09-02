#coding:gbk

import os
import sys

_target = os.environ.get("XTQUANT_COMPAT_BRIDGE_FILE")
if not _target:
    for _base in sys.path:
        _candidate = os.path.join(_base, "XTQUANT_COMPAT_BRIDGE.py")
        if os.path.isfile(_candidate):
            _target = _candidate
            break
if not _target or not os.path.isfile(_target):
    raise RuntimeError("XTQUANT_COMPAT_BRIDGE.py not found in QMT Python sys.path")
with open(_target, "r", encoding="utf-8") as _stream:
    _source = _stream.read()
exec(compile(_source, _target, "exec"), globals(), globals())
