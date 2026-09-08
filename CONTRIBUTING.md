# Contributing / 共建指南

[Official portal / 官网](https://prismax-team.github.io/LiveDiscoveryBench-Tasks/) · [Submit Proposal / 提交 Proposal](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/new?category=proposals)

## Proposals / 提案

Use the bilingual Proposals Discussion form. Your GitHub account identifies you; no private email is collected. Bodies, links and comments are public. Do not provide sensitive information or material you cannot publish. Earlier private website records have not been migrated publicly.

使用 Proposals 分类中的双语 Discussion 表单，以 GitHub 账号确认身份，不收集私人邮箱。正文、链接和评论均会公开；勿提交敏感信息或无权公开的材料。旧站私有记录未自动公开迁移。

Discuss feedback in comments and edit the original body to revise it. Metric explanations are always visible and required for custom, raw_only or unclassified metrics. Both permissions confirmations are required, including after revisions.

通过评论获得反馈，通过编辑正文修订。指标补充说明始终显示，自定义、仅原始分和未分类时必填；两项授权确认始终必需。

A maintainer other than the author runs **Proposal review** on `main`, supplying the Discussion number, decision and a public reason (20–5000 characters). The Action checks permission and records the actor, decision, exact content fingerprint and run link. Labels display status only. Editing approved content, including reverting an edit, requires renewed approval. The original author then opens the task PR; there is no website binding step.

非作者的维护者在 main 上运行 **Proposal review**，填写 Discussion 编号、决定及 20–5000 字符的公开理由。Action 校验权限并记录操作者、决定、正文摘要及运行链接。标签仅用于展示，不能作为批准凭据。修改获批正文（包括修改后还原）须重新批准；由原作者创建任务 PR，无需回网站绑定。

<a id="templates"></a>
## PR types and reviews / PR 类型与审核

| Purpose / 用途 | Label / 标签 | Required body line / 正文必需行 |
| --- | --- | --- |
| [New task / 新增任务](.github/PULL_REQUEST_TEMPLATE/new_task.md) | `type:new-task` | `Proposal: https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/discussions/NUMBER` |
| [Task fix / 任务修复](.github/PULL_REQUEST_TEMPLATE/task_fix.md) | `type:task-fix` | `Task: EXISTING_TASK_ID` |
| [Maintenance / 仓库维护](.github/PULL_REQUEST_TEMPLATE/maintenance.md) | `type:maintenance` | Describe scope / 说明范围 |

A maintainer confirms exactly one type label. New tasks must match an open, currently approved Proposal in this repository, with the same author. New-task/fix PRs change exactly one task and cannot mix in repository policy changes. Fixes refer to an existing task without another Proposal. Maintenance uses ordinary GitHub review, cannot introduce tasks, and stays off the task board. Scientific/scoring changes belong in task fixes; do not reclassify them as maintenance.

维护者确认唯一类型标签。新增任务须关联本仓库仍开放、有效获批且作者相同的 Proposal。新增/修复只修改一道任务，不混入仓库策略。修复关联已有任务，无需再提 Proposal。维护采用普通 GitHub 审核，不得新增任务且不进入任务看板；科学内容及评分变更应走任务修复。

For tasks, a maintainer posts exactly:

```text
/reviewers domain=@DOMAIN_LOGIN technical=@TECHNICAL_LOGIN
```

The two reviewers must be different and neither may be the PR author. Use GitHub's **Review changes → Approve** for formal decisions. Both seats must approve the current commit. A commit update or dismissed review invalidates the relevant approval. Edit/delete the assignment comment or post a newer one to change seats. An invalid newer assignment fails closed.

两席须由不同且非 PR 作者的账号担任。正式结论使用 GitHub 的 Review changes → Approve；两席须批准当前提交，更新代码或撤回审核后须重新检查。可编辑、删除指定评论或发布更新的指定评论改派；最新指定不合法时检查不通过。

## Package preparation / 准备任务包

- Use the five-part layout. Directory name and `meta.json.id` must match: `^[a-z0-9][a-z0-9._-]{0,127}$`. / 使用五部分结构，目录名与 `meta.json.id` 一致并匹配该格式。
- Use `instructions`, not `objective` or `custom_environment`. Submission templates use artifact-relative paths under `input/`; `has_template` defaults to true. / 不增加旧字段；提交模板按产物相对路径存于 `input/`，不适合提供模板时才写 `has_template: false`。
- `environment/environment.json` is required. Default: `{"schema_version":"1.0","type":"default"}`, with no other environment files. Custom: `{"schema_version":"1.0","type":"containerfile","containerfile":"Containerfile"}`, alongside its build file/dependencies. / 环境声明必需；默认环境目录只能有此 JSON，自定义环境另放构建文件及依赖。
- Implement both verifier entries as offline, deterministic programs. Validation uses bounded JSON request/response files; Test scores a frozen submission. Define feedback, budgets and scoring in the task; the framework supplies shared run-local `VerifyContext`. / 双入口须离线且确定性；Validation 使用有上限的 JSON 请求/响应，Test 对冻结提交评分；反馈、预算与评分由任务定义，共享状态由框架提供。
- Record an immutable `source_id`; leave unclassified `metric.type` as null and unconfirmed operational limits as `{}`. Do not invent transform parameters or measured baselines. / 记录不可变构造来源；未分类类型写 null，未确认资源上限写 `{}`，不编造转换参数或实测 baseline。
- Only commit redistributable material. The repository and PRs are public. Hidden-from-Agent data is not automatically safe to publish; agree a permitted delivery route for nonpublic scoring data with maintainers. / 仅提交可再分发材料；仓库及 PR 均公开。对 Agent 隐藏的数据不等于可以公开，非公开评分数据先与维护者确认合法交付方式。

## Merge boundary / 合并门槛

`Contribution gate` runs trusted default-branch policy, reloads GitHub state and checks type provenance, file changes, task structure, current Proposal approval and two current reviews. It never runs candidate code or unpacks submitted archives. PR, Proposal, assignment and review changes trigger rechecks; a scheduled reconciliation runs every 15 minutes. API errors do not pass the check.

Contribution gate 从默认分支加载可信策略，重新读取 GitHub 状态，校验分类来源、文件变化、结构、当前 Proposal 批准及双审。不会执行候选代码或解压上传文件。PR、Proposal、审核席及 Review 改变均触发重查，每 15 分钟另行对账；API 错误不判通过。

Protect `main` with this required GitHub Actions status, strict up-to-date checks, at least one native review, stale-review dismissal, last-push approval, conversation resolution, administrator enforcement, and no force pushes or deletions. This prevents normal merges with unmet requirements; it does not prevent creating PRs. Event processing has latency: before merging, maintainers must still inspect the latest scientific content and approved scope and wait for the latest gate run.

main 应设置此必需状态检查、分支最新要求、至少一份原生审核、旧审核失效、最后推送批准、讨论解决、管理员同样受限，并禁止强推及删除。这保证条件未满足时不能正常合并，不阻止创建 PR。事件处理存在延迟；维护者合并前仍须核对最新科学内容与获批范围并等待最新检查。

## Task maintenance and portal / 任务维护与官网

Discussion, PR and Review records are the only contribution state. The portal builds a public snapshot hourly and links back to GitHub; failures retain the last successful site. Task and leaderboard records are typed website source. For a broken published task, record bilingual `needs_fix`/`fixing` notes and its fix PR in the website's `src/data/task-maintenance.ts`; it is excluded from both leaderboards until a maintainer verifies the repair merge and restores `active`.

Discussion、PR、Review 是贡献状态的唯一来源。官网每小时构建公开快照并链接 GitHub；失败时保留上一成功版本。任务与榜单由网站类型化文件维护。已发布任务有问题时，在网站 src/data/task-maintenance.ts 记录双语说明、needs_fix/fixing 和修复 PR；修复合并核对后才恢复 active，其间从两处榜单排除。

Acceptance-only Discussions and PRs must start with `[ACCEPTANCE]` and carry `acceptance`; they are excluded from the portal. Close them after checks and never merge fictional tasks. Successful dual review requires two real, different people.

验收条目标题以 [ACCEPTANCE] 开头并带 acceptance 标签，始终不进入官网；验收后关闭，不合并虚构任务。双审成功路径须由两位不同的真实审核者完成。

```sh
python3 -I .github/scripts/test_task_structure.py
python3 -I .github/scripts/test_governance.py
python3 -I .github/scripts/task_structure.py .
```
