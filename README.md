# LiveDiscoveryBench Tasks

Public task-contribution repository for [LiveDiscoveryBench](https://github.com/PrismaX-Team/LiveDiscoveryBench).

This repository accepts task packages only after the corresponding Proposal has been approved for PR. Proposal approval allows a pull request; it does not mean that the task has passed final scientific review, been merged, or been formally published.

LiveDiscoveryBench 正式任务的公开共建仓库。

本仓库只接收已经获准进入 PR 阶段的 Proposal。Proposal 获准仅表示可以提交 PR，不代表任务已经通过最终科学审核、已经合并或已经正式发布。

## Task package contract / 任务包合同

Each task lives at `tasks/<task-id>/` and contains exactly five top-level parts:

每个任务位于 `tasks/<task-id>/`，顶层只包含以下五部分：

```text
tasks/<task-id>/
├── instruction.json
├── input/
├── environment/
├── verifier/
│   └── run/
│       └── main.py
└── meta.json
```

- `instruction.json` describes the task, Agent-visible inputs, required submission artifacts, the supplied environment, hard requirements, and confirmed resource limits.
- `input/` contains only data and optional submission templates visible to the Agent.
- `environment/` contains files that construct or prepare the task-specific initial environment; it may be empty.
- `verifier/` contains the fixed, offline, deterministic verifier and any scoring material it owns. Its required entry is `verifier/run/main.py`.
- `meta.json` is the concise task index: identity, domain, immutable construction source, stable data sources, raw metric, optional Matrix transform, and optional measured baseline.

- `instruction.json` 描述任务、Agent 可见输入、必须提交的产物、已提供环境、硬约束和已经确认的资源限制。
- `input/` 只保存 Agent 可见的数据和可选提交模板。
- `environment/` 保存构建或准备任务专用初始环境的文件；没有专用环境时可以为空。
- `verifier/` 保存固定、离线、确定性的 Verifier 及其自行管理的评分材料；固定入口为 `verifier/run/main.py`。
- `meta.json` 是任务简洁索引，记录身份、领域、不可变构造来源、稳定数据来源、原始指标、可选 Matrix 变换和可选实测 baseline。

Baselines, construction histories, review records, tests, and the full body of source evidence are maintained outside the five-part formal package. A package being present in this repository is not, by itself, evidence of scientific admission or runtime readiness.

Baseline、构造历史、审核记录、测试和完整来源证据在五部分正式包之外独立维护。任务包出现在本仓库本身，不等于它已经科学准入或能够稳定运行。

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. The automated workflow performs read-only structural and JSON syntax checks only. It never installs task dependencies, runs a Verifier, extracts archives, or executes code supplied by a pull request.

提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。自动工作流只进行只读结构检查和 JSON 语法解析；它不会安装任务依赖、运行 Verifier、解压归档，或执行 PR 提供的任何代码。
