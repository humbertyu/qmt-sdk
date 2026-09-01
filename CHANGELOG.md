# Changelog

## 0.1.0 - 2026-09-01

- Initial pure-file IPC protocol.
- Big QMT single-file bridge and launcher.
- MiniQMT-style quote subscription callbacks.
- `get_full_tick`, `get_market_data_ex`, instrument detail, and experimental history download.
- Daily workflow APIs for `update-instruments` and `sync-auto`: `get_market_data` and
  `get_stock_list_in_sector`, plus a longer full-market download timeout.
- Added a 41-function compatibility matrix generated from an installed official
  `xtquant.xtdata` API snapshot.
- Completed the 41-function public API surface with matching names and signatures.
- Added generic ContextInfo adapters, durable whole-quote/formula event routing, and
  process-local asynchronous history-download job lifecycle compatibility.
