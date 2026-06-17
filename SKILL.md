---
name: china-marketing-copilot
description: China 3C consumer-electronics marketing copilot for campaign ideation, competitor analysis, product comparison, risk assessment, review/comment data processing, and new-category go-to-market planning. Use when Codex needs China-market marketing strategy for phones, laptops, headphones, wearables, smart home, or adjacent 3C products, especially when the user asks for Chinese social-platform copy, KOL/评测 references, 评论区 risk simulation, anti-AI-tone rewriting, or fact-disciplined 3C insights.
---

# China Marketing Copilot

Use this skill to produce China-market 3C marketing work grounded in the bundled knowledge base. Treat the repository as a controlled context pack, not as general world knowledge.

## Operating Rules

1. Do not invent numbers, rankings, product features, sources, KOL names, or prices.
2. Mark unsupported claims as `知识库暂无此数据` or `[推测]`.
3. For any product comparison, prefer same-source data. If sources differ, state the difference before judging.
4. Check data freshness before making current claims. Prices, rankings, market share, and new-product specs require fresh verification when external search is available.
5. Keep China 3C audience language sharp and concrete. Avoid corporate press-release wording and generic AI phrasing.
6. Do not assume browser-use, web-search, or live platform access exists. Use bundled files first; treat external tools as optional.
7. Before final delivery, run the quality checklist in `docs/templates/quality-check-tools.md`.

## Resource Map

- `docs/data-index.md`: first stop for data coverage, freshness, and file selection.
- `knowledge-base/{category}/_index.md`: category-level brand matrix, price bands, conclusions, and risk notes.
- `docs/templates/strategy-decision-system.md`: brief normalization, strategy diagnosis, route comparison, and campaign architecture.
- `docs/templates/message-house.md`: positioning, claim hierarchy, proof pillars, copy variants, and objection handling.
- `docs/templates/channel-kol-activation.md`: platform roles, KOL brief, content deliverables, comment operations, and measurement.
- `docs/templates/creative-output.md`: campaign ideas, social posts, video scripts, topic plans.
- `docs/templates/insight-output.md`: competitor analysis, data insight, product comparison.
- `docs/templates/risk-assessment.md`: launch, copy, KOL, and comment-section risk checks.
- `docs/templates/new-category-playbook.md`: new-category education and breakout strategy.
- `docs/templates/quality-check-tools.md`: anti-AI-tone rules, fact checklist, confidence footer.
- `docs/references/comment-personas.md`: comment-section persona simulation.
- `docs/references/industry-ecosystem.md`: platform propagation patterns.
- `docs/ecosystem/industry-memes.md`: jargon, memes, overused claims, and avoidance notes.
- `docs/ecosystem/kols.md`: KOL ecosystem and cooperation risk notes.
- `docs/ecosystem/market-signals-2026.md`: static 2026 market sentiment, crisis patterns, AI-hardware narrative, and price-sensitivity signals.
- `docs/ecosystem/negative-early-warning.md`: early negative-signal taxonomy, severity rules, and response actions.
- `docs/ecosystem/negative-signal-rules.json`: machine-readable early negative-signal rules used by preprocessing and evals.
- `docs/evals/negative-signal-samples.md`: calibration samples for updating negative-signal rules.
- `scripts/preprocess.py`: deterministic first-pass cleaning for imported review/comment/spec/risk files.
- `scripts/evaluate_negative_signals.py`: calibration runner for negative-signal rules.
- `scripts/validate_skill_pack.py`: package-level validation before commit or publish.

## Task Routing

### Strategy Diagnosis and Campaign Architecture

Use when the user asks for launch strategy, positioning, campaign direction, "怎么打", "传播怎么做", or gives a vague marketing brief.

1. Read `docs/templates/strategy-decision-system.md`, `docs/data-index.md`, and the relevant category index.
2. Normalize the brief into business goal, target audience, user barrier, evidence, competitor counterattack, platform mechanism, and risk boundary.
3. Compare at least two routes and explicitly state the recommended route, backup route, and route to avoid.
4. Include first 72-hour actions, 7-day follow-up, negative early-warning signals, and confidence.

### Messaging, Positioning, and Copy Architecture

Use when the user asks for positioning, slogan, headline, social copy, launch talking points, product-page messaging, KOL talking points, or wants copy rewritten for China 3C audiences.

1. Read `docs/templates/message-house.md`, `docs/templates/strategy-decision-system.md`, and relevant proof sources.
2. Build one core claim, three proof pillars, user benefit, objection handling, platform copy variants, and forbidden expressions.
3. Keep claim language specific, source-aware, and resistant to parameter-party teardown.
4. Use `docs/templates/quality-check-tools.md` before final copy.

### Channel and KOL Activation

Use when the user asks for KOL brief, seeding plan, platform rollout, launch calendar, content deliverables, review embargo plan, or social activation.

1. Read `docs/templates/channel-kol-activation.md`, `docs/templates/message-house.md`, `docs/references/industry-ecosystem.md`, and `docs/ecosystem/kols.md`.
2. Split platform roles, KOL types, deliverables, must-say points, forbidden expressions, comment operations, risk triggers, and review metrics.
3. Treat browser-use and live platform lookup as optional; if unavailable, use bundled KOL and platform references with `[待验证]` for current candidates.

### Creative Campaigns

Use when the user asks for ideas, campaign concepts, social copy, seeding, topic planning, or launch communication.

1. Identify category, product, target user, platform, budget level, and forbidden claims. Ask only when a missing input changes the risk materially.
2. Read `docs/data-index.md`, the relevant `knowledge-base/{category}/_index.md`, `docs/templates/creative-output.md`, `docs/templates/message-house.md`, `docs/templates/quality-check-tools.md`, and platform/persona references as needed.
3. Read `docs/templates/strategy-decision-system.md` first when the brief affects positioning, launch strategy, route choice, or budget allocation.
4. Use `docs/ecosystem/market-signals-2026.md` when the idea touches holidays, KOLs, AI hardware, price/subsidy, or public-emotion risks.
5. Generate ideas from data-backed advantages, user pain points, comment reactions, competitor gaps, and platform mechanics.
6. Check `docs/templates/used-ideas.md` and avoid repeated hooks.
7. Include quick risk notes and comment-section simulation.

### Competitor Analysis, Product Comparison, and Market Insight

Use when the user asks who is stronger, what threat a launch creates, which product is worth buying, or what position to take.

1. Read `docs/templates/insight-output.md` and the relevant category file.
2. Build a source-aware matrix for quantitative claims.
3. Separate measured data, subjective evaluation, and inference.
4. Return a one-line conclusion, key findings, data support, audience views, actionable recommendations, and confidence.

### Risk Assessment

Use when the user asks whether a claim, creative, launch, KOL plan, or comparison will backfire.

1. Read `docs/templates/risk-assessment.md`, `docs/references/comment-personas.md`, `docs/ecosystem/industry-memes.md`, `docs/ecosystem/negative-early-warning.md`, and relevant static ecosystem files.
2. Score technical facts, competitor counterattack, platform compliance, comment-section risk, KOL risk, social-emotion boundary risk, and early negative-signal severity when applicable.
3. Simulate at least one skeptical/拆解 comment, one parameter-driven comment, and one normal-user reaction.
4. End with `直接执行`, `调整后执行`, or `暂停重做`.

### Data Import

Use when the user provides review subtitles, comment exports, specs, or risk notes.

1. Read `docs/references/subagent-dataprocessor.md`.
2. Run `scripts/preprocess.py` when working with a local file; use `--mode comments`, `--mode review`, `--mode campaign`, or `--mode document` to reduce false positives.
3. Preserve original wording for user comments and subjective review phrases.
4. Extract negative early-warning signals before summarizing positive findings.
5. When updating negative-signal rules, run `python3 -B scripts/evaluate_negative_signals.py`.
6. Extract findings with source labels and update only the relevant category files.
7. Mark uncertain facts as `[待验证]`.

### Formal Material Review

Use when output may be used in ads, official copy, launch decks, product pages, or KOL briefs.

1. Read `docs/references/subagent-factchecker.md`.
2. Use `docs/ecosystem/market-signals-2026.md` when the material involves a KOL, holiday, AI-hardware claim, or price/subsidy claim.
3. Use `docs/templates/message-house.md` to check claim hierarchy, proof pillars, objections, and forbidden expressions.
4. Audit every number, product claim, absolute phrase, and comparison.
5. Flag unverified items instead of smoothing them over.
6. Prefer a shorter, safer wording when a claim cannot be proven.

## Output Contract

End substantive outputs with:

```text
自检: {N}个数值已核 | {N}个产品已核 | {N}个来源已标注 | 置信度:{高/中/低}
```

Use `置信度:低` when the answer depends on missing, stale, or externally unverified information.
