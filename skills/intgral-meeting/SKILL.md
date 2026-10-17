---
name: intgral-meeting
description: Read Wispr Flow meetings, My thoughts and scratchpad notes, reconcile them into team meeting archives, and update product vision, MVP and engineering documents when requested. Use for meeting updates and post-meeting top-down documentation, with source-backed decisions and unresolved scope or ownership kept pending.
---

# Intgral Meeting

把 Wispr 原始记录变成可追溯的会议档案；用户要求时，再沿产品愿景 → MVP → engineering 更新现有文档。按用户的语言写。已确认决定、个人想法、讨论提议和待确认事项分别表达。

## 接入与范围

1. 使用当前成员自己的 Wispr Flow 连接器。本包的 plugin manifest 将 Wispr 列为必需 app；仅复制 skill 的客户端仍需单独连接 Wispr。缺少连接时提供连接入口和具体缺口，可继续准备文档结构；不要要求复制令牌或代用另一成员的账号。工具名称以运行时发现结果为准，见 [Wispr 读取规则](references/wispr.md)。
2. 读取用户提供的私有配置，或 `INTGRAL_TEAM_CONFIG` 指向的文件，兼容原有 `INTGRAL_TEAM_CONTEXT` 入口；项目明确指定配置时沿用它。读取 `workspace_root` 下的 `AGENTS.md`，通过 `local_indexes` 定位任务需要的来源。相对根目录从配置文件目录解析，索引路径从工作区根目录解析。没有配置时只询问目标档案位置、范围或时区等影响执行的缺口，不猜测真实成员和内部 URL。
3. 优先沿用 `collaboration_policy.meeting_archive`、`automation_execution`、`daily_logs`、`decision_making` 和当前确认记录。最少需要归档目标、时区、来源范围与起始边界、私有状态文件位置。路径与数据留在私有工作区，配置不扩大权限。
4. 判断本次结果：仅回顾、写回会议，或还要 top-down 更新。用户只说“更新 meeting”时完成会议归档与有关日志；只有明确要求或现有持续授权涵盖时才修改产品/MVP/engineering。不要因安装 skill 新建定时任务、启用其他录音源、发送团队广播或修改 Linear。

## 读取并归档

1. 按 [Wispr 读取规则](references/wispr.md) 列出指定范围或最近修改记录，完整读取有关 transcript、My thoughts 和需要的独立笔记。标明实际覆盖与未完成来源。
2. 结合私有状态与**当前在线档案**查重，覆盖已有人工归档；按 [归档与验证](references/archive.md) 更新同一场会议，保留手工内容、评论、图表、权限和既有链接。
3. 每场记录包含：本地时间与覆盖、来源链接、一句话结论、关键事实、已确认决定、提议/想法、行动与待确认项。行动没有明确负责人或期限就写“待确认”；未知说话人保留原标签。相对日期转换为具体日期，并保留依赖条件。
4. 按私有配置维护日期导航、中央当天工作日志和会议内当天执行日志的互链。仅补本次会议证据所支持的增量；其他来源未经读取不声明已汇总。最新有效摘要置前，旧快照保留并注明适用状态。
5. 对每个目标保存草稿、写入、重新加载并核对关键内容及链接。只有该目标读回成功才记为 verified；部分失败保留独立 pending，不把整批标成功或跳过下一次重试。

## 用户要求 top-down 时

读取 [top-down 更新](references/topdown.md)，先核对当前主文档和仍有效的确认依据，再依次更新愿景、MVP、工程约束与交付拆解。会议总结本身不构成批准；未确认的产品范围、架构、预算、分工、日期和验收门槛显式标待确认。不要用新草稿覆盖原文里的有效确认。

## 交付

返回实际更新的链接、读取范围、重要变化及剩余待确认/失败目标。区分“草稿已准备”“已写入并复核”“PR 待评审”“已安装”“账号已连接”。缺少原文、登录或目标权限时保留已完成工作和可恢复状态，说明阻塞；同一登录/权限错误重试一次仍失败就停止该目标，避免重复写入与提醒。

需要研究记录、决策确认或任务接入时，沿用私有配置中的 knowledge_capture / work_tracking 与已安装的团队指南。没有这些配置就记录有来源的待确认交接，不自行建立负责人、批准权或任务状态。发送消息、建任务、定时执行和权限调整分别需要已有授权。
