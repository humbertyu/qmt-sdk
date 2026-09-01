# Tick 兼容性报告

[English](tick-compatibility.md) | [简体中文](tick-compatibility.zh-CN.md)

本文档单独记录 Tick 兼容性的验证证据。接口能够调用或 DataFrame 结构一致，均不
代表数据已经完全一致。

## 验证样本

| 项目 | 数值 |
| --- | --- |
| 股票 | `000779.SZ` |
| 交易日 | `2026-09-01` |
| 大 QMT 历史数据条数 | 4915 |
| 现有 MiniQMT 业务数据 DB6 条数 | 4915 |
| 完全对应的时间戳 | 4915 / 4915 |
| 第一条时间 | `09:15:00.000` |
| 最后一条时间 | `15:30:00.001` |

结果包含 15:00 后的有效交易记录。兼容层不会过滤 15:00–15:30 的数据。

## 字段验证结果

| 字段 | 结果 | 证据或差异 |
| --- | :---: | --- |
| `time` | ✅ | 4915 个时间戳全部精确一致。 |
| `lastPrice`、`open`、`high`、`low`、`lastClose` | ✅ | 数值一致，仅存在浮点表示尾差。 |
| `volume` | ✅ | 全部精确一致。 |
| `askVol`、`bidVol` | ✅ | 全部精确一致。 |
| `askPrice`、`bidPrice` | ✅ | 数值一致，序列化后的浮点字符串可能不同。 |
| `transactionNum`、`openInt` | ✅ | 在当前样本中全部精确一致。 |
| `amount` | ⚠️ | 1716 条存在取整差异，最大绝对差为 1 元。 |
| `stockStatus` | ⚠️ | 当前大 QMT 历史结果返回 `0`；DB6 中包含 `2`、`3`、`5`、`8`、`12`、`13` 等交易阶段状态码。 |
| `pvolume` | ⚠️ | 当前大 QMT 历史结果在有效交易记录中返回 `0`；DB6 中为累计股数。 |
| `tickvol` | ⚠️ | 当前大 QMT 历史结果不提供该字段；兼容 DataFrame 中的 `0` 仅为结构占位值。 |
| `pe` | ⚠️ | 当前大 QMT 历史结果不提供该字段；兼容 DataFrame 中的 `0.0` 仅为结构占位值。 |

## 使用结论

当前桥接可以用于时间戳补偿，以及依赖核心价格、累计成交量、盘口和成交笔数的业务。
如果调用方依赖 `stockStatus`、`pvolume`、`tickvol` 或 `pe`，则不能把兼容结果视为
与 MiniQMT 完全等价。

因此可以先让 `sync-tick-redis` 写入独立 Redis 数据库进行验证；在确认下游没有依赖
上述四个差异字段前，不应覆盖可信生产数据。

## 复现工具

- `tools/capture_workflow_fixture.py`
- `tools/compare_workflow_fixtures.py`
- `tools/probe_subscription.py`

开源库本身不依赖 Redis。DB6 仅作为本次样本的外部验收基准。
