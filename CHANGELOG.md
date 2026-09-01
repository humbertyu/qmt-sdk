# Changelog

## 0.1.0 - 2026-09-01

- Initial pure-file IPC protocol.
- Big QMT single-file bridge and launcher.
- MiniQMT-style quote subscription callbacks.
- `get_full_tick`, `get_market_data_ex`, instrument detail, and experimental history download.
- Daily workflow APIs for `update-instruments` and `sync-auto`: `get_market_data` and
  `get_stock_list_in_sector`, plus a longer full-market download timeout.
- Replaced an incorrect 41-function shim snapshot with the real official
  `xtquant 250516.1.1` API baseline containing 138 public functions.
- Completed the 138-function public API surface with matching names and signatures.
- Added generic ContextInfo adapters, durable whole-quote/formula event routing, and
  process-local asynchronous history-download job lifecycle compatibility.
