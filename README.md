# AI builds: resources

This is the permanent home for everything the "AI builds" videos by Masoud Masoori point to: guides, small tools, source links and Claude skills. A video can be removed or replaced, but the page it sent you to stays here.

## Resources

| id | Video | What you get | Page |
|---|---|---|---|
| docling | "This free GitHub repo turns an invoice PDF into a clean table" | Install steps, the one command, how to check the output, when not to use it, and a block to paste into Claude | [resources/docling](resources/docling/README.md) |
| invoice-rule-check | "Use a rule, not AI" | A short Python script (standard library only) that adds up invoice lines and compares them to the order total, with tests and a fictional sample | [resources/invoice-rule-check](resources/invoice-rule-check/README.md) |
| weekly-ai-2026-10-30 | "This week in AI", episode 1 | The three stories with their primary sources, and the one thing to try this week | [resources/weekly-ai-2026-10-30](resources/weekly-ai-2026-10-30/README.md) |

How this repository is organized, and why nothing here is ever deleted: [STRUCTURE.md](STRUCTURE.md).

## Get a skill into Claude

This repository ships one Claude plugin, `ai-builds`, with two skills: `docling-convert` and `invoice-rule-check`. There are three routes. Retrieved 2026-10-28; docs change, so check the linked pages if a step differs.

### Route 1: Claude Code plugin marketplace

From the shell:

```
claude plugin marketplace add Masoud-Masoori/ai-builds
claude plugin install ai-builds@ai-builds
```

Inside a Claude Code session the same two steps are `/plugin marketplace add Masoud-Masoori/ai-builds` and `/plugin install ai-builds@ai-builds`. In a session, the install command opens the plugin panel so you can review the plugin and choose a scope first. In the shell, the scope is user by default; add `--scope project` or `--scope local` to change it.

One step instead of two (shell form needs Claude Code v2.1.292 or later): `claude plugin install ai-builds --marketplace Masoud-Masoori/ai-builds`.

Plugin skills are namespaced, so you call them as `/ai-builds:docling-convert` and `/ai-builds:invoice-rule-check`.

Good to know:

- A plugin can run hooks and MCP servers, so read the plugin before you install it. This one contains skills only, which you can check in `plugins/ai-builds`.
- Marketplaces from third parties do not auto-update by default. To get new versions, update it yourself or turn auto-update on.
- Plugins you install in Claude Code stay on your machine and are not added to your claude.ai account.
- Claude Desktop: the Code tab has a plugin browser (the + button, then Add plugins, or Plugins then Browse plugins). Whether Desktop can upload a standalone custom skill is UNKNOWN; no documented path was found.

Sources: https://code.claude.com/docs/en/discover-plugins and https://code.claude.com/docs/en/plugin-marketplaces (retrieved 2026-10-28).

### Route 2: copy the skill folder yourself

Copy a skill folder from `plugins/ai-builds/skills/` into one of these places:

- Personal, all your projects on that machine: `~/.claude/skills/<skill-name>/SKILL.md`
- One project, shared by committing it: `.claude/skills/<skill-name>/SKILL.md`

For example, the folder `docling-convert` becomes `~/.claude/skills/docling-convert/SKILL.md`. Personal skills are not available in Cowork or cloud sessions.

Source: https://code.claude.com/docs/en/skills (retrieved 2026-10-28).

### Route 3: upload to claude.ai

1. Download or zip the skill folder (for example `docling-convert`). The folder must be the root of the ZIP, not a subfolder, and its name must match the skill name.
2. In claude.ai go to Customize, then Skills.
3. Click the + button, then + Create skill, then Upload a skill.
4. Upload the ZIP.

Custom skills are available on Free, Pro, Max, Team and Enterprise plans, and need code execution to be enabled. On Team and Enterprise an owner can turn skill creation off. Whether claude.ai needs the file named `SKILL.md` (as in Claude Code) or `skill.md` (as the support article writes it) is UNKNOWN; if the upload says the file is missing, try the other spelling. Whether claude.ai accepts a GitHub repo directly as a skill source is also UNKNOWN; only ZIP upload is documented.

Sources: https://support.claude.com/en/articles/12512180-using-skills-in-claude and https://support.claude.com/en/articles/12512198-how-to-create-custom-skills (retrieved 2026-10-28).

## Disclosure

The videos these pages belong to use an AI representation of Masoud with a synthetic voice. Sample data in the videos and in these pages is fictional unless a page says otherwise. Nothing here is affiliated with or endorsed by the projects it mentions.

## License

MIT, see [LICENSE](LICENSE). Copyright 2026 Masoud Masoori.
