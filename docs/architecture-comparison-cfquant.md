# 与 cfquant 通信架构对照

本文记录对 [95ge/cfquant](https://github.com/95ge/cfquant) 的架构参考结论，避免后续重复
讨论或在稳定协议上做无必要的重构。

## cfquant 的可借鉴模式

cfquant 的 `xtdata.py` 将 API 调用统一映射为：

```text
xtdata.method(...)
  → client.request("xtdata.method", args/kwargs)
  → PipeHub / named pipe
  → QMT bridge action 分发
  → QMT callable
```

回调接口先注册事件名，再由客户端事件循环把 QMT 事件还原成 Python callback。核心价值是
API 层、通信层和 QMT 适配层分离，并且批量参数原样传递。

## xtquant-compat 的对应实现

```text
xtdata.method(...)
  → FileBridgeClient.request(method, params)
  → JSON 文件协议
  → XTQUANT_COMPAT_BRIDGE.py 分发
  → QMT ContextInfo / 全局 callable
```

当前项目已经具备对应能力：

| cfquant 模式 | compat 实现 | 决策 |
| --- | --- | --- |
| 统一 request(action, args/kwargs) | `method + params` 统一请求 | 保持；MiniQMT 签名在 API 层绑定，避免破坏现有协议 |
| 独立通信层 | `client.py` 文件传输 | 保持；QMT Python 缺少 `_socket`/`_ctypes`，named pipe 不可作为基础依赖 |
| QMT bridge action 分发 | `_handle()` 显式映射 + generic fallback | 保持；新 API 先显式映射，无法确认时标记条件转发 |
| callback/event 注册 | `events/<client>/<subscription>` + callback 线程 | 保持；已支持至少一次投递和 processed 归档 |
| 下载生命周期 | cfquant callback event/job 参数 | compat status 文件 + `get_request_status`/`cancel_request` | 已扩展为可观测、可取消协议 |
| 低延迟 named pipe | PipeHub/ctypes | 暂不采用；与纯标准库和 QMT 裁剪环境冲突 |

## 不在当前阶段重构的部分

1. 不把 `params` 改成 `args/kwargs` 双协议。当前所有已部署 QMT bridge 都使用 `params`，
   修改会要求同步替换桥接脚本并重新验证全部接口；API 层已通过官方签名绑定保证参数顺序。
2. 不把查询 API 隐式改成“下载后查询”。`get_market_data` 和 `get_market_data_ex` 必须
   保持 MiniQMT 的纯查询语义，历史下载由调用方显式完成。
3. 不引入 Redis、ZeroMQ、ctypes 或第三方库作为 compat 基础依赖。

## 后续 API 的统一执行方式

后续每个接口继续按以下路径实现：

```text
官方签名
  → xtdata.py 参数绑定/返回规范化
  → client.py 一次请求
  → 文件协议
  → QMT bridge 显式或条件映射
  → 结构/字段/性能/异常/取消验证
  → xtdata-api-matrix.md 记录
```

`get_market_data` 的历史缓存完整性问题暂时不在本阶段扩展；下一阶段优先按该流程验证
`get_market_data_ex`，包括 `1d`、`1m`、`tick`、批量、字段差异和数据时间范围。
