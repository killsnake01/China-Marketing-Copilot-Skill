# 维护和发布指南

> 用途：承接 README 不应展示给下载者的维护内容，包括资源地图、更新流程、发布校验和扩展纪律。面向 Skill 维护者、平台发布者和二次开发者。

## 维护原则

- 首页只展示下载价值、典型输入、首屏交付和能力边界。
- `SKILL.md` 保持路由器形态，细节进入 `docs/routes/`、`docs/templates/`、`docs/evals/` 和 `scripts/`。
- 新增能力要同时补模板、样本、脚本或校验入口，避免只写说明。
- 发布包只保留当前版本 `dist-v*` 产物，历史产物移到临时备份区。
- 外部搜索、浏览器、微博、新闻和平台后台能力都按增强能力处理，不能写成默认依赖。

## 资源地图

| 层级 | 主要文件 | 维护职责 |
|------|----------|----------|
| 技能入口 | `SKILL.md`; `agents/openai.yaml` | 触发、运行合约、最小路由和界面元数据 |
| 下载展示 | `README.md`; `docs/platform-listing.md` | 平台详情页、安装理由、示例输入和能力边界 |
| 平台字段 | `docs/platform-publish-fields.json`; `scripts/validate_platform_fields.py` | ClawHub、SkillHub、GitHub、Codex 的标题、副标题、短描述、版本和包名一致性 |
| 路由层 | `docs/agent-router.md`; `docs/routes/*.md` | 用户任务到模板、品类索引和校验脚本的选择 |
| 正式物料分层 | `docs/templates/audience-layering.md`; `docs/evals/audience-layering-samples.json`; `scripts/evaluate_audience_layering.py` | 区分前台可见内容、演讲者备注与内部附录，拦截审核语言泄露 |
| 运行能力 | `docs/runtime-capabilities.json` | 纯文档、脚本增强和联网增强三种环境的能力选择与回退 |
| 决策模板 | `assets/launch-decision-card.md`; `docs/templates/launch-decision-package.md`; `docs/templates/executive-decision-memo.md`; `docs/templates/route-scorecard.md`; `docs/templates/risk-ledger.md`; `docs/templates/route-switch-playbook.md`; `docs/templates/decision-consistency-gate.md` | 完整上市决策包、管理层纪要、路线评分、风险因果链和切换剧本 |
| 事实纪律 | `docs/templates/evidence-freshness-gate.md`; `docs/evals/evidence-claim-samples.json`; `docs/data-sources.json`; `docs/evidence-ledger.json` | 高时效事实复核、主张降级、数据时效与来源可追溯台账 |
| 负面预警 | `docs/ecosystem/negative-early-warning.md`; `docs/ecosystem/negative-signal-rules.json`; `docs/evals/negative-signal-samples.md`; `docs/evals/negative-propagation-samples.json` | 负面信号、否定语境、独立账号、速度、跨平台、业务影响、重复噪声和阶段校准 |
| 知识库 | `knowledge-base/mobile/_index.md`; `knowledge-base/headphones/_index.md`; `knowledge-base/laptops/_index.md`; `knowledge-base/wearables/_index.md`; `knowledge-base/smart-home/_index.md`; `knowledge-base/other/_index.md` | 品类事实、竞品结构、传播风险和数据覆盖 |
| 评测层 | `docs/evals/*.json`; `docs/evals/*.md`; `assets/examples/*.md` | 样本、黄金输出、质量评分和回归测试 |
| 跨智能体盲测 | `docs/evals/cross-agent-benchmark.json`; `scripts/evaluate_cross_agent_runs.py` | 比较 Codex、OpenClaw、Hermes 和 GPT 的触发、路由、证据纪律与交付质量 |
| 旧用法兼容 | `docs/evals/legacy-compatibility-samples.json`; `scripts/evaluate_legacy_compatibility.py` | 固定v1.3.7常用提示词、默认模式、熟悉交付和高级模块展开边界 |
| 发布层 | `CHANGELOG.md`; `SECURITY.md`; `RELEASE-MANIFEST.json`; `RELEASE-VALIDATION.json`; `scripts/build_publish_package.py`; `scripts/verify_release_artifacts.py` | 版本说明、安全边界、真实验证报告和三平台运行包 |

## 核心发布命令

```bash
python3 -B scripts/validate_skill_pack.py --write-report
python3 -B scripts/build_release_manifest.py --check
python3 -B scripts/build_publish_package.py --platform all --check
python3 -B scripts/verify_release_artifacts.py --build-temp
python3 -B scripts/validate_platform_fields.py
python3 -B scripts/check_internal_links.py
python3 -B scripts/audit_script_safety.py
python3 -B scripts/audit_evidence_ledger.py
python3 -B scripts/evaluate_cross_agent_runs.py --check
python3 -B scripts/evaluate_cross_agent_runs.py --self-test
python3 -B scripts/evaluate_legacy_compatibility.py
python3 -B scripts/evaluate_audience_layering.py --check
python3 -B scripts/install_local.py --self-test
```

生成供四端盲测的候选包：

```bash
python3 -B scripts/build_publish_package.py --platform all-with-personal --output candidate-v{version} --format zip --candidate
```

真实运行闸门通过后生成正式三平台包：

```bash
python3 -B scripts/build_publish_package.py --platform all-with-personal --output dist-v{version} --format zip
python3 -B scripts/verify_release_artifacts.py --output dist-v{version}
```

## 发布包分层

- GitHub 保留完整源码、维护文档、黄金样例、发布脚本和验证脚本。
- Codex、ClawHub 和 SkillHub 使用运行包，只包含技能入口、运行路由、模板、知识库、必要样本和执行脚本。
- Hermes 个人全量运行版保留全部品类知识库、生态资料、路由、模板、参考文件、运行评测、黄金样例、Schema 和执行脚本；移除构建发布、仓库审计、盲测题库、Git 元数据、历史发布包、缓存和系统垃圾文件。
- 跨智能体盲测题库与评分器只留在源码仓库，不进入任何待测安装包，防止答案泄漏。
- 旧用法兼容合同和校验器只留在源码仓库，不增加用户运行包上下文。
- `quickstart-example.md`、维护指南、平台发布路由、构建脚本和仓库级校验脚本不进入运行包。
- SkillHub 根目录继续过滤平台拒收的 `LICENSE` 和 `VERSION`，许可证文本改放在 `docs/package-license.txt`。
- 每个运行包构建后都执行独立的内部引用检查，防止瘦身后出现断链。

## 样本和脚本对应关系

| 能力 | 样本 | 校验脚本 |
|------|------|----------|
| 触发路由 | `docs/evals/trigger-queries.json` | `scripts/validate_skill_pack.py` |
| 负面传播批次 | `docs/evals/negative-propagation-samples.json` | `scripts/evaluate_negative_propagation.py` |
| 输出模式 | `docs/evals/output-mode-samples.json` | `scripts/validate_skill_pack.py` |
| 正式物料分层 | `docs/evals/audience-layering-samples.json`; `assets/examples/hypershell-links-boss-proposal.md` | `scripts/evaluate_audience_layering.py --check` |
| 证据时效 | `docs/evals/freshness-claim-samples.json` | `scripts/evaluate_freshness_claims.py --check` |
| 证据主张 | `docs/evals/evidence-claim-samples.json` | `scripts/evaluate_evidence_claims.py --check` |
| 上市决策包 | `docs/evals/decision-package-samples.json` | `scripts/evaluate_decision_package.py --check` |
| 管理层纪要 | `docs/evals/executive-memo-samples.json` | `scripts/evaluate_executive_memo.py --check` |
| 路线评分卡 | `docs/evals/route-scorecard-samples.json` | `scripts/evaluate_route_scorecard.py --check` |
| 风险账本 | `docs/evals/risk-ledger-samples.json` | `scripts/evaluate_risk_ledger.py --check` |
| 路线切换 | `docs/evals/route-switch-samples.json` | `scripts/evaluate_route_switches.py --check` |
| 执行闸门 | `docs/evals/execution-gate-samples.json` | `scripts/evaluate_execution_gate.py --check` |
| 上线后战情 | `docs/evals/post-launch-samples.json` | `scripts/evaluate_post_launch_samples.py --check` |
| 决策学习 | `docs/evals/decision-learning-samples.json` | `scripts/evaluate_decision_learning.py --check` |
| 结构化决策单 | `docs/evals/launch-decision-card-samples.json` | `scripts/validate_decision_output.py --check` |
| 黄金样例 | `docs/evals/golden-example-assertions.json`; `assets/examples/*.md` | `scripts/evaluate_golden_examples.py --check` |
| 质量评分 | `docs/evals/output-quality-rubric.json` | `scripts/evaluate_quality_rubric.py --check` |
| 来源可追溯 | `docs/evidence-ledger.json`; `schemas/evidence-ledger.schema.json` | `scripts/audit_evidence_ledger.py` |
| 跨智能体盲测 | `docs/evals/cross-agent-benchmark.json` | `scripts/evaluate_cross_agent_runs.py --check` 或 `--input runs.jsonl --require-complete` |
| 旧用法兼容 | `docs/evals/legacy-compatibility-samples.json` | `scripts/evaluate_legacy_compatibility.py` |

## 跨智能体盲测流程

1. 用待发布安装包分别安装到 Codex、OpenClaw、Hermes 和 GPT 测试环境。
2. 每次只发送 `docs/evals/cross-agent-benchmark.json` 中的 `prompt`，不发送预期路由、必备词或禁用规则。
3. 按 `agent_package_profiles` 记录待测包指纹，例如运行 `python3 -B scripts/evaluate_cross_agent_runs.py --print-runtime-fingerprint --package-profile codex`、`--package-profile clawhub` 和 `--package-profile hermes-personal`。
4. 把原始结果逐行保存为 JSONL：`case_id`、`agent`、`triggered`、`selected_route`、`selected_mode`、`output`、`captured_at`、`skill_version`、`runtime_package_fingerprint_sha256`。
5. 运行 `python3 -B scripts/evaluate_cross_agent_runs.py --input runs.jsonl --release-gate --summary-output docs/evals/live-release-status.json`。
6. 每个目标智能体完成全部19个案例且通过率达到85%后，正式公开包才会放行；仓库只保存脱敏汇总，原始回答继续留在外部测试记录。

静态命令 `--check` 只验证题库和路由覆盖；`--self-test` 使用76条合成记录检查评分器机械逻辑。两者都不产生兼容性成绩。真实结果保留为独立测试产物，避免写入待测安装包。

## 本机 Codex 安装同步

```bash
python3 -B scripts/install_local.py --check
python3 -B scripts/install_local.py --sync
```

- `--check` 会用当前源码临时构建 Codex 运行包，并逐文件检查本机安装漂移。
- `--sync` 会先把旧安装移动到 `~/.codex/skill-backups/`，再安装当前运行包并复核。
- `--self-test` 只在临时目录验证同步和漂移检测，不修改本机安装。

## 来源升级流程

1. 新资料先登记到 `docs/evidence-ledger.json`，写明发布者、标题、日期、定位信息、适用范围和强制复核字段。
2. 缺少稳定定位信息时保持 `partial`；占位框架保持 `missing`。
3. 知识文件头部写入唯一 `SRC-*` 编号，便于输出回溯来源等级。
4. 只有发布者、日期和稳定定位信息齐全时，才可升级为 `verified`。
5. 更新后运行 `python3 -B scripts/audit_evidence_ledger.py`，再运行总校验。

## 更新流程

1. 先判断本次改动属于展示层、路由层、模板层、schema层、样本层、脚本层、知识库层或发布层。
2. 展示层改动同步更新 `README.md` 和 `docs/platform-listing.md`。
3. 路由层改动同步更新 `SKILL.md`、`docs/agent-router.md` 和相关 `docs/routes/*.md`。
4. 模板层改动同步补样本；能机器判定的能力补脚本。
5. 默认输出、模式选择、术语或路由边界改动同步更新旧用法兼容合同。
6. 负面阶段规则改动同步更新 `schemas/negative-signal-batch.schema.json`、传播样本和批次分析脚本。
7. schema层改动同步更新 `schemas/launch-decision.schema.json`、`scripts/validate_decision_output.py` 和正反样本。
8. 知识库改动同步更新 `docs/data-index.md`、`docs/data-sources.json` 和 `docs/evidence-ledger.json`。
9. 发布层改动同步更新 `VERSION`、`CHANGELOG.md`、`RELEASE-MANIFEST.json` 和三平台包。
10. 运行 `scripts/validate_skill_pack.py --write-report` 生成带时间、源码指纹、Git状态和逐项结果的 `RELEASE-VALIDATION.json`。
11. 结束前运行包级校验和发布产物核验。

## 发布包清理

- 当前发布目录命名为 `dist-v{version}`。
- 正式发布目录默认只保留四个平台 ZIP；解压目录属于可再生成的构建过程文件。
- `dist/` 和旧 `dist-v*` 都属于可再生成产物，不进入 Git。
- 清理历史产物时优先移动到 `/private/tmp/china-marketing-cleanup-*`，保留可回滚路径。
- `git status --ignored --short dist-v{version}` 返回 `!! dist-v{version}/` 时，说明发布包已被忽略规则覆盖。

## 平台填写口径

| 平台 | 使用内容 |
|------|----------|
| GitHub | README 首页、CHANGELOG、SECURITY、源码和验证脚本；字段以 `docs/platform-publish-fields.json` 为准 |
| ClawHub | `dist-v{version}/clawhub-china-marketing-copilot-v{version}.zip`；字段以 `docs/platform-publish-fields.json` 为准 |
| SkillHub | `dist-v{version}/skillhub-china-marketing-copilot-v{version}.zip`；字段以 `docs/platform-publish-fields.json` 为准 |
| Codex 本机 | `SKILL.md`、`agents/openai.yaml` 和包内资源；字段以 `docs/platform-publish-fields.json` 为准 |
| OpenClaw / Hermes | `dist-v{version}/hermes-personal-china-marketing-copilot-v{version}.zip`；解压到 `~/.hermes/skills/china-marketing-copilot/`，字段以 `docs/platform-publish-fields.json` 为准 |

## 安全边界

- 不把 ClawHub、SkillHub、GitHub token 写入仓库。
- 不新增安装钩子、后台进程或默认联网行为。
- 脚本只读取包内文件或用户指定路径。
- 需要外部后台、浏览器或平台发布时，把凭证放在本地环境或平台会话中，不落地到文本文件。
