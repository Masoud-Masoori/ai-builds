# Structure and durability rules

## The rule behind everything

Resources never live inside render or video folders. A video can be deleted, re-cut or taken down without touching what a commenter was sent. A link in a DM or a caption must still work years later, so entries here are never deleted, only marked archived.

## Layout

```
README.md                      what this is, table of resources, how to get a skill into Claude
STRUCTURE.md                   this file
DM-REPLIES.md                  draft DM texts, one per resource
LICENSE                        MIT
resources/<id>/README.md       one page per resource (sections: What it is, How to use it, Sources)
resources/<id>/...             any files that page needs (scripts, samples, tests)
.claude-plugin/marketplace.json  makes this repository a Claude plugin marketplace
plugins/ai-builds/             the plugin: .claude-plugin/plugin.json and skills/<name>/SKILL.md
scripts/check_resources.py     the checker
tests/test_check_resources.py  tests for the checker
.github/workflows/check.yml    runs the checker and the tests on push and weekly
```

## Stable id rule

- A resource lives at `resources/<id>/`. The id is lowercase letters, digits and hyphens.
- The id is permanent. It is never renamed and never reused for a different resource, even after archiving, because links already sent point at it.
- If something must be replaced, add a new id and mark the old one archived with a pointer to the new one.
- A dated edition (for example a weekly episode) carries the date in the id.

## Archive rule

- Nothing is deleted. To retire a resource, add a line `Status: archived (reason, date)` directly under the title of its README, and change its row in the README table to say Archived. Keep the folder, the page and every link working.
- An archived page still has to pass the checker, including the three required sections.
- Skills in the plugin follow the same rule: a retired skill stays in `plugins/ai-builds/skills/` with its description starting with "Archived:" and a pointer to the replacement.

## How to add a resource (checklist)

1. Pick the id and check it is not used anywhere in `resources/` or in git history (`git log --all -- resources/<id>`).
2. Create `resources/<id>/README.md` with the sections What it is, How to use it, Sources. Every factual line gets a source URL you read and the date you read it, or the word UNKNOWN.
3. Put any scripts, samples and tests in the same folder. Tests run from the repository root with `python -m pytest -q`.
4. If viewers should get it as a Claude skill, add `plugins/ai-builds/skills/<name>/SKILL.md` with `name` and `description` frontmatter. The skill must ask before installing anything and must never ask for credentials.
5. Add a row to the table in README.md.
6. Add a draft DM to DM-REPLIES.md, with the link `https://github.com/Masoud-Masoori/ai-builds/tree/main/resources/<id>` filled in.
7. Run `python scripts/check_resources.py` (must print HELD) and `python -m pytest -q`.
8. Commit. Never put Windows paths, internal notes, credentials or private business details in this repository: it is public.

## DM texts

DM texts live in DM-REPLIES.md, not in the video folders. They are drafts; every send needs the owner's approval.

## Choices where the docs left a detail UNKNOWN

- The plugin sits in `plugins/ai-builds/` and the marketplace entry uses the source `./plugins/ai-builds`. This follows the documented example layout (`./plugins/my-first-plugin`). Whether a plugin at the repository root with source `./` is accepted was not confirmed in the docs read, so it was not used.
- The skills are in `plugins/ai-builds/skills/<name>/SKILL.md` (documented layout, one folder per skill). The marketplace entry does not list skills separately; the plugin loads them from `skills/`.
- Skill `name` and `description` are both written, and kept short (description under 200 characters) so they also fit the claude.ai help article's stated limits (name 64, description 200), even though the Claude Code docs read did not show those limits for Claude Code.
- The plugin and marketplace carry no version and no author: not required by the docs read. The local validator (`claude plugin validate`) passed with warnings about exactly those fields.
- The GitHub account and repository name used in links (`Masoud-Masoori/ai-builds`) come from the owner's brief. Until a repository exists under that name, `--online` link checks of those links will fail.
