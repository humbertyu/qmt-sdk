# QMT capability map

This document tracks the query capabilities available from the QMT runtime,
independently of the MiniQMT compatibility matrix.

| Capability area | Examples | qmt_sdk layer | Status |
| --- | --- | --- | --- |
| Market data | `get_market_data`, `get_market_data_ex`, `get_full_tick`, local data | `client.market` | Core verified |
| Live subscriptions | quote/tick subscription, events, unsubscribe | `client.market` | Core verified |
| Instruments and metadata | instrument detail, sectors, type, markets, IPO/ETF info | `client.instruments` | Partly verified |
| Financial data | financial table read, raw financial payload | `client.financial` | Structure verified; values depend on data availability |
| Historical downloads | K-line/tick download and status | `client.market` / `client.jobs` | Existing bridge support |
| Calendar | trading dates, holidays, calendar | `client.instruments` | Environment-dependent |
| Derivatives and special data | options, contracts, index weights, L2 query | domain clients via `QmtClient.query` first | Not uniformly normalized |
| Formula and factor queries | formula result, factor data, ranking data | domain clients via `QmtClient.query` first | Extension stage |
| Task control | status, cancellation, bridge status | `client.jobs` | Core verified |

## Official QMT data-function baseline

The official QMT data-function page lists 42 query/data-function entries. They
are grouped below as the initial QMT-native scope; this list is independent of
the MiniQMT compatibility matrix.

| Group | Official functions |
| --- | --- |
| Market and subscriptions (22) | `download_history_data`, `ContextInfo.get_market_data_ex`, `ContextInfo.get_full_tick`, `ContextInfo.subscribe_quote`, `ContextInfo.subscribe_whole_quote`, `ContextInfo.unsubscribe_quote`, `subscribe_formula`, `unsubscribe_formula`, `call_formula`, `call_formula_batch`, `ContextInfo.get_svol`, `ContextInfo.get_bvol`, `ContextInfo.get_turnover_rate`, `ContextInfo.get_longhubang`, `ContextInfo.get_north_finance_change`, `ContextInfo.get_hkt_details`, `ContextInfo.get_hkt_statistics`, `get_etf_info`, `get_etf_iopv`, `ContextInfo.get_local_data`, `ContextInfo.get_history_data`, `ContextInfo.get_market_data` |
| Financial (4) | `ContextInfo.get_financial_data`, `ContextInfo.get_raw_financial_data`, `ContextInfo.get_last_volume`, `ContextInfo.get_total_share` |
| Instruments and contracts (7) | `ContextInfo.get_instrument_detail`, `get_st_status`, `ContextInfo.get_his_st_data`, `ContextInfo.get_main_contract`, `ContextInfo.get_contract_multiplier`, `ContextInfo.get_contract_expire_date`, `ContextInfo.get_his_contract_list` |
| Options (5) | `ContextInfo.get_option_detail_data`, `ContextInfo.get_option_list`, `ContextInfo.get_option_undl_data`, `ContextInfo.bsm_price`, `ContextInfo.bsm_iv` |
| Corporate actions and index (2) | `ContextInfo.get_divid_factors`, `ContextInfo.get_weight_in_index` |
| Constituents and calendar (2) | `ContextInfo.get_stock_list_in_sector`, `ContextInfo.get_trading_dates` |

The page also documents data dictionaries and field tables; those are schemas,
not additional callable APIs. Each function will first be exposed through
`QmtClient.query()` and then promoted to a typed domain method after runtime
verification.

## Integration rule

Every new QMT query starts as a bridge method available through:

```python
client.query("method_name", {"parameter": value})
```

After signature, return structure, error behavior, and performance are
validated, it becomes a typed method in the appropriate domain client. It is
added to `xtquant_compat` only if a MiniQMT equivalent exists. This prevents
QMT-only features from being distorted by compatibility requirements.

## Native query acceptance checklist

The bridge accepts documented QMT keyword names and positional arguments for
the official functions below. Runtime availability and whether a result is
non-empty still depend on QMT version, local data, permissions, and instrument.

| Function group | Dispatch | Acceptance notes |
| --- | --- | --- |
| Market, history, local data | ✅ | Native parameter order is mapped; `get_full_tick` is latest snapshot only. |
| Quote/formula subscriptions | ✅ | Subscribe/unsubscribe and file-delivered callbacks are implemented. |
| Scalar market queries (`get_svol`, `get_bvol`, turnover, ETF, northbound/HK) | ✅ | Scalar samples verified where data existed; turnover wrapper may require pandas. |
| Financial (`get_financial_data`, raw) | ✅ | Field-list/stock-list order preserved; raw/turnover official wrappers may require pandas. |
| Instruments, contracts, options | ✅ | Signatures mapped; values depend on the local universe and permissions. |
| Corporate actions, index weights, sectors, calendar | ✅ | Official parameter aliases mapped; empty results are runtime/data conditions. |
| Formula calculation (`bsm_price`, `bsm_iv`, formula calls) | ✅ | Calculation samples verified; formula APIs require configured formulas. |

For each acceptance run record QMT version, exact parameters, elapsed time,
result type, row/count information, and exception text. An empty result is not
treated as an implementation failure. New functions must be added to this map
and to the automated probe before being promoted to a typed domain method.
