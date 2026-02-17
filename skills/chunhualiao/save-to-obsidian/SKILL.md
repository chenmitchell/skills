---
name: save-to-obsidian
description: Saves markdown content to remote Obsidian vault via SSH
version: 1.0.0
---

# Save to Obsidian

Saves markdown content to remote Obsidian vault via SSH.

## Prerequisite

**This skill is for machines WITHOUT iCloud sync** (e.g., Linux/Ubuntu servers). If your machine already has iCloud Desktop sync enabled and direct access to the Obsidian vault, you don't need this skill — just copy files directly to the vault path.

## When to Use

User says: "save to obsidian", "send to obsidian", "copy to obsidian"

## Process

1. Write content to a temp .md file (enforce formatting rules below)
2. Copy to remote vault: `scp <filepath> user@remote-host:/path/to/obsidian/vault/`
3. Confirm success to user

**Example:**
```bash
# Write content to temp file
cat > /tmp/my-note.md << 'EOF'
# My Note
Content here
EOF

# Copy to remote Obsidian vault
scp /tmp/my-note.md myuser@vault.example.com:~/Obsidian/MyVault/

# Clean up
rm /tmp/my-note.md
```

**Configuration:** The agent should use the SSH host and vault path configured in workspace TOOLS.md

## Formatting Rules

All content saved to Obsidian MUST follow these rules:

### Diagrams: Use Mermaid (mandatory)
- **Never** use ASCII box diagrams, ASCII art, or plaintext diagrams
- **Always** use Mermaid fenced code blocks (` ```mermaid `)
- Obsidian renders Mermaid natively — ASCII diagrams look broken
- Supported types: flowchart, sequence, state, class, ER, gantt, pie, mindmap, timeline, quadrant, graph

### Tables: Use Markdown tables
- Obsidian renders markdown tables natively
- For complex data, prefer tables over bullet lists

### Links: Use wiki-links or relative links
- Link between Obsidian notes: `[[note-name]]`
- External links: standard markdown `[text](url)`

### General
- Use headers (##) for structure — Obsidian outline panel relies on them
- Use YAML frontmatter if metadata is needed
- Keep filenames kebab-case (no spaces) for cross-platform compatibility

## Notes

- Uses existing SSH key auth (no password)
- Target: remote-host → Obsidian vault location
- Files sync via iCloud automatically (if vault is in iCloud folder)
