# Criteria for Code Preferences

Reference only — consult when deciding whether to update SKILL.md.

## When to Add

**Immediate (1 occurrence):**
- User explicitly states preference ("always use TypeScript")
- User corrects your approach ("don't split into so many files")
- User praises specific style ("I like how you structured that")

**After pattern (2+ occurrences):**
- User consistently accepts certain patterns
- User consistently rejects or modifies certain approaches

## When NOT to Add
- Project-specific requirement (this project uses X, doesn't mean always)
- One-off request
- Explicit override ("just this once, do it differently")

## How to Write Entries

**Preferences examples:**
- `asks before adding dependencies`
- `prefers single file for small projects`
- `always include tests`
- `verbose error messages`
- `comments for complex logic only`

**Never examples:**
- `no class-based components`
- `skip detailed planning for simple tasks`
- `no emojis in commit messages`

## Detecting Preference
- User modifies generated code the same way repeatedly
- User asks "why did you do X instead of Y?"
- User undoes certain patterns

## Maintenance
- Keep SKILL.md under 30 lines
- Group similar preferences
- Remove outdated entries
