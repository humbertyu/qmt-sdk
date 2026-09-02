# 新增 API 实施标准

本文档定义 `qmt-sdk` 新增或完善一个 `xtquant_compat.xtdata` API 时必须遵循的完整流程。
它是开发清单和验收标准；具体接口的结果、字段差异和测试数字写入
[`xtdata-api-matrix.md`](xtdata-api-matrix.md)，不要散落在 README 或业务项目文档中。

## 一、接口登记

1. 从目标版本的官方 `xtquant.xtdata` 获取准确名称、签名、默认值和返回类型。
2. 更新 `src/xtquant_compat/official_xtdata_api.json`（使用生成工具，不手工伪造签名）。
3. 在 `docs/xtdata-api-matrix.md` 的完整矩阵中登记状态：`🧪`、`⚠️` 或 `✅`。
4. 在矩阵行中填写“验证入口”，只能写 compat 项目的 API probe 或测试脚本，不能写
   blackbox-qmt 的业务命令。

## 二、行为设计

在写代码前明确并记录：

- 同步还是异步；是否允许回调；
- 单标的还是批量；外部调用是否必须保持一次调用；
- 是否可能长时间运行；默认超时和最大规模；
- 空输入、空结果、重复代码和非法参数的行为；
- 是否存在 QMT 端等价接口；
- MiniQMT 与 QMT 的字段、类型、索引、时间和精度差异。

普通查询必须保持纯查询语义，不得在查询函数内部偷偷下载或修改用户数据。

## 三、实现分层

每个 API 必须经过以下层次，不能把 QMT 特殊逻辑暴露给调用方：

```text
xtdata.py（MiniQMT 同名签名）
    ↓ 参数校验、返回规范化
client.py（一次请求、超时、取消、事件投递）
    ↓ JSON file protocol
XTQUANT_COMPAT_BRIDGE.py（QMT 端调用适配）
    ↓ QMT ContextInfo / 全局函数
QMT
```

批量 API 的外部签名和请求必须保持批量；如果 QMT 只有单项接口，只允许在桥接内部
循环，并在文档中记录性能原因。不得由业务项目偷偷改变 API 语义。

## 四、协议要求

请求必须包含 `protocol_version`、`request_id`、`client_id`、`method`、`params` 和时间戳。
响应必须包含 `request_id`、`ok` 和 `data`，错误必须包含可读错误、类型和 traceback。

长任务必须写入 `status/<request_id>.json`，至少包含：

```json
{"state":"pending|running|finished|failed|cancelled|abandoned",
 "processed":0,"total":0,"failed":0,"bridge_instance_id":"..."}
```

客户端必须支持超时取消、Ctrl+C 取消、状态读取；桥接重启时旧的 pending/running 任务必须
标记为 `abandoned`，不得假装自动恢复。取消是协作式的，在批次/单项边界检查；不能强制
中断正在执行的宿主 API 调用。

## 五、返回规范化

在 `xtdata.py` 集中处理：

- 外层容器和股票键；
- DataFrame 的行列方向、索引和列名；
- 字段顺序、缺失字段和占位值；
- 日期、整数、浮点和布尔类型；
- MiniQMT 拼写别名及 QMT 扩展字段。

单项和批量接口必须调用同一规范化 helper，避免两个入口返回不同结构。

## 六、验证顺序

每个 API 至少完成以下验证，并在矩阵对应章节逐项记录：

1. 签名：位置参数、关键字参数、默认值；
2. 可用性：QMT 策略能否调用；
3. 结构：外层类型、键、DataFrame 方向、索引、列和 dtype；
4. 数据：与 MiniQMT 相同输入的记录数量、时间范围、核心字段和数值容差；
5. 边界：空列表、单项、多项、无数据、非法代码；
6. 长任务：状态、进度、超时、取消、失败和桥接重启；
7. 性能：固定样本、规模、环境、耗时和瓶颈分解；
8. 重复运行：确认无脏响应、孤儿 processing 文件或重复事件。

验证结论只能使用：

- `✅`：在明确样本、周期和字段范围内结构与数据通过；
- `⚠️`：可调用但有明确字段、数据、性能或语义差异；
- `🧪`：仅完成签名/通用转发，真实行为未验证；
- `➖`：MiniQMT 本地连接语义无法由文件桥接保留。

## 七、必须更新的文件

完成一个 API 后检查以下文件：

- `src/xtquant_compat/official_xtdata_api.json`：官方签名/元数据；
- `src/xtquant_compat/xtdata.py`：公开 API 和返回规范化；
- `src/xtquant_compat/client.py`：仅在需要新协议能力时修改；
- `qmt_strategy/XTQUANT_COMPAT_BRIDGE.py`：QMT 端适配；
- `tests/test_xtdata.py`：签名、结构和规范化单元测试；
- `tests/test_qmt_bridge.py`：桥接 dispatch、错误、取消和状态测试；
- `docs/xtdata-api-matrix.md`：汇总行和对应的详细章节；
- `README.md`：只在安装/使用方式变化时更新，并链接本标准文档。

## 八、交付门槛

未完成结构/数据/边界验证时不得标记为 `✅`。必须运行单元测试、编译检查和 lint；涉及
QMT 桥接脚本的改动必须部署后重启 `XTQUANT_COMPAT_BRIDGE_LAUNCHER`，并在交付记录中写明
实例 ID。涉及纯客户端或文档的改动不要求重启。

`get_instrument_detail_list` 是本标准的参考范例：它展示了批量外部语义、QMT 内部单项
适配、统一字段规范化、规模性能记录以及已知底层差异的完整写法。
