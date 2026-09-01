# xtquant-compat

[English](README.md) | [简体中文](README.zh-CN.md)

`xtquant-compat` 通过运行在大 QMT 内部的纯文件桥接，提供 MiniQMT
`xtquant.xtdata` API 的兼容实现。它面向缺少 `_socket`、`_ctypes`、pandas、Redis、
ZeroMQ 或其他第三方包的 QMT Python 裁剪运行环境。

当前状态：实验版 `0.1.0`。在与生产行情完成对照验证前，建议与现有 MiniQMT
并行部署，不要直接替换生产链路。

## 为什么使用文件 IPC？

- QMT 策略侧只使用内置标准库和 `ContextInfo`。
- 请求、响应和订阅事件均采用原子写入，可以检查和审计。
- 外部回调成功处理前，订阅事件会保留在磁盘上。
- 项目不分发 QMT DLL、专有 Python 包或厂商源代码。

文件 IPC 的代价是额外延迟和文件系统负载。它面向常规行情、故障恢复和广泛的
QMT 环境适配，不面向订单簿或逐笔级高频交易。

## API 兼容状态

兼容目标来自本机已安装的官方 `xtquant.xtdata` 公开函数，而不是项目自行定义的
接口集合。当前基准是官方发行版 `250516.1.1` / 模块版本 `xtquant_250516`，共包含
138 个公开函数。目前 138 个函数均已提供同名、同签名的公开入口；真实大 QMT
环境中的行为验证单独统计。

| 状态 | 数量 |
| --- | ---: |
| 公开 API 覆盖 | 138 / 138 |
| 已完成行为验证 | 8 |
| 已实现适配、等待验证 | 116 |
| MiniQMT 本地语义不同 | 14 |

官方接口名称、签名、状态和已知差异的完整列表见
[`docs/xtdata-api-matrix.md`](docs/xtdata-api-matrix.md)。

### 已实现的核心 API

| API | 大 QMT 可调用 | MiniQMT 结构一致 | MiniQMT 数据一致 |
| --- | --- | --- | --- |
| `get_full_tick` | 是 | 是 | 核心行情字段已验证 |
| `get_market_data_ex`（`1d`、`1m`） | 是 | 是 | 单日样本已验证 |
| `get_market_data_ex`（`tick`） | 是 | 是 | 核心字段已验证；差异见下文 |
| `get_market_data` | 是 | 是，股票为行、时间为列 | 单日样本已验证 |
| `subscribe_quote` / `unsubscribe_quote` | 是 | 是 | 当前快照和时间戳已验证 |
| `get_instrument_detail` | 是 | 已规范化业务所需字段 | 单股票样本已验证 |
| `get_stock_list_in_sector` | 是 | 股票代码列表 | 样本中大 QMT 多出 10 只较新股票 |
| `download_history_data(2)` | 是 | 支持完成回调 | 已验证两只股票及 `1d`/`1m`/`tick` |
| `bridge_status` | 是 | 项目扩展 API | 项目扩展 API |

仓库保留了可重复验收工具：`tools/capture_workflow_fixture.py`、
`tools/compare_workflow_fixtures.py` 和 `tools/probe_subscription.py`。

在已测的 `000779.SZ` 交易日中，大 QMT 与现有 MiniQMT 业务数据的 4915 个
Tick 时间戳全部一致，包含 `15:30:00.001`。价格、成交量、盘口量和成交笔数一致
（仅有浮点尾差），`amount` 最大相差 1 元。大 QMT 历史结果中的 `stockStatus`、
`pvolume`、`tickvol` 尚不能与原生值完全一致；项目将其明确列为已知差异。缺失的
结构字段会使用中性占位值，调用方不能将这些占位值视作与原生数据等价。

未支持的 API 不会被静默模拟。兼容性细节见
[`docs/compatibility.md`](docs/compatibility.md)。

## 安装外部客户端

请在外部 Python 3.8+ 环境中安装。不要将该包安装到 QMT 内置 Python 环境。

```powershell
cd D:\Projects\xtquant-compat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## 部署 QMT 策略

1. 将 `qmt_strategy/XTQUANT_COMPAT_BRIDGE.py` 复制到：

   ```text
   D:\FinTools\QMT\python\XTQUANT_COMPAT_BRIDGE.py
   ```

2. 在大 QMT 中新建策略，名称必须准确填写为：

   ```text
   XTQUANT_COMPAT_BRIDGE_LAUNCHER
   ```

3. 将 `qmt_strategy/XTQUANT_COMPAT_BRIDGE_LAUNCHER.py` 的内容粘贴到策略中。
4. 启动策略并确认日志出现：

   ```text
   [xtquant_compat] started root=D:\FinTools\QMT\xtquant_compat_bridge
   ```

桥接默认使用独立目录，不会接触之前实验使用的
`D:\FinTools\QMT\file_bridge`。

## 外部调用

业务调用通常只需修改导入路径：

```python
from xtquant_compat import xtdata

print(xtdata.bridge_status())
print(xtdata.get_full_tick(["000779.SZ"]))

seq = xtdata.subscribe_quote(
    "000779.SZ",
    period="tick",
    callback=lambda data: print(data),
)
```

订阅回调会被转换成常见的 MiniQMT 格式：

```python
{"000779.SZ": [{"time": 1788241293000, "lastPrice": 9.98, "volume": 640940}]}
```

默认桥接目录不合适时，可以显式配置：

```python
from xtquant_compat import configure

configure(root=r"D:\FinTools\QMT\xtquant_compat_bridge", timeout=30)
```

## 可靠性模型

- 请求和响应文件名包含 UUID。
- 写入方先写临时文件，再通过原子重命名发布。
- 行情订阅事件采用至少一次投递语义。
- 用户回调失败时，事件文件会保留并等待重试。
- 对于当前三秒行情，消费者应将 `symbol + time` 作为幂等标识。
- 历史 Tick 对账和补偿仍由上层应用负责。

文件通信协议见 [`docs/protocol.md`](docs/protocol.md)。

## 许可证与商标声明

项目采用 Apache-2.0 许可证。QMT、MiniQMT 和 xtquant 的名称归各自权利人所有。
本项目是独立的兼容实现，不包含其专有组件。
