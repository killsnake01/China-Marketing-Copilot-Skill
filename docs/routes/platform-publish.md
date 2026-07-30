# 平台发布路由

## 触发

用户要求更新 GitHub、ClawHub、SkillHub、Codex 本机安装版，或要求“发布”“上传”“同步版本”“构建 zip 包”。

## 读取顺序

1. `README.md`
2. `docs/platform-listing.md`
3. `docs/platform-publish-fields.json`
4. `CHANGELOG.md`
5. `SECURITY.md`
6. `VERSION`
7. `RELEASE-MANIFEST.json`
8. `scripts/validate_platform_fields.py`
9. `scripts/validate_skill_pack.py`
10. `scripts/evaluate_evidence_claims.py`
11. `scripts/evaluate_route_switches.py`
12. `scripts/evaluate_execution_gate.py`
13. `scripts/evaluate_golden_examples.py`
14. `scripts/check_internal_links.py`
15. `scripts/audit_script_safety.py`
16. `scripts/build_publish_package.py`
17. `scripts/verify_release_artifacts.py`
18. `docs/evals/live-release-status.json`
19. `scripts/install_local.py`

## 必备输出

- 当前版本号和目标平台。
- 平台字段台账校验结果：标题、副标题、短描述、slug、版本、包名和展示顺序。
- 发布前验证结果。
- 证据主张样本结果。
- 路线切换样本结果。
- 执行闸门样本结果。
- 黄金样例断言结果。
- 四端真实运行闸门状态、运行包指纹和脱敏记录数。
- 包内引用完整性检查结果。
- 脚本安全审计结果。
- 发布产物核验结果。
- GitHub 源码、ClawHub 包、SkillHub 包和 Codex 本机安装版的处理状态。
- 生成的发布包路径和 zip 路径。
- 平台字段：`slug`、`version`、`displayName`、技能显示名。
- 平台详情文案：标题、副标题、短简介、示例提问和能力边界。
- 密钥处理方式：只在命令环境或平台输入框使用，禁止写入仓库文件。
- 可信度材料：更新记录、安全边界、发布清单和校验结果。
- 发布后核验项：线上版本、显示名、简介、下载入口、评测报告或后台状态。

## 平台规则

| 平台 | 包形态 | 关键规则 |
|------|--------|----------|
| GitHub | 当前仓库源码 | 保留 `README.md`、`LICENSE`、`VERSION`、脚本和验证文件 |
| ClawHub | `scripts/build_publish_package.py --platform clawhub` 输出目录或 zip | 使用中文显示名和当前版本，上传前跑包级验证 |
| SkillHub | `scripts/build_publish_package.py --platform skillhub` 输出 zip | 构建时临时补 `slug/version/displayName`，过滤平台拒收的 `.gitignore`、`LICENSE`、`VERSION` |
| Codex 本机 | `scripts/install_local.py --sync` | 旧安装先移入备份目录，再逐文件确认与当前 Codex 运行包一致 |

## 执行纪律

- 先运行 `python3 -B scripts/validate_skill_pack.py`。
- 如更新平台字段、标题、副标题、短描述、版本或包名，先运行 `python3 -B scripts/validate_platform_fields.py`。
- 如更新证据主张纪律，单独运行 `python3 -B scripts/evaluate_evidence_claims.py --check` 快速确认标注、降级和拦截动作。
- 如更新路线切换剧本，单独运行 `python3 -B scripts/evaluate_route_switches.py --check` 快速确认继续、缩窄、切换和暂停动作。
- 如更新执行闸门规则，单独运行 `python3 -B scripts/evaluate_execution_gate.py --check` 快速确认三类上线、调整或暂停判断。
- 如更新样例，单独运行 `python3 -B scripts/evaluate_golden_examples.py --check` 快速确认黄金样例断言。
- 如只改文案或路由，单独运行 `python3 -B scripts/check_internal_links.py` 快速确认无断链。
- 如新增或修改脚本，单独运行 `python3 -B scripts/audit_script_safety.py` 快速确认无高风险脚本行为。
- 盲测前用 `--candidate` 生成候选包；四端完整运行后把脱敏汇总写入 `docs/evals/live-release-status.json`。
- 正式构建运行 `python3 -B scripts/build_publish_package.py --platform all`；真实运行闸门未通过时脚本应主动阻断。
- 构建后运行 `python3 -B scripts/verify_release_artifacts.py`，确认当前 dist 只有当前版本三平台目录和 zip。
- 上传平台前确认 `RELEASE-MANIFEST.json` 版本和 `VERSION` 一致。
- 上传平台前确认 `docs/platform-publish-fields.json` 的 version、package_name 和当前发布包一致。
- 发布包只使用脚本生成目录，避免手动删文件造成遗漏。
- token、key 和登录态只用于本次发布流程，不能写入 README、脚本、日志或样例。
