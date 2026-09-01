# xtquant.xtdata API implementation and compatibility

本文档是项目唯一的 API 实现与兼容性记录。README 只提供入口，不重复维护结论。
This is the single source of truth for API implementation and compatibility claims.

Reference: official `xtquant.xtdata` installed locally; distribution `250516.1.1`,
module version `xtquant_250516`, inspected on 2026-09-01.

- ✅ 在列明的样本、返回结构和字段范围内完整验证。
- ⚠️ 已通过大 QMT 端到端调用，但存在已知字段、数值或语义差异。
- 🧪 仅有公开名称、签名和通用文件适配入口，真实行为尚未验证。
- ➖ 公开名称和签名存在，但 MiniQMT 本地连接或文件语义无法原样保留。

API surface coverage and behavioral compatibility are intentionally reported separately.

## 长任务、取消与恢复协议

文件桥接对可能耗时较长的批量详情和历史数据下载统一写入
`<bridge_root>/status/<request_id>.json`。状态文件包含 `state`（`running`、
`finished`、`failed` 或 `cancelled`）、`processed`、`total`、`failed`、
`bridge_instance_id` 和时间戳。客户端可用 `xtdata.get_request_status(request_id)`
读取状态，用 `xtdata.cancel_request(request_id)` 发出协作式取消请求；取消会在每个
股票处理边界生效，底层 QMT 单只调用阻塞时无法强制中断。

普通同步 API 保持纯查询语义：不会在 `get_market_data*` 中隐式下载历史数据。
需要补齐本地缓存时必须由调用方显式调用 `download_history_data*`。桥接重启会产生新的
`bridge_instance_id`，旧请求不应继续被视为可恢复；调用方应检查实例 ID，并按业务策略
重新提交未完成任务。响应和错误文件仍按请求 ID 一一对应，处理中的文件不会被覆盖。

## 重点业务接口验收汇总

状态必须按接口和周期理解。一个接口在任一已测周期存在字段差异时，完整 API 表中的
总状态会标为 ⚠️，即使它的其他周期已经完全通过。

| API / 周期 | 当前命令 | 大 QMT 端到端 | 返回结构 | 字段与数据 | 结论 |
| --- | --- | :---: | :---: | :---: | --- |
| `get_stock_list_in_sector` | `update-instruments`, `sync-auto` | ✅ | ✅ | ⚠️ | 返回 `list[str]`；大 QMT 多 10 只较新股票。 |
| `get_instrument_detail` | `update-instruments` | ✅ | ⚠️ | ✅ | 原生 31 个字段均可提供；返回结果另有 4 个大 QMT 扩展字段。 |
| `get_market_data` / `1d` | `update-instruments` | ✅ | ✅ | ✅ | 字段字典、股票行、时间列以及样本数值通过。 |
| `download_history_data2` / `1d`, `1m`, `tick` | `sync-auto`, `sync-tick-redis` | ✅ | ⚠️ | 不适用 | 两只股票下载通过；严格原生回调/返回语义尚未完全确认。 |
| `get_market_data_ex` / `1d` | `sync-auto` | ✅ | ✅ | ✅ | 单日一根，字段、索引、dtype 和数值通过。 |
| `get_market_data_ex` / `1m` | `sync-auto` | ✅ | ✅ | ✅ | 241 根，字段、索引、dtype 和数值通过。 |
| `get_market_data_ex` / `tick` | `sync-auto`, `sync-tick-redis` | ✅ | ✅ | ⚠️ | 4915 个时间戳全部一致；4 个字段存在差异或占位值。 |
| `subscribe_quote` / `tick` | `subscribe-tick` | ✅ | ✅ | ⚠️ | `{symbol: [tick]}` 结构通过；字段全集未完全一致。 |
| `unsubscribe_quote` | `subscribe-tick` | ✅ | ⚠️ | 不适用 | 取消订阅有效；返回值语义未确认与原生完全一致。 |
| `get_full_tick` | 快照轮询 | ✅ | ✅ | ⚠️ | 时间、价格、累计量和盘口核心字段通过；字段全集待确认。 |

## `update-instruments` 全流程性能与结果记录

以下结果来自 2026-09-01、目标日期 `20260831`、相同的
`update-instruments --dry-run` 命令。两次均不写入 parquet 或 metadata。

| 后端 | 总耗时 | 行数/股票数 | `is_trading` 分布 | 备注 |
| --- | ---: | ---: | --- | --- |
| MiniQMT native | 8.90 秒 | 5207 / 5207 | `True: 5201, False: 6` | 原生客户端一次批量行情查询；详情接口官方源码虽为 Python 循环，但底层客户端调用很快。 |
| Big QMT compat（原 500 只分批） | 52.49 秒 | 5217 / 5217 | `False: 4752, True: 465` | 11 次行情桥接请求；该分批逻辑已移除。 |
| Big QMT compat（当前单次批量） | 51.92 秒 | 5217 / 5217 | `False: 4752, True: 465` | 行情一次请求约 1.75 秒，主要耗时来自详情逐只调用。 |

### 结果数量差异

Big QMT 的 `沪深A股` 列表为 5217 只，MiniQMT 为 5207 只。多出的 10 只为：

`301655.SZ`, `301688.SZ`, `301689.SZ`, `301697.SZ`, `301699.SZ`,
`601123.SH`, `688826.SH`, `688828.SH`, `688835.SH`, `688836.SH`。

这些是数据源更新时间差异导致的较新标的，不是兼容层重复、拆分或遗漏；当前策略是保留
大 QMT 返回的完整集合，不在适配层静默过滤。

### 性能原因定位

MiniQMT 官方 `get_instrument_detail_list` 的 Python 源码确实逐只调用
`get_instrument_detail`，但这些调用落在 MiniQMT 的本地客户端/服务和缓存路径上；5219 只
实测约 2.34 秒。Big QMT 侧没有等价的批量详情接口，桥接只能在策略进程内循环调用
`ContextInfo.get_instrument_detail`；5217 次调用约占 compat 全流程的 50 秒。文件桥接已
做到外部一次请求，无法消除 QMT 策略 API 每次调用本身的开销。

### 可复现命令

```powershell
python cli/cli.py update-instruments --date 20260831 --dry-run
python cli/cli.py update-instruments --date 20260831 --backend compat --dry-run
```

单独测量底层阶段时，应分别记录 `get_market_data(['amount'], 全市场, '1d', ...)` 和
`get_instrument_detail_list(全市场)` 的耗时，不能只看总流程时间。

## 已验证接口的逐字段记录

### `get_stock_list_in_sector`

| 项目 | MiniQMT | 大 QMT / 兼容层 | 差异 |
| --- | --- | --- | --- |
| 返回类型 | `list[str]` | `list[str]` | 无 |
| `沪深A股` 样本数量 | 5207 | 5217 | 大 QMT 多 10 只较新股票 |
| MiniQMT 集合覆盖 | 5207 | 5207 | MiniQMT 中的代码全部存在于大 QMT 结果 |
| 大 QMT 新增代码 | 无 | `301655.SZ`, `301688.SZ`, `301689.SZ`, `301697.SZ`, `301699.SZ`, `601123.SH`, `688826.SH`, `688828.SH`, `688835.SH`, `688836.SH` | 数据源更新时间差异，不应强行过滤 |

### `get_instrument_detail`

验证样本为 `000779.SZ`。兼容结果包含原生 MiniQMT 的全部 31 个字段。

| 字段 | 大 QMT 原始表现 | 兼容层处理 | 当前结论 |
| --- | --- | --- | --- |
| `FloatVolume` | 部分环境使用拼写 `FloatVolumn` | 映射并保留 `FloatVolume` | ✅ 与 MiniQMT 数值一致 |
| `TotalVolume` | 部分环境使用拼写 `TotalVolumn` | 映射并保留 `TotalVolume` | ✅ 与 MiniQMT 数值一致 |
| `CreateDate`, `OpenDate`, `ExpireDate`, `TradingDay` | 大 QMT 返回整数 | 规范为字符串 | ✅ 类型和值一致 |
| `SettlementPrice` | 当前大 QMT 返回空值 | 使用 `PreClose` 作为已验证股票类型的兼容值 | ✅ 当前样本一致；其他品种待验证 |
| `IsRecent`, `IsTrading` | 当前大 QMT 返回空值 | 使用 `False` | ✅ 当前股票样本一致；不能代表实时交易状态 |
| `LastVolume` | 当前大 QMT 返回空值 | 使用 `0` | ✅ 当前样本一致 |
| `LongMarginRatio`, `ShortMarginRatio` | 当前大 QMT 返回空值 | 使用 `0.0` | ✅ 当前样本一致 |
| `ContractOpenInterestQuota`, `ContractTradeQuota`, `ProductOpenInterestQuota`, `ProductTradeQuota` | 缺失 | 使用 `0` | ✅ 当前样本一致 |
| `ProductType` | 缺失 | 使用 `None` | ✅ 当前样本一致 |
| `FloatVolumn`, `TotalVolumn`, `HSGTFlag`, `RzrkCode` | 大 QMT 扩展字段 | 原样保留 | ⚠️ MiniQMT 结果没有这些额外字段 |

### `get_market_data` / `get_market_data_ex`（1d 与 1m）

验证股票为 `000779.SZ`，交易日为 `2026-08-31`。

| API / 周期 | 返回结构 | 字段 | 索引与 dtype | 数值差异 |
| --- | --- | --- | --- | --- |
| `get_market_data` / `1d` | `dict[field, DataFrame]`；股票为行、时间为列 | `amount` | 与 MiniQMT 一致 | 最大绝对差 `1.1920928955078125e-07` |
| `get_market_data_ex` / `1d` | `dict[symbol, DataFrame]`；1 行 | `open, high, low, close, volume, amount` | 字符串日期索引、列顺序和 dtype 一致 | OHLCV 精确一致；amount 最大绝对差 `1.1920928955078125e-07` |
| `get_market_data_ex` / `1m` | `dict[symbol, DataFrame]`；241 行 | `open, high, low, close, volume, amount` | 14 位字符串时间索引、列顺序和 dtype 一致 | volume 精确一致；价格最大差 `1.7763568394002505e-15`；amount 最大差 `7.450580596923828e-09` |

上述差异属于浮点表示尾差，在当前样本中没有业务数值差异。

### `get_market_data_ex`（tick）

验证股票为 `000779.SZ`，交易日为 `2026-09-01`；对照来源为现有 MiniQMT
业务链路写入的 Redis DB6。Redis 不是本项目依赖，只是外部验收基准。

| 项目 | 结果 |
| --- | --- |
| 大 QMT 历史数据 | 4915 条 |
| DB6 数据 | 4915 条 |
| 完全对应的时间戳 | 4915 / 4915 |
| 时间范围 | `09:15:00.000` 至 `15:30:00.001` |
| 15:00–15:30 | 保留，不过滤 |

| 字段 | 状态 | 具体差异 |
| --- | :---: | --- |
| `time` | ✅ | 4915 个时间戳全部精确一致。 |
| `lastPrice`, `open`, `high`, `low`, `lastClose` | ✅ | 数值一致，仅有浮点表示尾差。 |
| `volume` | ✅ | 全部精确一致。 |
| `askVol`, `bidVol` | ✅ | 全部精确一致。 |
| `askPrice`, `bidPrice` | ✅ | 数值一致，序列化浮点字符串可能不同。 |
| `transactionNum`, `openInt` | ✅ | 当前样本全部精确一致。 |
| `amount` | ⚠️ | 1716 条存在取整差异，最大绝对差 1 元。 |
| `stockStatus` | ⚠️ | 大 QMT 历史结果为 `0`；DB6 包含 `2`, `3`, `5`, `8`, `12`, `13` 等交易阶段码。 |
| `pvolume` | ⚠️ | 大 QMT 历史结果在有效交易记录中为 `0`；DB6 为累计股数。 |
| `tickvol` | ⚠️ | 大 QMT 历史结果不提供；兼容 DataFrame 的 `0` 仅为结构占位。 |
| `pe` | ⚠️ | 大 QMT 历史结果不提供；兼容 DataFrame 的 `0.0` 仅为结构占位。 |

依赖时间、核心价格、累计 `volume`、盘口或成交笔数的调用方可以继续隔离验证。
依赖 `stockStatus`, `pvolume`, `tickvol`, `pe` 的调用方不能把当前结果视为与
MiniQMT 完全等价。

### `subscribe_quote` / `unsubscribe_quote`

| 项目 | 当前实现 | 差异或限制 |
| --- | --- | --- |
| 回调外层 | `{symbol: [tick]}` | ✅ 与当前 MiniQMT 调用方式一致 |
| 行情节奏 | 盘中约 3 秒一次；收盘后订阅立即得到当前快照 | ✅ 时间戳与 DB6 对齐 |
| 事件可靠性 | 文件落盘，回调成功后移动到 processed | 至少一次投递；调用方必须按 `symbol + time` 幂等 |
| 回调字段 | 大 QMT 原始字段并增加外层结构 | ⚠️ `stime` 为额外字段；`tickvol`, `pe`, `volRatio`, `speed1Min`, `speed5Min` 等字段全集尚未与 MiniQMT 完全一致 |
| 订阅 ID | 兼容层本地整数 ID，内部保存 QMT ID | 类型兼容，但数值不等于原生 QMT ID |
| `unsubscribe_quote` 返回值 | 当前返回 `True` / `False` | ⚠️ 取消动作有效；原生返回值语义尚未完成对照 |

### `download_history_data2`

| 项目 | 当前结果 | 差异或限制 |
| --- | --- | --- |
| 大 QMT 下载 | 两只股票的 `1d`, `1m`, `tick` 均成功 | ✅ |
| 15:00 后 tick | 下载结果包含到 `15:30:00.001` | ✅ |
| 兼容回调 | 完成后调用 `callback({"finished": 1, "result": result})` | 满足当前业务只检查 `finished` 的用法 |
| MiniQMT 严格回调对照 | 原生 `download_history_data2(tick)` 探针超过 90 秒未返回且无回调，已中止 | ⚠️ 不能据此声明回调字段和时序完全等价 |
| 批量规模 | 已测 2 只股票 | 全市场负载、超时和磁盘容量尚未验证 |

### `get_full_tick`

| 项目 | 当前结论 |
| --- | --- |
| 返回外层与股票键 | ✅ 已验证 |
| `time`, `lastPrice`, `volume`, 买卖盘价格与数量 | ✅ 当前样本与 DB6 对齐 |
| `amount` | ⚠️ 存在小额取整差异 |
| 字段全集 | ⚠️ 尚未逐字段证明与 MiniQMT 完全一致 |

## 复现工具

- `tools/capture_workflow_fixture.py`：分别在 MiniQMT 与兼容环境生成标准化快照。
- `tools/compare_workflow_fixtures.py`：比较结构、索引、dtype 和记录。
- `tools/probe_subscription.py`：验证订阅回调、间隔和取消订阅。

## 完整 138 接口矩阵

<!-- GENERATED_API_MATRIX_START -->

| Official API and signature | Status | Notes |
| --- | --- | --- |
| `add_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bind_formula(request_id, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_amount_change(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_call_info(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_conversion_price(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `bnd_get_put_info(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `call_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={})` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `compute_coming_trading_calendar(market, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `connect(ip='', port=None, remember_if_success=True)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `create_array(shape, dtype_tuple, capsule, size)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `create_formula(formula_name, formula_content, formula_params={})` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `create_sector(parent_node, sector_name, overwrite=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `create_sector_folder(parent_node, folder_name, overwrite=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `datetime_to_timetag(datetime, format='%Y%m%d%H%M%S')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `del_formula(formula_name)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `disconnect()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `download_cb_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_etf_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_financial_data(stock_list, table_list=[], start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_financial_data2(stock_list, table_list=[], start_time='', end_time='', callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_his_st_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_contracts(incrementally=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_data(stock_code, period, start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_history_data2(stock_list, period, start_time='', end_time='', callback=None, incrementally=None)` | ⚠️ | Two-stock `1d`/`1m`/`tick` workflow passed; strict native callback timing/fields and full-market load remain unverified. |
| `download_holiday_data(incrementally=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_index_weight()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_metatable_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_sector_data()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `download_tabular_data(stock_list, period, start_time='', end_time='', incrementally=None, download_type='validationbypage', source='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `fetch_quote_server_from_config(root_path, key_list)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `gen_factor_index(data_name, formula_name, vars, sector_list, start_time='', end_time='', period='1d', dividend_type='none')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `generate_index_data(formula_name, formula_param={}, stock_list=[], period='1d', dividend_type='none', start_time='', end_time='', fill_mode='fixed', fill_value=nan, result_path=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `getDividFactors(*args, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_kline_trading_periods()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_sub_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_all_trading_periods()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_authorized_market_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_broker_queue_data(stock_list=[], start_time='', end_time='', count=-1, show_broker_name=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_cb_info(stockcode)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_client()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_current_connect_sub_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_data_dir()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_divid_factors(stock_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_etf_info()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_field_list(metaid)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_financial_data(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_financial_data_ori(stock_list, table_list=[], start_time='', end_time='', report_type='report_time')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_formula_result(request_id, start_time='', end_time='', count=-1, timeout_second=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_formulas()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_full_kline(field_list=[], stock_list=[], period='1m', start_time='', end_time='', count=1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_full_tick(code_list)` | ⚠️ | Core quote fields verified against the current three-second feed; complete field parity remains pending. |
| `get_fullspeed_orderbook(code_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_option_list(undl_code, dedate)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_option_list_batch(undl_code, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_his_st_data(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_hk_broker_dict()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_holidays()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_index_weight(index_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_instrument_detail(stock_code, iscomplete=False)` | ⚠️ | All 31 native fields passed for one stock; the result retains four Big QMT-only fields and other instrument types remain pending. |
| `get_instrument_detail_list(stock_list, iscomplete=False)` | ⚠️ | Batch shape verified for 2/50/500 stocks and full 5217-stock workflow; fields are normalized per item. Big QMT internally performs one-by-one detail calls and is materially slower than MiniQMT. |
| `get_instrument_type(stock_code, variety_list=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_ipo_info(start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_kline_trading_period(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_order(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_quote(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2_transaction(field_list=[], stock_code='', start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_l2thousand_queue(stock_code, gear_num=None, price=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_local_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, data_dir=None)` | 🧪 | `data_dir` cannot retain its MiniQMT-local cache meaning. |
| `get_main_contract(code_market: str, start_time: str = '', end_time: str = '')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ✅ | Native field-keyed, stock-by-timetag DataFrame orientation and one-day values verified. |
| `get_market_data3(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data_ex(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | ⚠️ | `1d`/`1m` passed; Tick structure and core data match but `stockStatus`, `pvolume`, `tickvol`, and `pe` differ or use placeholders. |
| `get_market_data_ex_ori(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_data_ori(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_market_last_trade_date(market)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_markets()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_config(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_fields(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_info(table)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_metatable_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_detail_data(optioncode)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_list(undl_code, dedate, opttype='', isavailavle=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_option_undl_data(undl_code_ref)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_order_rank(code, order_time, order_type, order_price, order_volume, order_left_volume)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_period_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_quote_server_config()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_quote_server_status()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `get_sec_main_contract(code_market: str, start_time: str = '', end_time: str = '')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_sector_info(sector_name='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_sector_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_stock_list_in_sector(sector_name, real_timetag=-1)` | ⚠️ | Shape verified. Tested Big QMT universe contained all MiniQMT symbols plus 10 newer symbols. |
| `get_stock_type(stock_code, variety_list=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_bson(codes: list, fields: list, period: str, start_time: str, end_time: str, count: int = -1, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_data(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_tabular_formula(codes: list, fields: list, period: str, start_time: str, end_time: str, count: int = -1, dividend_type='none', **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_calendar(market, start_time='', end_time='')` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_contract_list(stockcode, date=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_dates(market, start_time='', end_time='', count=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_trading_period(stock_code)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_transactioncount(code_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `get_wp_market_list()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gld(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, data_dir=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd2(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gmd3(field_list=[], stock_list=[], period='1d', start_time='', end_time='', count=-1, dividend_type='none', fill_data=True, enable_read_from_server=True)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `gsl(sector_name, real_timetag=-1)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `hello()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `import_formula(formula_name, file_path)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `is_stock_type(stock, tag)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `push_custom_data(meta, datas, coverall=False)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `read_feather(file_path)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `reconnect(ip='', port=None, remember_if_success=True)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `remove_sector(sector_name)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `remove_stock_from_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_market_stock_list(market, datas)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_market_trading_day_list(market, datas)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `reset_sector(sector_name, stock_list)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `run()` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `show_quote_server_status()` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper(callback)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper_1820(callback)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_callback_wrapper_convert(callback, metaid)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_formula(formula_name, stock_code, period, start_time='', end_time='', count=-1, dividend_type=None, extend_param={}, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_l2thousand(stock_code, gear_num=None, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_l2thousand_queue(stock_code, callback=None, gear_num=None, price=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_quote(stock_code, period='1d', start_time='', end_time='', count=0, callback=None)` | ⚠️ | Callback envelope and timestamps verified; complete callback field parity and native sequence identity differ or remain pending. |
| `subscribe_quote2(stock_code, period='1d', start_time='', end_time='', count=0, dividend_type=None, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `subscribe_whole_quote(code_list, callback=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `supply_history_data(stock_code, period, start_time='', end_time='', incrementally=None)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `t2d(timetag, format)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `timetagToDateTime(*args, **kwargs)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `timetag_to_datetime(timetag, format)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `try_except(func)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `unsubscribe_formula(request_id)` | 🧪 | Environment-dependent adapter; real-QMT verification pending. |
| `unsubscribe_quote(seq)` | ⚠️ | Real Big QMT unsubscribe action verified; native return-value semantics remain pending. |
| `watch_quote_server_status(callback)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `watch_xtquant_status(callback)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |
| `write_feather(dest_path, param, df)` | ➖ | Environment-dependent adapter; real-QMT verification pending. |

### Totals

| Metric | Count |
| --- | ---: |
| Public names and signatures | 138 / 138 |
| ✅ Fully verified for the tested scope | 1 |
| ⚠️ Operational with known differences | 7 |
| 🧪 Verification pending | 116 |
| ➖ Different local semantics | 14 |

<!-- GENERATED_API_MATRIX_END -->
