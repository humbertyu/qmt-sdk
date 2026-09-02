# qmt-sdk

[English](README.md) | [简体中文](README.zh-CN.md)

`qmt-sdk` 通过运行在 QMT 内部的纯文件桥接，提供统一 QMT API，同时兼容 MiniQMT
`xtquant.xtdata`。它面向缺少 `_socket`、`_ctypes`、pandas、Redis、
ZeroMQ 或其他第三方包的 QMT Python 裁剪运行环境。

当前状态：实验版 `0.2.0`。在与生产行情完成对照验证前，建议与现有 MiniQMT
并行部署，不要直接替换生产链路。

## 为什么使用文件 IPC？

- QMT 策略侧只使用内置标准库和 `ContextInfo`。
- 请求、响应和订阅事件均采用原子写入，可以检查和审计。
- 外部回调成功处理前，订阅事件会保留在磁盘上。
- 项目不分发 QMT DLL、专有 Python 包或厂商源代码。

文件 IPC 的代价是额外延迟和文件系统负载。它面向常规行情、故障恢复和广泛的
QMT 环境适配，不面向订单簿或逐笔级高频交易。

## API 实现与兼容情况

README 不重复罗列各接口结论。统一的
[API 兼容性文档](docs/xtdata-api-matrix.md) 包含 138 个官方接口、业务命令映射、
返回结构验证、逐字段差异、数值误差、已知限制和可复现测试工具。

未支持或尚未验证的接口会被明确标记，不会被笼统描述为兼容。

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
    [qmt_sdk] started root=D:\FinTools\QMT\xtquant_compat_bridge
   ```

桥接默认使用独立目录，不会接触之前实验使用的
`D:\FinTools\QMT\file_bridge`。

## 外部调用

业务调用通常只需修改导入路径：

```python
from qmt_sdk import QmtClient

client = QmtClient()
print(client.jobs.bridge_status())

# MiniQMT 存量代码也可继续使用：
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
