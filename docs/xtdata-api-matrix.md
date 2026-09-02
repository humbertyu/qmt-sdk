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

## 实际调用优先适配清单

以下清单来自对一个典型数据同步/实时服务调用面的静态扫描。它只表示外部调用方实际
使用过的 XtData API，不改变兼容库的 API 范围；已完成的接口仍以本文前面的验收章节和
下方完整矩阵为准。

| API | 使用场景 | 当前状态 | 下一步验收重点 |
| --- | --- | --- | --- |
| `get_stock_list_in_sector` | 获取股票池、订阅池 | ⚠️ 已适配并验收 | 不同板块、顺序和跨重启稳定性 |
| `get_instrument_detail` | 股票属性、上市日期 | ⚠️ 已适配并验收 | 其他证券类型和实时状态字段 |
| `get_instrument_detail_list` | 批量股票属性 | ⚠️ 已适配并验收 | 长任务性能和取消恢复 |
| `get_market_data` | 日线成交额/属性判断 | ⚠️ 已适配并验收 | 缓存缺失时的 `fill_data` 语义 |
| `get_market_data_ex` | 1d、1m、tick 历史/盘中读取 | ⚠️ 已适配并验收 | tick 个别字段和异常重试 |
| `download_history_data` | 单股票历史补数 | ⚠️ 已适配 | 返回值、增量参数和错误语义 |
| `download_history_data2` | 1d、1m、tick 批量补数 | ⚠️ 已适配并验收 | 逐股票进度 callback 和长任务恢复 |
| `subscribe_quote` | 实时 tick/1m 推送 | ⚠️ 已适配并验收 | 字段全集、断线重连和事件积压 |
| `unsubscribe_quote` | 取消实时订阅 | ✅ 返回值已统一 | 重复取消和桥接重启后的行为 |
| `get_trading_calendar` | 交易日历同步 | ➖ 接口已适配但当前 QMT 环境不可用 | MiniQMT 与 Big QMT 均未提供可调用实现 |
| `get_financial_data` | 财务表查询 | 🧪 已有适配入口，未完成真实验收 | 返回层级、字段 dtype、无数据年度和分批读取 |
| `download_financial_data2` | 财务数据下载 | 🧪 已有适配入口，未完成真实验收 | 下载完成回调、返回值和下载后读取 |

下一阶段优先处理后三个尚未完成真实验收的 API；其余已标记为 ⚠️ 的行情接口主要进入
异常、重连和字段补齐阶段，不再重复实现另一套调用方式。

## 长任务、取消与恢复协议

文件桥接对可能耗时较长的批量详情和历史数据下载统一写入
`<bridge_root>/status/<request_id>.json`。状态文件包含 `state`（`running`、
`finished`、`failed`、`cancelled` 或 `abandoned`）、`processed`、`total`、`failed`、
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

| API / 周期 | 验收类型 | 大 QMT 端到端 | 返回结构 | 字段与数据 | 结论 |
| --- | --- | :---: | :---: | :---: | --- |
| `get_stock_list_in_sector` | Python API probe | ✅ | ✅ | ⚠️ | 返回 `list[str]`；大 QMT 多 10 只较新股票。 |
| `get_instrument_detail` | Python API probe | ✅ | ⚠️ | ✅ | 原生 31 个字段均可提供；返回结果另有 4 个大 QMT 扩展字段。 |
| `get_market_data` / `1d` | Python API probe | ✅ | ✅ | ✅ | 字段字典、股票行、时间列以及样本数值通过。 |
| `download_history_data2` / `1d`, `1m`, `tick` | 独立行为验收 | ✅ | ⚠️ | 不适用 | 下载链路通过；返回值已统一为 `{}`，逐股票进度回调时序仍未完全等价。 |
| `get_market_data_ex` / `1d` | Python API probe | ✅ | ✅ | ✅ | 单日一根，字段、索引、dtype 和数值通过。 |
| `get_market_data_ex` / `1m` | Python API probe | ✅ | ✅ | ✅ | 241 根，字段、索引、dtype 和数值通过。 |
| `get_market_data_ex` / `tick` | 独立行为验收 | ✅ | ✅ | ⚠️ | 4915 个时间戳全部一致；4 个字段存在差异或占位值。 |
| `subscribe_quote` / `tick` | 独立行为验收 | ✅ | ✅ | ⚠️ | `{symbol: [tick]}` 结构通过；字段全集未完全一致。 |
| `unsubscribe_quote` | 独立行为验收 | ✅ | ⚠️ | 不适用 | 取消订阅有效；返回值语义未确认与原生完全一致。 |
| `get_full_tick` | Python API probe | ✅ | ✅ | ⚠️ | 时间、价格、累计量和盘口核心字段通过；字段全集待确认。 |

## 已验证接口的逐字段记录

### `get_stock_list_in_sector`

| 项目 | MiniQMT | 大 QMT / 兼容层 | 差异 |
| --- | --- | --- | --- |
| 返回类型 | `list[str]` | `list[str]` | 无 |
| `沪深A股` 样本数量 | 5207 | 5217 | 大 QMT 多 10 只较新股票 |
| MiniQMT 集合覆盖 | 5207 | 5207 | MiniQMT 中的代码全部存在于大 QMT 结果 |
| 大 QMT 新增代码 | 无 | `301655.SZ`, `301688.SZ`, `301689.SZ`, `301697.SZ`, `301699.SZ`, `601123.SH`, `688826.SH`, `688828.SH`, `688835.SH`, `688836.SH` | 数据源更新时间差异，不应强行过滤 |

边界验收（2026-09-01）：空 sector 和未知 sector 均返回空 `list`；`沪深A股` 返回 5217
项且无重复，首尾顺序稳定于本次运行。其他板块名称和跨重启顺序尚未承诺。

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

### `get_instrument_detail_list`

该接口保持 MiniQMT 的公开签名和返回结构：一次调用返回
`dict[stock_code, detail_dict]`。兼容层通过一次文件请求把股票列表交给桥接；桥接内部
逐只调用 Big QMT 的 `ContextInfo.get_instrument_detail`，并对每个结果应用与单只接口
相同的字段规范化。

| 股票数量 | 返回数量 | 实测耗时 | 结论 |
| ---: | ---: | ---: | --- |
| 2 | 2 | 约 0.23 秒 | ✅ |
| 50 | 50 | 约 0.53 秒 | ✅ |
| 500 | 500 | 约 4.44 秒 | ✅ |
| 5217 | 5217 | 约 50 秒 | ✅ 结构和数量完整；⚠️ 性能明显慢于 MiniQMT |

MiniQMT 官方实现的 Python 源码同样是逐只循环，但 5219 只实测约 2.34 秒；Big QMT
每次详情调用都经过策略运行时，因此不能仅依据源码中的循环形式推断性能相同。该差异
属于底层 QMT 能力差异，不是文件桥接重复发送请求。

#### 标准 API 验收记录（2026-09-01）

| 验收项 | 结果 |
| --- | --- |
| 签名 | `get_instrument_detail_list(stock_list, iscomplete=False)`，与 MiniQMT 一致 |
| 空列表 | 返回 `{}`，不产生 QMT 调用 |
| 单项调用 | `000779.SZ` 返回 1 项，约 0.109 秒 |
| 两项调用 | `000779.SZ`, `000001.SZ` 返回 2 项，约 0.174 秒 |
| 返回类型 | `dict[str, dict]`；每个详情均经过单项接口相同的别名、默认值和日期规范化 |
| 字段 | MiniQMT 31 个基础字段均存在；Big QMT 扩展字段原样保留，详见单项字段表 |
| 状态协议 | 每个请求生成 status 文件；完成后为 `finished`，包含 request ID、实例 ID、处理数和总数 |
| 重启语义 | 本次重启后实例 ID 为 `5f2b8d66dbb646299b1ebeffec3f108b`；旧的 pending/running 请求会标记为 `abandoned` |
| 性能对照 | MiniQMT 单项约 0.018 秒；compat 单项约 0.109 秒；全市场差异主要来自 Big QMT 宿主 API 调用成本 |

取消专项验收（重启后实例 `d41c500b7d204cedbd97cd55e324c2ac`）：提交 5219 只长任务，
在 `running` 且已处理 2 只时取消；客户端收到 `BridgeCancelledError`，最终状态为
`cancelled`，处理中的文件数为 0。该结果证明取消、错误分类和清理语义均已生效。

本记录覆盖了标准文档要求的签名、正常路径、边界输入、结构规范化、对照性能和任务状态。
取消/超时需要在真实长任务运行期间另行验收，不能用短请求推断。

### `get_trading_calendar`

兼容层已提供 `get_trading_calendar(market, start_time='', end_time='')`，桥接端优先调用
大 QMT 的三参数形式；若当前 QMT 构建仍保留历史的第四个 `tradetimes` 参数，则以
`False` 回退调用。该接口目前已完成调用适配，尚未完成真实环境的历史范围、未来日期、
市场代码和空结果对照，验收完成前不标记为完全通过。

#### 运行时能力验收（2026-09-02）

对 `SH`/`SZ` 历史范围、未来范围、空日期参数和未知市场分别调用。MiniQMT 对有效市场
统一返回 `function not realize (ErrorID 300000)`；Big QMT 当前策略运行时未暴露
`get_trading_calendar` callable，兼容层返回 `BridgeMethodNotSupportedError`。因此目前
无法进行 native/compat 数据列表对照，也不能使用该接口生成交易日历；调用方需使用已有
本地日历或其他已验证来源。这是 QMT 运行时能力限制，不是参数映射问题。

### `get_market_data` / `1d`

返回结构为 `dict[field, DataFrame]`，股票为行、时间为列；`amount` 字段的结构、索引和
样本数值已与 MiniQMT 对照通过，浮点尾差最大约 `1.19e-7`。

### `get_market_data_ex` / `1d` 与 `1m`

验证股票为 `000779.SZ`，交易日为 `2026-08-31`。

| API / 周期 | 返回结构 | 字段 | 索引与 dtype | 数值差异 |
| --- | --- | --- | --- | --- |
| `get_market_data` / `1d` | `dict[field, DataFrame]`；股票为行、时间为列 | `amount` | 与 MiniQMT 一致 | 最大绝对差 `1.1920928955078125e-07` |
| `get_market_data_ex` / `1d` | `dict[symbol, DataFrame]`；1 行 | `open, high, low, close, volume, amount` | 字符串日期索引、列顺序和 dtype 一致 | OHLCV 精确一致；amount 最大绝对差 `1.1920928955078125e-07` |
| `get_market_data_ex` / `1m` | `dict[symbol, DataFrame]`；241 行 | `open, high, low, close, volume, amount` | 14 位字符串时间索引、列顺序和 dtype 一致 | volume 精确一致；价格最大差 `1.7763568394002505e-15`；amount 最大差 `7.450580596923828e-09` |

2026-09-01 通过 `tools/capture_workflow_fixture.py` 分别在 MiniQMT 和 compat 环境采集
`000779.SZ`、`20260901`，再用 `tools/compare_workflow_fixtures.py` 对照。两周期的外层
股票键、行数、列名、索引和 dtype 均一致；逐字段记录显示仅存在浮点序列化尾差。

上述差异属于浮点表示尾差，在当前样本中没有业务数值差异。

#### 批量与边界验收（`get_market_data`）

2026-09-01 使用 `amount`、`1d`、`20260831` 验证：2 只返回形状 `(2, 1)`，全市场 5217
只返回 `(5217, 1)`，一次请求约 2.26 秒；空股票列表、无数据日期和 `count=1` 均正常
返回字段字典，不抛异常。Big QMT 默认 `fill_data=True` 会把不可见历史补成 0；同请求
使用 `fill_data=False` 只返回 465 个有数据股票。接口结构和调用语义通过，但数据完整性
依赖 Big QMT 目标日期缓存，不能假定与 MiniQMT 自动一致。

#### 对 `update-instruments` 的迁移结论

兼容库层面的两个 API 已满足调用和结构要求，但不能仅凭此宣布业务迁移完成。使用相同
目标日期 `20260831` 的全市场结果中，MiniQMT 的 `amount` 推导交易状态为
`True: 5201, False: 6`，Big QMT 在默认 `fill_data=True` 下为 `True: 465, False: 4752`。
进一步使用 `fill_data=False` 时，Big QMT 只返回 465 行，且全部为正成交额；其余股票
并非返回 `NaN`，而是目标日期历史数据在 Big QMT 本地缓存中不可见，`fill_data=True`
将缺失项补成 0。这不是 `is_trading` 判断代码或字段映射错误，而是两个 QMT 实例的历史
缓存/数据可见范围不同；若直接迁移，`is_trading` 等业务字段会发生实质错误。

结论：`update-instruments` 当前具备“技术链路可迁移、可做只读 dry-run”的条件，尚不具备
“结果无需复核即可替换 MiniQMT 生产流程”的条件。必须先解决或明确补齐 Big QMT 目标日
全市场历史数据，再进行最终迁移验收。

#### 全市场 1d 批量、落盘与生产文件对照（2026-09-01）

这是对 `download_history_data2` + `get_market_data_ex` 的独立外部验收，不会调用或覆盖
任何生产数据目录。测试严格复现常见调用方的 1000 只/批边界；批处理仍属于调用方，
兼容库只负责处理一个批次。工具为 `tools/probe_sync_1d_batches.py`，每只股票单独保存
为生产格式的 Parquet，并在每批完成后更新 `manifest.json`。输出根目录示例：
`D:\\Temp\\xtquant-sync-1d-probe\\20260901\\{native,compat}`。

| 验收项 | MiniQMT native | Big QMT compat | 结论 |
| --- | ---: | ---: | --- |
| 统一股票列表 | 5207 | 5207 | ✅ compat 使用 native 保存的 `stocks.json`，排除股票池差异 |
| 批次数 / 批大小 | 6 / 1000 | 6 / 1000 | ✅ 调用顺序和业务批次一致 |
| 成功返回并落盘 | 5207 / 5207 | 5207 / 5207 | ✅ 每只股票均生成独立 Parquet |
| 总耗时（下载+查询+保存及批次间隔） | 631.5 秒 | 402.8 秒 | ⚠️ Big QMT 本次更快，但耗时受本地缓存状态影响 |
| Parquet 保存累计耗时 | 19.2 秒 | 19.8 秒 | ✅ 已单独计时并写入 manifest |
| 与生产 20260901 行覆盖 | 5207 / 5207 | 5207 / 5207 | ✅ 无缺失文件或缺失日期行 |
| 与生产 OHLCV | 5091 只四舍五入后一致 | 与 native 核心值一致 | ✅ 价格和 volume 仅有浮点表示尾差 |
| 与生产 `amount` | 最大绝对差约 1 | 最大绝对差约 51 | ⚠️ Big QMT 存在系统性取整/量化差异 |

文件级对照显示，compat 的结构、日期索引、字段集合和覆盖范围均满足 1d 读取要求；
但 `amount` 不能宣称与 MiniQMT/生产数据完全等价。典型样本 `300712.SZ`：compat
返回 `27727800.0`，生产文件为 `27727749.0`，差异约 51。该差异发生在 Big QMT
底层数据返回层，不是 Parquet 保存造成的（native 保存文件与生产值最大仅差约 1）。
因此本验收支持“接口链路和文件落盘可迁移”，不支持在未定义 `amount` 取整容差前直接
替换依赖精确成交额的生产逻辑。

#### 全市场 1m 批量、落盘与生产文件对照（2026-09-01）

使用同一工具将周期切换为 `1m`，仍采用 1000 只/批，并使用 native 生成的
`stocks.json` 作为 compat 输入。两边结果分别写入
`D:\\Temp\\xtquant-sync-1m-probe\\20260901\\native` 和 `compat`，不触碰生产文件。

| 验收项 | MiniQMT native | Big QMT compat | 结论 |
| --- | ---: | ---: | --- |
| 股票数 / 成功保存 | 5207 / 5207 | 5207 / 5207 | ✅ 覆盖完整 |
| 批次数 / 批大小 | 6 / 1000 | 6 / 1000 | ✅ 与业务批次一致 |
| 返回分钟线总数 | 1,254,887 | 1,254,887 | ✅ 每只股票 241 根（末批按实际交易数据） |
| 总耗时（下载+查询+保存及批次间隔） | 457.3 秒 | 286.7 秒 | ⚠️ 本次 compat 更快，受缓存状态影响 |
| Parquet 保存累计耗时 | 27.8 秒 | 22.5 秒 | ✅ 已单独计时并写入 manifest |
| 与生产 1m 文件覆盖 / 形状 | 5207 / 5207 | 5207 / 5207 | ✅ 行数、时间索引和字段列一致 |
| native vs compat 最大绝对差 | — | 价格约 `4.55e-13`，amount 约 `1.19e-7` | ✅ 仅浮点表示尾差，volume 精确一致 |
| 与生产最大绝对差 | 0 | 价格约 `4.55e-13`，amount 约 `1.19e-7` | ✅ compat 1m 与生产数值一致（浮点尾差范围） |

结论：在 20260901 全市场样本上，`1m` 的下载、查询、独立 Parquet 落盘和生产文件
对照均通过；未发现 1d 中出现的 `amount` 系统性差异。该结论仅覆盖本次日期、股票池和
字段集合，后续日期仍需抽样复验。

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

同一 fixture 验收确认：两边 tick DataFrame 均为 `(4915, 20)`，20 列顺序和 dtype 完全
一致，索引时间戳一致；逐记录 JSON 比较为 `false` 主要来自已知浮点表示差异及上述字段
差异，而不是行数或时间错位。

#### 大结果二进制传输优化验收（2026-09-02）

原文件桥接会将 tick 数组递归转换为 JSON 列表，再由客户端重建 DataFrame。现对
`get_market_data_ex` 增加 Pickle protocol 4 二进制 sidecar；外部 API 和同步阻塞语义不变，
JSON 仍作为写入失败时的回退格式。50 只、`20260901` 的生产 tick 批次对照如下：

| 阶段 | MiniQMT native | compat（二进制） |
| --- | ---: | ---: |
| 下载 | 2.673 秒 | 9.721 秒 |
| `get_market_data_ex` 查询 | 6.327 秒 | 5.766 秒 |
| Parquet 保存 | 1.717 秒 | 1.547 秒 |
| 返回/保存股票数 | 50 / 50 | 50 / 50 |
| 返回 tick 行数 | 220073 | 220072 |

查询耗时由优化前约 18–20 秒降至约 5.8 秒，已接近 native；保存后的字段集合和核心
数值保持一致，`600127.SH` 仅发现 native 多 1 条重复时间记录。响应目录测试后无残留
`.pkl` 文件。当前剩余主要差异在下载阶段：Big QMT 未暴露真正的批量下载函数，桥接仍需
逐只调用 `down_history_data`；该问题与传输格式无关。

#### 全量 tick 首轮缺失股票复核（2026-09-02）

首轮全市场批量测试中 compat 比 native 少保存 17 只股票。对这 17 只股票改为单独一批
重试（仍执行“下载 → `get_market_data_ex([], ..., 'tick', ...)` → Parquet 落盘”），全部
成功：17/17，共 67474 条 tick。与 native 文件逐股票按 `time` 对照后，17 只均为相同的
时间戳集合和相同的行数；`lastPrice/open/high/low/volume/amount` 最大差异均为浮点表示
尾差（amount 最大约 `2.38e-7`），没有真实数值差异。

因此首轮缺失不是这些股票没有 20260901 tick，也不是字段映射问题，而是 50 只批量请求
中的偶发漏返回/运行时不稳定。补偿机制应由外部调用方负责：调用方根据自己的股票池和
本地数据文件执行“批次返回数量校验 + 缺失股票单只重试”。兼容库只负责实现
MiniQMT API 的返回语义，不知道某个股票在业务上是否应该有数据，也不能把空结果一律
判定为错误；不能仅凭批量 API 返回成功就让业务层认为全量完成。

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

2026-09-01 重启后的 Big QMT 能力探测结果：`download_history_data2` 未暴露，
`download_history_data` 与 `down_history_data` 可用。因此 compat 的批量下载只能在桥接
内部逐只回退，不能声称使用了 Big QMT 原生批量下载接口。

#### 返回值与完成回调语义验收（2026-09-02）

MiniQMT 实测单股票 `1d` 下载完成后返回空字典 `{}`；完成回调为进度字典，不包含逐股票
布尔结果。兼容层已将 Big QMT 逐只 `down_history_data` 的结果隐藏，统一返回 `{}`，并在
同步请求完成后调用一次：

```python
{"finished": total, "total": total, "stockcode": "", "message": ""}
```

这保证了“下载后再查询”的调用方不会因返回值结构变化而分支。当前文件桥接尚未提供
MiniQMT 那种每只股票完成时实时触发一次 callback 的进度事件；依赖逐股票进度展示或
中途处理的调用方仍需单独验收。下载是否真正产生目标数据，应通过后续
`get_market_data_ex` 读取结果确认。

### `download_history_data`

这是 MiniQMT 的单股票入口，兼容层保持同名签名，并委托到批量入口；QMT 桥接内部再将
每只股票映射为 `down_history_data(stock, period, start_time, end_time)`。因此调用方不需要
知道 Big QMT 没有同名 `xtdata.download_history_data`。

#### 单股票联动验收（`000779.SZ`，20260901）

| 周期 | MiniQMT 总耗时 | compat 总耗时 | 下载后行数 | 数据读取 |
| --- | ---: | ---: | ---: | --- |
| `1d` | 0.962 秒 | 0.437 秒 | 1 | ✅ `get_market_data_ex` 可读 |
| `1m` | 0.146 秒 | 0.175 秒 | 241 | ✅ `get_market_data_ex` 可读 |
| `tick` | 0.637 秒 | 4.132 秒 | 4915 | ✅ `get_market_data_ex` 可读 |

#### 重复运行性能复测

为排除首次调用/缓存预热影响，单进程连续运行 5 次同一股票、同一日期的完整链路：

| 周期 | MiniQMT 5 次耗时范围/平均 | compat 5 次耗时范围/平均 | 行数 |
| --- | --- | --- | ---: |
| `1d` | 0.059–0.938 秒 / 0.250 秒 | 0.167–0.373 秒 / 0.276 秒 | 1 |
| `1m` | 0.070–0.140 秒 / 0.085 秒 | 0.164–0.277 秒 / 0.221 秒 | 241 |
| `tick` | 0.213–0.332 秒 / 0.276 秒 | 0.479–0.816 秒 / 0.684 秒 | 4915 |

此前 compat tick 的 4.132 秒是冷启动/桥接首次处理的异常高值；连续运行后稳定在约
0.5–0.8 秒，仍约为 MiniQMT 的 2.5 倍，主要成本是 JSON 文件传输和 DataFrame 重建。

两边的签名均为 `download_history_data(stock_code, period, start_time='', end_time='',
incrementally=None)`。MiniQMT 返回 `None`；compat 返回 `{stock_code: True}`，表示 Big
QMT 的 `down_history_data` 逐项完成结果。这是返回值差异，不影响下载后数据读取；tick
字段差异仍按 `get_market_data_ex` tick 专节记录。

#### 与 `get_market_data_ex` 的标准联动验收

在相同环境、股票 `000779.SZ`、日期 `20260901` 下，按“下载后查询”的调用顺序分别测量：

| 周期 | MiniQMT 下载 | MiniQMT 查询 | compat 下载 | compat 查询 | 返回行数 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `1d` | 0.160 秒 | 0.769 秒 | 0.419 秒 | 0.139 秒 | 1 |
| `1m` | 0.105 秒 | 0.065 秒 | 0.219 秒 | 0.158 秒 | 241 |
| `tick` | 0.111 秒 | 0.078 秒 | 0.475 秒 | 0.587 秒 | 4915 |

三种周期均收到 1 次完成回调；compat 返回结果为 `{stock: True}`，MiniQMT 返回 `{}`，
这是底层下载函数返回值语义差异，不影响下载完成。`1d`、`1m` 的结构和核心数值已通过
fixture 对照；tick 的行数、时间戳和核心字段已通过，字段差异见 tick 专节。

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
- `tools/probe_market_data_ex.py`：按周期测量 `download_history_data2` 与 `get_market_data_ex` 联动。

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
