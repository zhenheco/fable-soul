# Fable Soul

English | [繁體中文](README.zh-TW.md)

**A judgment layer for AI coding agents — make your AI think, verify, and communicate like a senior engineer.**

Most AI agent failures aren't knowledge failures. The model knows how to write the code; it just ships a false "done" without running anything, patches a symptom instead of the root cause, hedges a claim it could verify in ten seconds, or asks permission instead of finishing the work. Fable Soul is a battle-tested set of operating rules that fixes those failures at the behavior level — and a toolkit for keeping the rules alive as your agent evolves.

Works with **Claude Code** and **Codex** (or any runner that reads Markdown instructions).

## What's inside

```
fable-soul/
├── SKILL.md                        # Skill entry point (3 modes: Embody / Maintain / Transfer)
├── references/
│   ├── soul.md                     # The judgment rules — the core of this project
│   ├── maintenance.md              # Mirror map, sync procedure, failure-capture loop
│   └── transfer-prompts.md         # 6 prompt templates for turning experience into skills
└── scripts/
    ├── sync_soul.py                # Sync rules to all install locations, detect drift
    └── validate_skill.py           # Structural validation for the skill package
```

## Modules

### 1. The judgment rules (`references/soul.md`)

19 operating rules plus executable gates. Highlights:

- **Operating Gates** — a Task Start Gate (goal / mechanism / proof), a Proof Contract matching verification to task type (code, frontend, SEO/publishing, writing), and Red Flag Recovery actions.
- **Root cause before any fix** — no change ships until the agent can state the bug's mechanism in one sentence.
- **Verify before claiming** — "done" requires observed evidence; a successful file edit only proves the agent typed.
- **Finish the work** — for reversible in-scope work, do it instead of asking "want me to fix it?"
- **Measure instead of hedging** — if a claim is checkable in under a minute, check it; numbers beat adjectives.
- **Rationalization table** — the exact excuses models give ("the edit succeeded, so it's done", "the test will probably pass") mapped to why each one is wrong. Each row was captured verbatim from a real failure.
- **Red Flags checklist** — a pre-reply self-check the agent runs before ending every turn.

### 2. Three operating modes (`SKILL.md`)

- **Embody** — load the rules into the current session and work that way, silently.
- **Maintain** — capture new failures into the rules (with a RED–GREEN test loop: reproduce the failure without the new wording, apply the minimal edit, confirm the behavior flips), keep installs in sync, and audit/slim the rules so the file stays loadable.
- **Transfer** — turn a stronger model's advice, postmortems, or session lessons into durable skills, preserving the mechanism instead of the aura.

### 3. Transfer prompts (`references/transfer-prompts.md`)

Six ready-to-use prompt templates:

| Prompt | What it does |
|--------|--------------|
| Departing Principal | Makes a strong model convert its project judgment into a skill library for weaker/cheaper models |
| Instruction Audit | Finds stale, contradictory, or over-prescriptive rules before you add more |
| Failure Archaeology | Mines git history and postmortems so future agents don't re-fight settled bugs |
| Executable Campaign | Produces a decision-gated plan with exact commands, expected outputs, and branch points |
| Fresh Verifier | An independent pass that flags claims without evidence before "complete" is reported |
| Skill Library Review | Three-pass audit (factual / doctrine / usability) of a generated skill library |

### 4. Sync & drift tooling (`scripts/`)

- `sync_soul.py` — copies the skill to `~/.claude/skills/` and `~/.codex/skills/`, and regenerates global instruction files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) from the single canonical source. `--check` reports drift without changing anything. It will **not** overwrite a global file it didn't generate — you'll get a skip warning instead.
- `validate_skill.py` — checks frontmatter, reference links, and package structure.

## Install

**Option A — skill only (non-invasive).** Copy this folder to your skills directory:

```bash
# Claude Code
cp -r fable-soul ~/.claude/skills/fable-soul

# Codex
cp -r fable-soul ~/.codex/skills/fable-soul
```

The rules load when the skill is invoked.

**Option B — always-on (recommended).** Run the sync script from the repo root:

```bash
python scripts/sync_soul.py          # install everywhere + generate global files
python scripts/sync_soul.py --check  # verify everything is in sync
```

This makes the rules load in **every** session via your global instruction file. If you already have a `CLAUDE.md` / `AGENTS.md`, the script skips it — paste the body of `references/soul.md` into your existing file instead.

## Maintaining your own rules

The rules are designed to grow from **your** agent's failures, not from generic advice:

1. Your agent ships a false "done" or makes an excuse — record the rationalization **verbatim**.
2. Check whether an existing rule already covers it. If yes, strengthen that rule instead of adding a duplicate.
3. **RED**: reproduce the failure in a fresh session without the new wording.
4. **GREEN**: apply the minimal edit, re-run the same scenario, confirm the behavior flips.
5. Sync: `python scripts/sync_soul.py`.

No rule edit ships untested. And there's a growth budget: if `soul.md` exceeds ~250 lines, slim it before adding more — a judgment layer the model skims is worse than a shorter one it reads.

## Design principles

- **Single source of truth.** `references/soul.md` is canonical; every install location is a script-regenerated mirror. Drift is detectable and mechanical to fix.
- **Rules must be executable.** Every rule needs a failure mode it prevents, a trigger, a changed behavior, and a proof surface. "Think harder" prose doesn't qualify.
- **Advice is not infrastructure.** A tip from a blog post or a stronger model gets in only after it survives the capture loop.

## License

MIT

---

*Fable Soul is an independent open-source project. Not affiliated with any AI vendor.*
