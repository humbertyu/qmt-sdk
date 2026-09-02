# qmt-sdk

`qmt-sdk` 是一个面向中国用户的 QMT 外部调用 SDK。它通过运行在 QMT 内部的文件桥接，
把 QMT 的查询和行情能力安全地暴露给外部 Python 程序；同时提供 `xtquant_compat`，
用于适配 MiniQMT/`xtquant.xtdata` 的常用接口，帮助已有 MiniQMT 代码迁移到 QMT。

项目当前以查询和行情为主，不包含下单、撤单、账户或持仓修改。文件桥接不依赖 QMT
Python 环境中的 Redis、ZeroMQ、`_socket`、`_ctypes` 或 pandas；外部 Python 环境负责
安装 pandas 等数据处理依赖。

## 一、项目提供什么

```text
外部 Python 程序
    ├─ qmt_sdk       QMT 原生风格的统一客户端
    └─ xtquant_compat MiniQMT/xtquant.xtdata 兼容层
            ↓
      文件 bridge（运行在 QMT 策略中）
            ↓
      QMT ContextInfo
```

`qmt_sdk` 尽量返回 QMT 原生结构；`xtquant_compat` 再将结果转换为存量 MiniQMT
代码常用的结构。两者共用同一个文件 bridge 和请求队列，QMT API 始终在策略线程中串行执行。

## 二、安装外部 Python 客户端

不要把本项目安装到 QMT 自带的 Python。请使用外部 Python 3.8 或更高版本：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

如果只使用运行时，不需要开发依赖，可以执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

## 三、在 QMT 中部署 bridge

仓库的 `qmt_strategy` 目录已经包含两个需要部署的文件：

- `XTQUANT_COMPAT_BRIDGE.py`：实际 bridge 实现；
- `XTQUANT_COMPAT_BRIDGE_LAUNCHER.py`：QMT 策略入口。

安装步骤：

1. 将 `qmt_strategy/XTQUANT_COMPAT_BRIDGE.py` 复制到 QMT Python 的搜索路径中。
   通常可以复制到 QMT 安装目录下的 `python` 目录；不要求使用某个固定盘符或目录名称。
2. 在 QMT 策略管理器中新建一个策略，名称准确填写：

   ```text
   XTQUANT_COMPAT_BRIDGE_LAUNCHER
   ```

3. 打开仓库中的 `qmt_strategy/XTQUANT_COMPAT_BRIDGE_LAUNCHER.py`，将全部内容复制到该策略。
4. 启动策略，确认日志出现类似：

   ```text
   [xtquant_compat] started root=... instance=...
   [xtquant_compat] scheduled adjust interval=100nMilliSecond
   ```

launcher 会自动从 QMT 的 `sys.path` 查找 `XTQUANT_COMPAT_BRIDGE.py`。如果 QMT 没有把
复制目录加入搜索路径，可以设置环境变量 `XTQUANT_COMPAT_BRIDGE_FILE` 指向该文件。

bridge 默认使用独立的数据目录；请求、响应、状态和订阅事件都会写入其中。不要把这个
目录与其他实验 bridge 混用，也不要将其加入生产数据目录。

## 四、外部程序调用

### 使用 QMT 原生风格客户端

```python
from qmt_sdk import QmtClient

client = QmtClient()
print(client.data.get_market_data_ex(
    ["open", "high", "low", "close", "volume", "amount"],
    ["000001.SZ"], "1d", "20260902", "20260902",
))
```

### 迁移 MiniQMT/xtquant 存量代码

```python
from xtquant_compat import xtdata

stocks = xtdata.get_stock_list_in_sector("沪深A股")
data = xtdata.get_market_data_ex(
    ["open", "high", "low", "close", "volume", "amount"],
    stocks[:10], "1d", "20260902", "20260902",
)
print(data)
```

订阅接口保持常见 MiniQMT 调用方式：

```python
def on_quote(data):
    print(data)

seq = xtdata.subscribe_quote("000001.SZ", period="tick", callback=on_quote)
# 不再需要时：
xtdata.unsubscribe_quote(seq)
```

默认 bridge 配置不适合时，可以显式设置目录和超时：

```python
from xtquant_compat import configure

configure(root=r"<bridge-data-root>", timeout=120)
```

## 五、目前支持的能力

以下按能力分类列出，不在 README 中重复维护每一个接口的字段差异。完整签名、实现状态、
返回结构、逐字段差异和测试记录以 [API 兼容性文档](docs/xtdata-api-matrix.md) 为准。

### 行情与历史数据

- `get_market_data`、`get_market_data_ex`、`get_local_data`
- `get_full_tick`
- `get_history_data`
- `download_history_data`、`download_history_data2`
- 1d、1m、tick 数据读取和独立落盘流程

### 订阅与事件

- `subscribe_quote`
- `subscribe_whole_quote`
- `unsubscribe_quote`
- 订阅事件回调、事件文件持久化和至少一次投递

### 标的、板块与交易日历

- `get_stock_list_in_sector`
- `get_instrument_detail`、`get_instrument_detail_list`
- 交易日历、ST 状态、合约列表和合约属性查询

### ETF、期权和指数

- ETF 信息和 IOPV
- 期权列表、期权详情、标的数据
- 指数成分、权重和主力合约查询
- 除权除息、BSM 价格和隐含波动率计算

### 财务和市场扩展查询

- `get_financial_data`
- 港股通、龙虎榜、北向资金等市场扩展查询
- `get_turnover_rate`、`get_raw_financial_data` 已接入签名，但当前部分 QMT 环境缺少
  pandas，暂不作为可用数据能力承诺

### 当前明确不在范围内

- 下单、撤单及交易回报
- 账户、持仓和资金修改
- 需要厂商专有 DLL 或 QMT 外部服务才能完成的功能

## 六、请求、订阅和可靠性

外部请求可以并发提交，但同一个 QMT 实例中的 `ContextInfo` API 始终单线程串行执行。
订阅建立后，行情事件走独立事件通道，不持续占用普通查询通道；订阅控制请求仍需等待
当前正在执行的 QMT 调用结束。

请求状态包括排队、运行、完成、失败和取消。长任务超时后，调用方应检查状态并根据业务
需要补偿；bridge 不能强行中断已经进入 QMT 的底层调用。历史 tick 与业务数据的收盘后
补偿也由调用方负责。

## 七、文档与测试

- [API 兼容性与逐字段测试记录](docs/xtdata-api-matrix.md)
- [API 标准实现流程](docs/api-implementation-standard.md)
- [文件协议](docs/protocol.md)

测试工具位于 `tools` 目录，测试输出应写入独立临时目录，不能覆盖生产数据。

## 八、许可证

本项目采用 Apache-2.0 许可证。QMT、MiniQMT 和 xtquant 是其各自权利人的名称；
本项目是独立的适配实现，不包含厂商专有组件。
