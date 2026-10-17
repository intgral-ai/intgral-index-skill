# intgral-guide-skill

供成员交给语言模型使用的团队工作指南。描述要推进的工作，模型会先找到相关资料，再厘清目标、责任角色、依赖、下一步行动与完成标准。

本公开仓库保存可复用的方法、通用角色和空配置示例。实际成员、项目目标、内部来源与审批规则在团队私有系统中维护。

调用名：`intgral-guide-skill`。仓库：https://github.com/intgral-ai/intgral-guide-skill。

仓库另含 [intgral-meeting](skills/intgral-meeting/SKILL.md)：读取 Wispr Flow 会议、My thoughts 与独立笔记，查重归档，并在用户要求时从产品愿景到 MVP、engineering 更新现有文档。未确认的范围与分工保持待确认。

## Meeting skill 与 Wispr 接入

原有指南仍在仓库根目录；会议 skill 在 `skills/intgral-meeting/`，两者可分别安装。正式安装使用已合并的 `main`；PR 分支供评审，不覆盖已安装的稳定副本。

在带有 skill-installer 的 Codex 中，合并后可直接请求：

> 使用 $skill-installer，从 intgral-ai/intgral-guide-skill 的 main 安装 skills/intgral-meeting。

也可将 `skills/intgral-meeting/` 完整复制到客户端的 skills 目录，保留 `references/` 和 `agents/`。安装后下一轮对话可调用 `$intgral-meeting`。

在客户端连接 **Wispr Flow**，使用本人账号完成授权。仅安装 skill 不会自动安装连接器或完成 OAuth。支持 Codex plugin 的客户端可加载本仓库根目录的 [.codex-plugin/plugin.json](.codex-plugin/plugin.json)，其中通过 [.app.json](.app.json) 将官方 Wispr app 声明为必需依赖；该 manifest 不含令牌，也不代成员授权。导入入口由客户端提供。

首次使用前，在私有配置或当前会话提供：归档目标、时区、来源相关性/起始范围、私有 state 路径；需要 top-down 时再指定三份现有主文档。已有项目配置则直接沿用。只在获授权的目标登录 docs，并遵守项目的浏览器设置。不要把个人配置、state、会议原文或账号凭据放入本仓库。

调用示例：

> 使用 $intgral-meeting，更新今天的 meeting，包含 Wispr 的 My thoughts 和独立笔记，写回现有会议档案。

> 使用 $intgral-meeting，根据这三场会议从 top down 更新产品愿景、MVP 和 engineering。未确认的范围、分工和日期标待确认，保留已有确认和评论。

接入验证分三步：能列出本人授权范围的会议；能完整读取一场会议的 notes/transcript；能按请求写入并重新加载目标档案。只验证连接时不要修改文档。插件导入、连接授权与写回是否成功分别报告；本仓库的静态检查不能证明客户端已连接。

## 使用

将整个目录安装或复制到模型客户端支持的 skills 目录，保留 `SKILL.md`、`references/` 和 `assets/` 的相对结构；也可以把 [SKILL.md](SKILL.md) 和所需的引用文件一起交给模型。

例如：

> 使用 intgral-guide-skill：我收到一项客户反馈，需要判断下一步应该补什么信息、与哪些角色协作，以及产物放在哪里。

需要实际团队信息时，按 [配置示例](assets/team-context.example.json) 在**仓库外的私有位置**建立配置，并让当前模型读取该文件。支持本地文件的环境可设置 `INTGRAL_TEAM_CONTEXT` 指向它；没有配置或工具权限时，模型仍能给出角色级指导，并说明关键缺口。配置中使用现有系统的访问控制，不存放访问令牌。

提供 `workspace_root` 后，模型先读取该根目录下的 `AGENTS.md`，再由 skill 按项目配置中的 `local_indexes` 加载任务相关资料，并到源站核实实时状态。相对的 `workspace_root` 从配置文件所在目录解析，索引路径从工作区根目录解析。实际根路径和索引内容留在私有工作区；资料索引与具体代码仓库的知识图分别维护。

团队目标、成员分工、会议安排和任务状态在私有来源中维护。只有查找资料、协作或记录流程改变时，才需要更新本 skill。

## 工作流程

1. 明确这次要达成的结果和当前卡点。
2. 读取项目 `AGENTS.md` 和获授权的私有配置，通过 `local_indexes` 只定位本次所需来源。
3. 回到来源核实适用版本与当前状态，连接目标、任务、角色、依赖和产物。
4. 给出下一步行动：谁参与、需要什么输入、产物放哪、怎样算完成；按请求和既有授权执行。
5. 将已确认的结果链接回相关文档和任务，交接待核验事项。

## 平台分工

| 平台 | 负责什么 |
|---|---|
| Figma | 设计系统、UI/UX、组件与交互，实施和评审对齐适用版本 |
| [docs.intgral.ai](https://docs.intgral.ai) | 商务、研究、会议、团队流程等文档 |
| Drive | 需要在 Drive 保存的文件和附件，由相关文档链接过去 |
| Slack | 讨论、协调、决策来源和交接 |
| Linear | 正式任务、负责人、依赖和计划状态 |
| GitHub | 代码、PR、测试、实现与发布证据 |

工作方法与平台关系见 [gear map](references/gear-map.md)，工作场景分支见 [workflows](references/workflows.md)。Skill 的指导本身不扩大成员或模型的操作权限。

## 贡献与检查

公开 issue 和 PR 使用虚构示例与通用角色。内部资料、链接、设计截图、客户记录和私有配置留在私有系统中。提交前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

仅需 Python 3.11 或更高版本，无第三方运行依赖：

```sh
python3 scripts/validate.py --history
python3 -m unittest discover -s tests -v
```

检查涵盖包结构、相对链接、配置示例、当前文件及 Git 历史中的常见敏感信息模式。还需要人工确认内容适合公开；自动检查不等于完整的安全审计。

采用 [MIT License](LICENSE)。
