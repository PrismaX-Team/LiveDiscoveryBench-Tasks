# Contributing a task / 提交任务

[Official portal / 官网](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/) · [Submit Proposal / 提交 Proposal](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/new?category=proposals) · [Task contract / 任务合同](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/en/contribute/task-contract/) ([中文](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/zh/contribute/task-contract/))

A task enters Science Innovation Exam in two steps: a public **Proposal** that is reviewed by a domain expert, then a **task PR** that adds the five-part task package and is reviewed by a domain expert and a technical expert. This page explains the PR step. Maintainer rules live in [MAINTAINERS.md](MAINTAINERS.md).

任务分两步进入 Science Innovation Exam：先提交公开 **Proposal**，由一位领域专家审核；获批后再提交**任务 PR**，加入五部分任务包，由一位领域专家和一位技术专家审核。本页说明 PR 这一步；维护者规则见 [MAINTAINERS.md](MAINTAINERS.md)。

## 1. Before you start / 开始之前

You need an **approved Proposal of your own** in this repository. Open one with the bilingual Proposals Discussion form if you have not yet; bodies, links and comments are public, so do not include sensitive material or anything you cannot publish. When a maintainer approves it, the bot posts a comment with the next steps and a prefilled PR link. Editing an approved Proposal suspends its approval.

你需要一份**本人已获批的 Proposal**。若还没有，请通过 Proposals 分类的双语 Discussion 表单提交；正文、链接与评论都会公开，请勿放入敏感或无权公开的材料。维护者批准后，机器人会在讨论串中给出下一步说明和预填好的 PR 链接。修改已获批的 Proposal 会使批准暂停。

One approved Proposal becomes one task package and one PR. / 一份获批 Proposal 对应一个任务包和一个 PR。

## 2. Understand the task contract / 了解任务合同

A task package has exactly five top-level parts:

```text
tasks/<task-id>/
├── instruction.json   what the agent reads before starting
├── input/             agent-visible data and submission templates
├── environment/       environment.json (default image or Containerfile)
├── verifier/          validation/run/main.py and test/run/main.py
└── meta.json          identity, task sources, raw metric, baseline
```

The portal's [task contract page](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/en/contribute/task-contract/) ([中文](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/zh/contribute/task-contract/)) walks through an annotated example and explains what every field is for and how to fill it. Read it once before touching the template. The English working copy of the field rules is [contributor/build-sie-task-package/task-contract.md](contributor/build-sie-task-package/task-contract.md).

官网的[任务合同详情页](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/zh/contribute/task-contract/)用一个带注释的示例逐项说明每个字段是做什么的、该怎么填。动手前先读一遍。字段规则的英文工作副本见 [contributor/build-sie-task-package/task-contract.md](contributor/build-sie-task-package/task-contract.md)。

## 3. Get the template and the skill / 获取模板与 Skill

Fork this repository and clone your fork. Everything you need is already inside it:

先 Fork 本仓库并克隆你的 fork。需要的东西都已经在仓库里：

| What / 内容 | Path / 路径 |
| --- | --- |
| Empty, structurally valid package / 空的合法任务包模板 | [`tasks/_template/`](tasks/_template/) |
| Skill for an AI coding agent (Cursor, Codex, Claude Code) / 给 AI 编程助手的 Skill | [`contributor/build-sie-task-package/`](contributor/build-sie-task-package/) |
| Extra-software example (Containerfile) / 额外软件示例 | [`contributor/build-sie-task-package/examples/environment-containerfile/`](contributor/build-sie-task-package/examples/environment-containerfile/) |
| Local structural check / 本地结构检查 | [`contributor/build-sie-task-package/scripts/check_package.py`](contributor/build-sie-task-package/scripts/check_package.py) |

```sh
git clone https://github.com/<you>/LiveDiscoveryBench-Tasks.git
cd LiveDiscoveryBench-Tasks
git checkout -b task/<task-id>
cp -r tasks/_template tasks/<task-id>
```

To let an agent help, copy the skill directory into your agent's skills folder (for example `.cursor/skills/build-sie-task-package/` or `~/.codex/skills/build-sie-task-package/`), put the approved Proposal text and your materials (papers, data, code, licences) next to the package, and ask: “Use `build-sie-task-package` to prepare the task package for `tasks/<task-id>` from the proposal and materials.” The skill fills what your materials support and asks for the facts that would change the science, the score or the contract. Keep construction notes and tests outside `tasks/<task-id>/`.

若希望 AI 协助，把 Skill 目录拷到助手的 skills 目录（如 `.cursor/skills/build-sie-task-package/` 或 `~/.codex/skills/build-sie-task-package/`），把已获批的 Proposal 全文和材料（论文、数据、代码、许可）放在任务包旁边，然后说：“按 `build-sie-task-package`，根据 proposal 和材料为 `tasks/<task-id>` 准备任务包。”Skill 会先填材料能支持的部分，缺会改变科学、分数或合同的事实时再问你。构建笔记和测试放在 `tasks/<task-id>/` 之外。

## 4. Build and check the package / 构建并检查任务包

- `<task-id>` is a short slug: lowercase start, then lowercase, digits, `.`, `_`, `-`; at most 128 characters. Directory name and `meta.json.id` must match. / `<task-id>` 为短 slug：小写字母开头，只含小写、数字、`.`、`_`、`-`，最长 128 字符；目录名与 `meta.json.id` 一致。
- The package is English, even if the Proposal is Chinese. / 任务包内文本为英文，即使 Proposal 是中文。
- `input/` holds only agent-visible data and submission templates. Hidden scoring data lives under `verifier/test/`; validation and test must be self-contained. / `input/` 只放 Agent 可见数据与提交模板；隐藏评分数据放在 `verifier/test/` 下，validation 与 test 必须自包含。
- Both `verifier/validation/run/main.py` and `verifier/test/run/main.py` are required and must run offline and deterministically. / 双入口均必需，须离线、确定性运行。
- Keep the default image unless every extra package has a pinned version; then switch `environment/` to the Containerfile example. / 除非每个额外软件都有固定版本，否则保持默认镜像；需要时再换成 Containerfile 示例。
- Do not invent hidden labels, scoring formulas, baseline numbers or licences. Leave `metric.type` as `null` and `limitation` as `{}` when not confirmed. / 不编造隐藏标签、评分公式、baseline 数值或许可；未确认时 `metric.type` 写 `null`，`limitation` 写 `{}`。
- Commit only redistributable material; the repository and every PR are public. / 只提交可再分发的材料；仓库和 PR 均公开。

Run the same checks CI runs before pushing:

```sh
python3 contributor/build-sie-task-package/scripts/check_package.py tasks/<task-id>
python3 -I .github/scripts/task_structure.py .
```

A green check means the directory loads. Scientific validity and whether the verifier actually scores correctly are judged in review. / 绿灯只表示目录能被加载；科学有效性和 verifier 是否正确评分由审核判断。

## 5. Open the pull request / 提交 PR

1. Push your branch to your fork. / 把分支推到你的 fork。
2. Open the PR against `PrismaX-Team/LiveDiscoveryBench-Tasks` `main`. The easiest way is the **Create task PR** link in the bot's approval comment on your Proposal: click **compare across forks**, pick your fork and branch, and the description already contains the required `Proposal:` line. / 向 `PrismaX-Team/LiveDiscoveryBench-Tasks` 的 `main` 发起 PR。最简单的方式是点击 Proposal 讨论串中机器人评论里的 **Create task PR** 链接：点 **compare across forks**，选择你的 fork 和分支，正文已带上必需的 `Proposal:` 行。
3. If you open the PR another way, use the [new task template](.github/PULL_REQUEST_TEMPLATE/new_task.md) (`?template=new_task.md`) and make sure the body contains exactly one line: / 若从其他入口创建，请选择[新增任务模板](.github/PULL_REQUEST_TEMPLATE/new_task.md)（`?template=new_task.md`），并确保正文含有这一行：

   ```text
   Proposal: https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/NUMBER
   ```

4. Title the PR `[task] <task-id>` and describe what the package contains and how you validated the verifier. / PR 标题写 `[task] <task-id>`，正文说明任务包内容和 verifier 的验证方式。

One PR changes exactly one task directory and nothing else. / 一个 PR 只改动一个任务目录，不改其他文件。

## 6. What happens next / 之后会发生什么

1. **CI** checks the package structure and that the PR links your currently approved Proposal. It never runs your code. / **CI** 检查结构和 Proposal 关联，不执行你的代码。
2. A maintainer sets the `type:new-task` label and assigns two reviewers with `/reviewers domain=@… technical=@…`. / 维护者设置 `type:new-task` 标签并指定两位审核者。
3. The **domain reviewer** checks the science and the metric; the **technical reviewer** checks the implementation, environment and verifier determinism. Both must approve the current commit; pushing new commits asks for renewed approval. / **领域审核者**核对科学与指标，**技术审核者**核对实现、环境与 verifier 确定性。两位都须批准当前提交；再推送新提交需重新批准。
4. After merge the task appears on the portal with you credited as contributor. Later repairs go through task-fix PRs. / 合并后任务出现在官网并署名。后续修复走任务修复 PR。

Progress is visible on the [portal's contribution board](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/en/contribute/#contribution-activity) and in the PR itself. / 进展可在[官网共建看板](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/zh/contribute/#contribution-activity)和 PR 中查看。

<a id="templates"></a>
## Other PR types / 其他 PR 类型

| Purpose / 用途 | Template / 模板 | Required body line / 正文必需行 |
| --- | --- | --- |
| New task / 新增任务 | [`new_task.md`](.github/PULL_REQUEST_TEMPLATE/new_task.md) | `Proposal: https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/NUMBER` |
| Task fix / 任务修复 | [`task_fix.md`](.github/PULL_REQUEST_TEMPLATE/task_fix.md) | `Task: EXISTING_TASK_ID` |
| Maintenance / 仓库维护 | [`maintenance.md`](.github/PULL_REQUEST_TEMPLATE/maintenance.md) | Describe scope / 说明范围 |

Task fixes touch one existing task and need no new Proposal. Maintenance PRs cannot add tasks. Review rules for each type are in [MAINTAINERS.md](MAINTAINERS.md).

任务修复只改动一道已有任务，无需新 Proposal；维护 PR 不得新增任务。各类型的审核规则见 [MAINTAINERS.md](MAINTAINERS.md)。
