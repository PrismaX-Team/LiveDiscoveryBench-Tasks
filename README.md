# LiveDiscoveryBench Tasks

Task contribution repository for LiveDiscoveryBench. / LiveDiscoveryBench 任务共建仓库。

## Contribute / 参与共建

| PR purpose / 用途 | Label / 标签 | Required link / 关联信息 |
| --- | --- | --- |
| New task / 新增任务 | `type:new-task` | Approved Proposal ID and detail URL / 获批 Proposal 编号及详情链接 |
| Task fix / 任务修复 | `type:task-fix` | Existing task ID and problem / 已有任务 ID 及问题 |
| Repository maintenance / 仓库维护 | `type:maintenance` | Maintenance scope; no Proposal / 维护范围，无需 Proposal |

Classify by the change, not the author's role. Maintainers adding tasks also need approved Proposals. Choose a [PR template](CONTRIBUTING.md#templates); a maintainer confirms exactly one type label.

按改动用途而非作者身份分类；管理员新增任务也需获批 Proposal。选择 [PR 模板](CONTRIBUTING.md#templates)，由维护者确认唯一类型标签。

## Task package / 任务包

```text
tasks/<task-id>/
├── instruction.json
├── input/
├── environment/
│   └── environment.json
├── verifier/
│   ├── validation/run/main.py
│   └── test/run/main.py
└── meta.json
```

- `instruction.json`: task instructions, visible inputs, final artifacts, supplied environment, requirements and confirmed limits. / 任务说明、可见输入、最终产物、已提供环境、要求与已确认上限。
- `input/`: Agent-visible data and submission templates only. / 仅放 Agent 可见数据及提交模板。
- `environment/environment.json`: required executable environment contract (`default` or `containerfile`). / 必需的可执行环境合同。
- `verifier/validation/run/main.py`: research feedback via `--input`, `--request`, `--response`. / 研究期间反馈入口。
- `verifier/test/run/main.py`: frozen-submission scoring via `--input`, `--submission`, `--result`. / 冻结提交后的最终评分入口。
- `meta.json`: task identity, immutable construction source, data sources, raw metric, optional conversion and measured baseline. / 任务身份、不可变构造来源、数据来源、原始指标及可选转换与实测 baseline。

Exactly five top-level parts. Keep build history, baseline implementations and review reports outside the package. Both verifier entries are required; `verifier/run/main.py` is obsolete. The framework supplies the shared run-local `VerifyContext`; this repository does not provide an evaluation runtime.

顶层严格五部分；构造历史、baseline 实现及审核报告放在包外。双入口均必需，旧 `verifier/run/main.py` 不再使用。共享的 Run-local `VerifyContext` 由框架提供，本仓库不提供评测运行环境。

Copy `tasks/_template/`, rename it and replace all placeholders. The template deliberately has no working scientific verifier. CI checks structure only, never executes task code, and does not establish scientific approval or runtime readiness. See [CONTRIBUTING.md](CONTRIBUTING.md).

复制 `tasks/_template/`、重命名并替换占位内容。模板不提供可用的科学评分器；CI 仅检查结构，不执行任务代码，不代表科学准入或可运行性。详见[共建指南](CONTRIBUTING.md)。
