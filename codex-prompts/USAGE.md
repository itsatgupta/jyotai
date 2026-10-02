# How to use the Codex prompts

## Rule

Run one prompt at a time.

After each prompt:

1. Let Codex implement it.
2. Ask it to run tests.
3. Review the changed files.
4. If tests pass, commit.
5. Move to the next prompt.

## Suggested command

From the repository root:

```bash
codex
```

Then paste the contents of:

```text
codex-prompts/00_START_HERE.md
```

For the next task, paste:

```text
codex-prompts/01_FOUNDATION.md
```

and continue sequentially.

## If Codex tries to do too much

Tell it:

> Stop. Implement only the current task. Do not implement later roadmap items.

## If you do not understand the code

Ask Codex:

> Explain the changes in plain English. Do not modify code.

You can also bring the error/output back to ChatGPT and ask for help.
