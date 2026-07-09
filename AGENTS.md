# AGENTS.md

Guidance for agents working in this repository.

## Scope

This repo packages the Fable Soul skill. The canonical rule source is `references/soul.md`; generated or mirrored copies must not be edited directly.

## Verification

Run `npm run check` or `make check` before committing changes. The gate validates the skill package and runs the sync script unit tests through the standard `tests/` wrapper.

## Boundaries

- Do not install hooks, scheduled tasks, or global instruction syncs unless explicitly requested.
- Do not edit generated mirror blocks by hand.
- Keep changes limited to the skill source, tests, docs, and packaging metadata.
