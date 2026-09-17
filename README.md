# Science Innovation Exam Tasks

Task contribution repository for Science Innovation Exam. / Science Innovation Exam 任务共建仓库。

[Official portal / 官网](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/) · [Submit Proposal / 提交 Proposal](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/new?category=proposals) · [How to submit a task PR / 如何提交任务 PR](CONTRIBUTING.md)

## Contribute / 参与共建

Submit a Proposal first. Once it is approved, follow [CONTRIBUTING.md](CONTRIBUTING.md): copy `tasks/_template/`, optionally let an AI agent build the package with the skill in `contributor/build-sie-task-package/`, run the local check, and open a PR from your fork. / 先提交 Proposal；获批后按[共建指南](CONTRIBUTING.md)操作：复制 `tasks/_template/`，可用 `contributor/build-sie-task-package/` 中的 Skill 让 AI 协助构建，运行本地检查，再从 fork 提交 PR。

| PR purpose / 用途 | Label / 标签 | Required link / 关联信息 |
| --- | --- | --- |
| New task / 新增任务 | `type:new-task` | Currently approved public Discussion URL / 当前有效获批的公开 Discussion 链接 |
| Task fix / 任务修复 | `type:task-fix` | Existing task ID and problem / 已有任务 ID 及问题 |
| Repository maintenance / 仓库维护 | `type:maintenance` | Maintenance scope; no Proposal / 维护范围，无需 Proposal |

Classify by the change, not the author's role. Maintainers adding tasks also need approved Proposals. Choose a [PR template](CONTRIBUTING.md#templates); a maintainer confirms exactly one type label. Step-by-step instructions are in [CONTRIBUTING.md](CONTRIBUTING.md); maintainer rules are in [MAINTAINERS.md](MAINTAINERS.md).

按改动用途而非作者身份分类；管理员新增任务也需获批 Proposal。选择 [PR 模板](CONTRIBUTING.md#templates)，由维护者确认唯一类型标签。分步说明见[共建指南](CONTRIBUTING.md)，维护者规则见 [MAINTAINERS.md](MAINTAINERS.md)。

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
- `meta.json`: task identity, task sources, raw metric, optional conversion and measured baseline. / 任务身份、任务来源、原始指标及可选转换与实测 baseline。

Exactly five top-level parts. Keep build history, baseline implementations and review reports outside the package. Both verifier entries are required; `verifier/run/main.py` is obsolete. The framework supplies the shared run-local `VerifyContext`; this repository does not provide an evaluation runtime.

顶层严格五部分；构造历史、baseline 实现及审核报告放在包外。双入口均必需，旧 `verifier/run/main.py` 不再使用。共享的 Run-local `VerifyContext` 由框架提供，本仓库不提供评测运行环境。

Copy `tasks/_template/`, rename it and replace all placeholders. The template deliberately has no working scientific verifier. `contributor/build-sie-task-package/` is a skill for AI coding agents that fills the package from an approved Proposal and bundles the contract schemas and a local checker (`scripts/check_package.py`). The trusted gate checks structure, Proposal approval and current dual reviews without executing task code; it does not establish scientific validity or runtime readiness. See [CONTRIBUTING.md](CONTRIBUTING.md).

复制 `tasks/_template/`、重命名并替换占位内容。模板不提供可用的科学评分器。`contributor/build-sie-task-package/` 是给 AI 编程助手的 Skill，可根据获批 Proposal 填写任务包，并附带合同 schema 与本地检查脚本（`scripts/check_package.py`）。可信检查器校验结构、Proposal 批准和当前双审，不执行任务代码，不代表科学有效性或可运行性。详见[共建指南](CONTRIBUTING.md)。

## Website contribution data / 官网共建数据

This repository owns `data/contributions.json` on its `gh-pages` branch. The **Update contribution snapshot** workflow reads public Discussions and PRs, saves the JSON, then deploys the existing static site with the refreshed data. It runs after contribution governance/review workflows, on relevant Discussion events, on `portal-updated` repository dispatch, hourly, and on manual dispatch from `main`. It uses only this repository's `GITHUB_TOKEN`; no cross-repository token is required for data updates.

公开共建数据保存在本仓库 **gh-pages 分支**的 `data/contributions.json`，不写入受保护的 main。**Update contribution snapshot** 使用本仓库自己的 Token，读取公开 Proposal/PR、保存数据并直接部署已有静态网页，不重新构建官网。贡献审核完成、Discussion 变化、收到 `portal-updated` 事件、每小时及手动运行都会触发；无需为数据同步配置跨仓库 Token。手工推送网页产物后需手动运行一次此 Action。

Pages publishing source must be **GitHub Actions**, with `main` and `gh-pages` permitted by the `github-pages` environment. Website source code remains in the separate private website repository. / Pages 发布来源设置为 **GitHub Actions**；`github-pages` 环境允许 main 与 gh-pages 分支部署。网站源码继续保存在独立私有仓库。
