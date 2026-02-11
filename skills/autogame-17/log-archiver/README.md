# Log Archiver Skill

## Description
Automatically manages the `logs/` directory by archiving old task logs and cleaning up debris.

## Usage
```bash
node skills/log-archiver/index.js --days 7 --archive-dir "logs/archive"
```

## Features
- Moves `task_*.txt` files older than N days to an archive folder.
- Compresses archived logs (optional, future).
- Deletes archives older than M days.
- Generates a summary report of archived files.
