# Contributing tasks / 共建任务

## 1. Obtain Proposal approval / 先获得 Proposal 批准

Submit a Proposal through the LiveDiscoveryBench website. Start a task pull request only after an Admin has marked the Proposal `approved_for_pr`. Keep the public Proposal ID and URL: both are required in the pull request template.

请先在 LiveDiscoveryBench 网站提交 Proposal。只有 Admin 将状态设为 `approved_for_pr` 后，才开始任务 PR。请保存公开 Proposal 编号和地址；PR 模板必须填写两者。

Approval is permission to enter repository review, not a promise of merge or formal publication. Scientific admission, package validation, isolation, deterministic verification, and long-term maintainability remain subject to project review.

批准只表示可以进入仓库审核，不承诺合并或正式发布。科学准入、任务合同、隔离、确定性验证和长期可维护性仍需由项目团队复核。

## 2. Prepare one five-part package / 准备一个五部分任务包

1. Copy `tasks/_template/` to `tasks/<task-id>/`.
2. Use the same task ID in the directory name and `meta.json.id`. It must match `^[a-z0-9][a-z0-9._-]{0,127}$`.
3. Keep exactly the five top-level paths shown in the repository README. Do not add a task-level README, `TASK.md`, baseline, construction history, review material, test report, or source-evidence archive.
4. Replace all template text. Use stable HTTPS links for data sources and supporting materials. Do not commit secrets, credentials, personal data, restricted data, or materials you are not allowed to redistribute.
5. Keep Agent-visible data in `input/`. Keep fixed scoring material owned by the Verifier under `verifier/`; do not create `input/private/`.
6. Make the Verifier offline and deterministic. The repository-wide contract currently fixes only the path `verifier/run/main.py`; do not invent a task-specific invocation protocol in public metadata.

1. 将 `tasks/_template/` 复制为 `tasks/<task-id>/`。
2. 目录名与 `meta.json.id` 使用同一任务 ID，并匹配 `^[a-z0-9][a-z0-9._-]{0,127}$`。
3. 顶层严格保留 README 所列五部分。不要在任务包内加入 README、`TASK.md`、baseline、构造历史、审核材料、测试报告或来源证据全集。
4. 替换全部模板文字；数据来源和支撑材料使用稳定 HTTPS 地址。不要提交 Secret、凭据、个人信息、受限数据或无权再分发的材料。
5. Agent 可见数据放在 `input/`；Verifier 自己管理的固定评分材料放在 `verifier/`，不要建立 `input/private/`。
6. Verifier 必须可离线、确定性运行。当前全局合同只固定 `verifier/run/main.py` 路径，不要在公开元数据中自行发明任务专属调用协议。

## 3. Open the pull request / 提交 PR

Keep a pull request focused on one task package. Complete every field in the pull request template, including the approved Proposal URL, task ID, immutable construction source, stable data sources, and redistribution licenses or terms.

一个 PR 只处理一个任务包。完整填写 PR 模板，包括已批准 Proposal 地址、任务 ID、不可变构造来源、稳定数据来源，以及再分发许可证或条款。

The automated check validates the five required paths, rejects extra task-level paths and symlinks, parses `instruction.json` and `meta.json`, and confirms that `verifier/run/main.py` is non-empty. Passing this check does not validate scientific claims or execute the task.

自动检查会核对五个必需路径、拒绝任务顶层额外路径和符号链接、解析 `instruction.json` 与 `meta.json`，并确认 `verifier/run/main.py` 非空。通过该检查不代表科学主张已经核验，也不会执行任务。
