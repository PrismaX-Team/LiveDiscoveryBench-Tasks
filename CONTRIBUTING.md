# Contributing / 共建指南

<a id="templates"></a>
## PR templates / PR 模板

Choose a template when comparing branches, or copy its contents into the PR body. Template selection neither grants approval nor sets labels; a maintainer confirms one type label.

比较分支时选择模板，或复制模板内容到 PR 正文。选择模板不代表批准，也不会自动设置标签；维护者确认唯一类型标签。

| Purpose / 用途 | Start / 开始创建 | Template / 模板 |
| --- | --- | --- |
| New task / 新增任务 | [Compare](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/compare?expand=1&template=new_task.md) | [new_task.md](.github/PULL_REQUEST_TEMPLATE/new_task.md) |
| Task fix / 任务修复 | [Compare](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/compare?expand=1&template=task_fix.md) | [task_fix.md](.github/PULL_REQUEST_TEMPLATE/task_fix.md) |
| Maintenance / 仓库维护 | [Compare](https://github.com/PrismaX-Team/LiveDiscoveryBench-Tasks/compare?expand=1&template=maintenance.md) | [maintenance.md](.github/PULL_REQUEST_TEMPLATE/maintenance.md) |

### New task / 新增任务 — `type:new-task`

Submit a website Proposal and receive Admin approval (`approved_for_pr`). Copy `tasks/_template/` to `tasks/<task-id>/`; add one task per PR without unrelated repository changes. Fill in the approved Proposal ID (e.g. `LDBP-2026-000001`) and website detail URL. Create the GitHub PR, then bind its URL from the approved Proposal page. Maintainers adding tasks follow the same process.

先在网站提交 Proposal 并获 Admin 批准（`approved_for_pr`）。复制 `tasks/_template/` 到 `tasks/<task-id>/`，一个 PR 仅新增一道任务，不混入无关仓库改动。填写获批 Proposal 编号（如 `LDBP-2026-000001`）及站内详情链接；创建 GitHub PR 后回到获批 Proposal 页面绑定 PR 链接。管理员新增任务也走同样流程。

The Proposal remains private: its URL does not grant access. Do not copy private proposal material into the public PR. / Proposal 始终私有，链接不授予访问权限；不要把私有提案材料复制到公开 PR。

### Task fix / 任务修复 — `type:task-fix`

Reference one existing task ID; describe the defect, correction, verification and impact on previous scores. No new Proposal is required. Ask an Admin to register the fix against the existing task on the website. The original merged PR stays merged. Both new tasks and fixes require Domain and Technical review.

关联一个已有任务 ID，说明缺陷、修复、验证及对旧分数的影响；无需新 Proposal。请 Admin 在网站为已有任务登记修复 PR；原 PR 保持已合并。新增任务及修复均走 Domain 与 Technical 双审。

### Repository maintenance / 仓库维护 — `type:maintenance`

Documentation, CI, templates and configuration need no Proposal and do not enter the website task PR board. Mechanical maintenance may touch multiple existing packages; explain the scope and validate all affected packages. Do not use maintenance to introduce new tasks or bypass scientific/scoring review. Split mixed-purpose work into separate PRs.

文档、CI、模板及配置维护无需 Proposal，不进入网站任务 PR 看板。机械性维护可涉及多个已有包，须说明范围并检查所有受影响包。不得借维护新增任务或绕过科学内容、评分逻辑审核；不同用途的改动分开提 PR。

## Package preparation / 准备任务包

- Use the five-part layout. Directory name and `meta.json.id` must match: `^[a-z0-9][a-z0-9._-]{0,127}$`. / 使用五部分结构，目录名与 `meta.json.id` 一致并匹配该格式。
- Use `instructions`, not `objective` or `custom_environment`. Submission templates use artifact-relative paths under `input/`; `has_template` defaults to true. / 不增加旧字段；提交模板按产物相对路径存于 `input/`，不适合提供模板时才写 `has_template: false`。
- `environment/environment.json` is required. Default: `{"schema_version":"1.0","type":"default"}`, with no other environment files. Custom: `{"schema_version":"1.0","type":"containerfile","containerfile":"Containerfile"}`, alongside its build file/dependencies. / 环境声明必需；默认环境目录只能有此 JSON，自定义环境另放构建文件及依赖。
- Implement both verifier entries as offline, deterministic programs. Validation uses bounded JSON request/response files; Test scores a frozen submission. Define feedback, budgets and scoring in the task; the framework supplies shared run-local `VerifyContext`. / 双入口须离线且确定性；Validation 使用有上限的 JSON 请求/响应，Test 对冻结提交评分；反馈、预算与评分由任务定义，共享状态由框架提供。
- Record an immutable `source_id`; leave unclassified `metric.type` as null and unconfirmed operational limits as `{}`. Do not invent transform parameters or measured baselines. / 记录不可变构造来源；未分类类型写 null，未确认资源上限写 `{}`，不编造转换参数或实测 baseline。
- Only commit redistributable material. The repository and PRs are public. Hidden-from-Agent data is not automatically safe to publish; agree a permitted delivery route for nonpublic scoring data with maintainers. / 仅提交可再分发材料；仓库及 PR 均公开。对 Agent 隐藏的数据不等于可以公开，非公开评分数据先与维护者确认合法交付方式。

## Maintainer checklist / 合并前人工核对

1. Confirm purpose and exactly one type label, independent of author role. / 确认用途及唯一类型标签，不因管理员身份豁免流程。
2. For new tasks, open the private Proposal with an authorized account; confirm approval, author and consistency with the PR. GitHub creation itself is not blocked, and CI does not query website approval. / 新增任务：用有权限账号核对私有 Proposal 的批准、作者及与 PR 的一致性；网站不阻止直接开 GitHub PR，CI 不查询批准状态。
3. Confirm the real GitHub PR exists, belongs here, matches the registered author and contains the intended task. Binding currently checks URL format only. / 核对真实 PR 存在、属于本仓库、作者与登记一致、内容对应；网站绑定目前只检查 URL 格式。
4. For task PRs, confirm both review seats approved the latest changes and current CI passed. Merge on GitHub, then manually synchronize CI/GitHub status on the website; a website status update does not merge a PR. / 任务 PR：最新改动须通过站内双审及当前 CI；在 GitHub 合并，再人工同步站内状态，站内更新不执行合并。
5. Review maintenance on GitHub without registering it as a task contribution. No label or CI result substitutes for manual review. / 维护 PR 在 GitHub 审核，不登记为任务贡献；标签及 CI 不代替人工核对。

## CI boundary / CI 边界

CI requires one type label and checks affected package structure, JSON, environment declarations and both verifier paths. No task code is imported or executed, no dependencies installed, images built or archives unpacked. PRs use the checker from the base commit; checker changes take effect after merge and must be tested locally before merging. CI does not prove scientific validity, runtime correctness or Proposal approval, nor does it configure branch protection.

CI 要求唯一类型标签，检查受影响包的结构、JSON、环境声明及双入口；不导入或执行任务代码、不安装依赖、不构建镜像、不解压。PR 使用目标分支提交的检查器；检查器改动合并后生效，维护者合并前本地测试。CI 不证明科学有效性、运行正确性或 Proposal 获批，也不会自动配置分支保护。

```sh
python3 -I .github/scripts/test_task_structure.py
python3 -I .github/scripts/task_structure.py .
```
