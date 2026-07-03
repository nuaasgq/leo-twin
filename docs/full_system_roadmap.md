# LEO-Twin Full-System Roadmap

## 总体策略

完整版开发采用“契约冻结 -> 并行实现 -> 集成验证 -> 性能收敛”的持续迭代方式。每轮只处理一个明确任务，所有任务必须有测试、review 和 CI gate。

## 任务 DAG

```mermaid
flowchart TD
    FS000["FS-000 阶段治理升级"]
    FS010["FS-010 全域耦合契约"]
    FS020["FS-020 轨道精细化模型"]
    FS030["FS-030 网络协议栈契约"]
    FS040["FS-040 算力资源契约"]
    FS050["FS-050 三维展示控制前端"]
    FS060["FS-060 数据面板前端"]
    FS070["FS-070 全域指标体系"]
    FS080["FS-080 轨道-网络耦合"]
    FS090["FS-090 网络-算力耦合"]
    FS100["FS-100 全链路集成验证"]

    FS000 --> FS010
    FS010 --> FS020
    FS010 --> FS030
    FS010 --> FS040
    FS010 --> FS050
    FS010 --> FS060
    FS010 --> FS070
    FS020 --> FS080
    FS030 --> FS080
    FS030 --> FS090
    FS040 --> FS090
    FS050 --> FS100
    FS060 --> FS100
    FS070 --> FS100
    FS080 --> FS100
    FS090 --> FS100
```

## 12 步执行路线

1. 升级项目治理：区分 MVP-0 与完整版阶段。
2. 冻结完整版跨域数据契约和事件耦合边界。
3. 建立自动任务 DAG，使 Orbit / Network / Compute / Frontend 可并行推进。
4. 扩展轨道配置契约：轨道根数、姿态、星座、星历输入边界。
5. 扩展网络协议栈契约：应用层、传输层、网络层、数据链路层、物理层、信道层。
6. 扩展算力契约：节点资源、任务队列、服务链、卸载策略输入输出。
7. 实现轨道精细化第一版，并保持事件输出稳定。
8. 实现网络分层第一版，路由、链路和信道通过配置画像驱动。
9. 实现算力资源第一版，使任务生命周期受网络传输状态影响。
10. 拆分前端：三维控制界面与数据面板界面分别独立运行。
11. 增加全域指标：轨道、链路、路由、传输、任务、资源、UI 性能。
12. 做大规模稳定性收敛：万星级逻辑规模、长时间事件流、内存与指标下采样。

## 并行工作流

| 工作流 | 主要目录 | 首要任务 |
|---|---|---|
| Orbit | `src/leo_twin/models/orbit/` | 精细轨道状态生成与 `ORBIT_UPDATE` 稳定输出 |
| Network | `src/leo_twin/models/network/` | 分层协议栈、空地/空空链路、路由输出 |
| Compute | `src/leo_twin/models/compute/` | 任务队列、资源状态、任务生命周期 |
| Metrics | `src/leo_twin/services/metrics/` | KPI 聚合、下采样、数据面板输出 |
| Frontend 3D | `frontend/src/3d/` + `frontend/src/config_panel/` | 中文控制面、三维轨道/链路/覆盖展示 |
| Frontend Dashboard | `frontend/src/dashboard/` | 独立中文数据面板 |

## 当前实现状态

截至 2026-07-04，本路线图已经从“契约冻结”推进到“可运行全链路雏形”。下表用于约束后续开发，避免重复实现或越界重构。

| 领域 | 已具备能力 | 主要文件 | 下一步缺口 |
|---|---|---|---|
| 任务治理 | 完整版任务 DAG、阶段边界和自动化执行规则 | `docs/codex_skill.md`, `src/leo_twin/sees/full_system_tasks.py` | 将 DAG 状态接入可视化任务面板 |
| 轨道 | 确定性 Kepler 轨道状态生成，输出 `ORBIT_UPDATE` | `src/leo_twin/models/orbit/keplerian.py` | 星座批量配置、摄动画像、星历导入边界 |
| 网络接入 | 基于卫星位置的空地接入和链路状态生成 | `src/leo_twin/models/network/position_engine.py` | 空空链路、多跳拓扑、增量拓扑缓存 |
| 网络分层 | 应用层、传输层、网络层、数据链路层、物理层、信道层配置画像 | `src/leo_twin/models/network/stack.py` | 每层协议画像和事件输出的更细粒度映射 |
| 信道/物理 | 确定性链路预算、自由空间损耗、容量估算 | `src/leo_twin/models/network/channel.py` | 天气/遮挡画像、频率复用、波束切换 |
| 路由 | 静态、最短路径、链路状态、距离向量画像的确定性路径选择 | `src/leo_twin/models/network/routing.py` | 动态链路代价、空空多跳策略、失败重路由 |
| 传输 | TCP/UDP 流级传输画像，影响时延和有效容量 | `src/leo_twin/models/network/transport.py` | 拥塞窗口画像、丢包响应、业务流分类 |
| 算力 | 路由感知任务生命周期和确定性调度策略 | `src/leo_twin/models/compute/network_aware.py`, `src/leo_twin/models/compute/scheduling.py` | 将调度策略接入运行引擎，增加服务链与资源争用 |
| 指标 | 全链路事件采集、摘要输出和前端态势数据 | `src/leo_twin/services/metrics/collector.py` | 分层 KPI、下采样策略、长时间运行分段输出 |
| 前端 | 中文三维控制面、配置控制、数据面板和全链路态势卡片 | `frontend/src/` | 拆分独立数据面板入口，补充链路/路由/算力图表 |
| 规模验证 | 千星级位置网络 smoke test 和确定性回归 | `tests/scale/` | 万星级逻辑配置、百万事件稳定性预算 |

## 下一批可执行任务

1. 将 `ComputeSchedulingRuntime` 接入 `RouteAwareComputeEngine`，让任务排队策略影响 `TASK_START` 和 `TASK_FINISH`。
2. 为完整流水线增加多卫星、多用户配置生成器，覆盖星座、用户分布、业务流和算力节点。
3. 在 `PositionDrivenNetworkEngine` 中加入空空链路与增量拓扑缓存，避免每轮全图重算。
4. 按链路类型拆分信道画像：空地、空空、地面回传。
5. 为前端增加链路预算、路由路径、传输协议和算力队列的中文数据面板。
6. 建立万星级逻辑规模配置和性能预算测试，明确事件增长、内存窗口和指标采样上限。

## 验收原则

- 轨道、网络、算力必须互相影响，但只能通过事件影响。
- 网络层次必须清晰，协议和物理/信道参数先以配置画像表达。
- UI 必须中文化，按钮必须绑定实际控制行为。
- 每次迭代必须能回归现有测试。
- 大规模能力必须通过压测和稳定性指标证明，不能只靠声明。
