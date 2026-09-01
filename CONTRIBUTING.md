# Contributing

Keep QMT-side code compatible with its bundled Python 3.6 and standard library. Do not
add socket, ctypes, pandas, Redis, ZeroMQ, or vendor package dependencies to the QMT
strategy. New compatibility claims require a fixture test and a real-QMT validation note.

Run checks with:

```powershell
python -m pytest
ruff check .
```
