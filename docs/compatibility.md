# xtdata compatibility

The project targets behavioral compatibility for explicitly listed APIs, not a claim of
complete compatibility with every `xtquant` release.

## Known differences

- Import path is `from xtquant_compat import xtdata`; it does not shadow `xtquant`.
- Big QMT subscription callbacks use column arrays internally. The bridge expands them
  to the common `{stock_code: [tick]}` callback shape.
- `get_market_data_ex` is converted to stock-keyed pandas DataFrames externally.
- Big QMT may round cumulative `amount` differently from MiniQMT by small absolute
  amounts while `time`, `lastPrice`, and cumulative `volume` agree.
- `download_history_data2` currently runs QMT's single-symbol downloader sequentially.
- Connection-management and QMT local-cache path APIs are intentionally unsupported.

## Verified environment

- Big QMT bundled Python 3.6 with no `_socket`, `_ctypes`, pandas, or importlib.
- `000779.SZ` subscription cadence and timestamp compared with a MiniQMT DB6 feed.
- `get_full_tick`, daily/minute `get_market_data_ex`, and instrument details.
