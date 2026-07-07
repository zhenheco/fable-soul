# Soul Maintenance（zhenheco fork）

## Mirror Map

Canonical: `references/soul.md` in the dev repo (`zhenheco/fable-soul`, local clone under Claude Code Projects). Content files (`references/*.md`) stay byte-identical to upstream so `git fetch upstream` diffs cleanly; only `scripts/` and this file diverge.

| Mirror | Runner that reads it | Content | Mechanism |
|--------|---------------------|---------|-----------|
| `$HOME/Documents/CC Cli/skills/fable-soul/` | Claude Code Skill tool（`~/.claude/skills` 是 vault symlink）+ git 跨機同步 | full skill copy | `sync_soul.py` rsync-style copy |
| `~/.codex/skills/fable-soul` | Codex skill loader | symlink → vault skill | ensured by `sync_soul.py` |
| `$HOME/Documents/CC Cli/CLAUDE-global.md` | Claude Code every session（via `~/.claude/CLAUDE.md` symlink）；Codex 亦繼承（見下行） | `<!-- fable-soul:begin/end -->` marker block，compact soul body | `sync_soul.py` block injection |
| `$HOME/Documents/CC Cli/codex-tail.md` | Codex（經 sync-codex.sh） | marker block，Codex-only Reasoning Directives | `sync_soul.py` block injection |
| `~/.codex/AGENTS.md` | Codex, every session | GENERATED = CLAUDE-global.md + codex-tail.md | `scripts/sync-codex.sh`（sync_soul.py 注入後自動呼叫）— **never edit directly** |

The block carries the **compact rendering** (`references/soul-compact.md`) from the line `**Violating the letter...**` onward. The compact version keeps every rule, the full rationalization table, and all red flags, but compresses rule prose to its core imperative — roughly 40% fewer tokens per session, equivalence verified against the eval scenarios. Skill mirrors carry the full `soul.md`. The sync script enforces structural parity (rule count, table rows, red-flag count) between canonical and compact and refuses to sync on mismatch. Edit canonical first, mirror the change into soul-compact.md, then sync — never hand-edit a mirror or a marker block.

**Codex-only Reasoning Directives block**（injected into `codex-tail.md`）is NOT part of the soul — it is a set of runtime workarounds for GPT-5.5 on Codex: an anti-truncation directive (failure mode: reasoning cut at ~516 tokens, long-reasoning tasks fail; proof surface: reasoning-token counts and task accuracy in Codex), an agentic-persistence directive (failure mode: Codex ends its turn or hands back mid-task during long autonomous runs; proof surface: turns ending with unresolved in-scope steps), and a subagent-delegation directive distilled from lazycodex/Hephaestus (failure mode: Codex works serially and never spawns subagents despite `multi_agent = true`; proof surface: parallel explore/implement subagent calls appearing in long Codex runs). Strip condition: remove a directive when OpenAI fixes the underlying behavior, the Codex default model moves off gpt-5.5, or (for delegation) `multi_agent` is disabled.

## Sync Procedure

1. Edit canonical `references/soul.md`（+ mirror the change into `soul-compact.md`）in the dev repo only.
2. Run `python scripts/sync_soul.py` from the dev-repo skill root. It copies the skill to the vault, injects/refreshes both marker blocks, and runs `sync-codex.sh` to regenerate `~/.codex/AGENTS.md`.
3. Run `python scripts/sync_soul.py --check` to confirm zero drift.
4. Read back at least one target where a runner loads it（`~/.claude/CLAUDE.md` 尾端 block、`~/.codex/AGENTS.md`）.
5. Commit + push **both repos**: the dev repo, and the vault repo（`skills/fable-soul/` + `CLAUDE-global.md` + `codex-tail.md`）— vault push is what syncs other machines.

If `--check` reports drift you did not cause, a mirror or block was edited directly. Diff against canonical, review mirror-side additions on merit — advice is not infrastructure — adopt what survives into canonical, then re-sync.

**Upstream updates**: `git fetch upstream && git diff upstream/main -- references/ ':!references/maintenance.md'` in the dev repo（remote `upstream` = akseolabs-seo/fable-soul）. Because those files stay upstream-identical, any diff is a real upstream change — review, merge, re-sync. `scripts/check_update.py` will always report `scripts/` + this file as differing（by design, forked integration layer）; trust the git diff scoped to `references/` instead.

## 與 zhenheco 既有紀律的分工

- **Soul = 判斷層（HOW to think）**；`rules/*.md`（hard-rules、engineering-discipline、debugging、orchestration）= 工作流層（WHAT to do、誰做）。重疊處（root cause、evidence、surgical changes、fail loud）是互相強化，非衝突；若日後要瘦身，跑 transfer-prompts.md 的 Instruction Audit，從 rules 端刪重複、soul 端保持 upstream-identical。
- **失誤記錄路由**：模型「判斷失誤」（false done、hedged claim、symptom patch、選項菜單不推薦）→ 本檔 Capture Loop；專案/領域錯誤（Hard Rule 6）→ `auto-skill`。同一事件兩者都命中時，先 capture 進 soul（可測、可同步），auto-skill 留 pointer。

## Capture Loop (adding a failure to the soul)

Trigger: a model produced a failure worth preventing — false "done", hedged checkable claim, symptom patch, ineffective requested fix shipped, options menu instead of a recommendation, ceremony on a simple question.

1. **Record the rationalization verbatim.** The exact excuse the model gave is the table row; paraphrases lose the trigger.
2. **Check for existing coverage.** Search soul.md's rules, table, and red flags. If a rule already covers it, the failure means the rule was ignored, not missing — strengthen the wording, add the verbatim excuse to the existing row, or add a red flag; do not add a duplicate rule.
3. **RED**: reproduce the failure with a subagent pressure scenario WITHOUT the new wording. If you cannot reproduce it, you do not know what you are fixing.
4. **GREEN**: apply the minimal edit to canonical, re-run the same scenario, confirm the behavior flips.
5. **Sync** per the procedure above.

No rule edit ships untested. "The wording is obviously clear" is itself a rationalization.

## Growth Budget

soul.md must stay loadable in every session. Before adding, ask what to remove or compress. If the file exceeds roughly 250 lines, run the Instruction Audit prompt (transfer-prompts.md) and slim it before adding more. A judgment layer that models skim is worse than a shorter one they read.
