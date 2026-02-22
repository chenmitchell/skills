---
name: nextcloud
description: Access Nextcloud files via WebDAV API. Sync documents for RAG indexing, upload files, manage folders, and automate workflows. Use when browsing cloud files, syncing to local RAG, uploading recordings, or any Nextcloud file operations.
---

# Nextcloud Skill

Work with Nextcloud file storage via WebDAV API.

## Setup

Configure credentials (run once):

```bash
python3 nextcloud_helper.py setup \
  --url https://cloud.example.com \
  --user admin \
  --pass "your-app-password" \
  --rag-path /home/user/data/work-sync
```

Or use environment variables:
```bash
export NEXTCLOUD_URL="https://cloud.example.com"
export NEXTCLOUD_USER="admin"
export NEXTCLOUD_PASS="your-app-password"
export NEXTCLOUD_RAG_PATH="/home/user/data/work-sync"
```

## Quick Start

```bash
cd /path/to/skill/scripts

# List files
python3 nextcloud_helper.py list Documents/

# Upload file
python3 nextcloud_helper.py upload local.txt Documents/notes.txt

# Download file  
python3 nextcloud_helper.py download Documents/notes.txt local.txt

# Sync folder to local
python3 nextcloud_helper.py sync Documents/Work/ --local /home/user/data/work
```

## Large File Uploads

For files >50MB, use `--http11` to avoid HTTP/2 protocol errors:

```bash
python3 nextcloud_helper.py upload large_video.mp4 Videos/movie.mp4 --http11
```

## RAG Sync Workflow

1. Sync remote folders:
```python
from nextcloud_helper import sync_down
result = sync_down(["Documents/Notes", "Documents/Transcripts"], 
                  "/home/user/data/work-sync")
print(f"Synced {result['synced']} files")
```

2. Reindex RAG (with your preferred tool):
```bash
# Example with your RAG system
python3 rag_helper.py reindex
```

## Auto-Detection

Find recent recordings:
```python
from nextcloud_helper import find_files_by_ext
recordings = find_files_by_ext("Recordings", 
                               (".mp3", ".mp4", ".m4a"),
                               max_age_hours=24)
```

## Reference Documentation

- [WebDAV API Reference](references/webdav-api.md) - Complete endpoint docs

## Common Issues

| Issue | Solution |
|-------|----------|
| HTTP/2 protocol error | Use `--http11` flag for uploads |
| 000 status on upload | Connection dropped, retry with `--http11` |
| Large upload fails | Increase timeout or use chunked upload |
| Auth failed | Check app password in Nextcloud settings |
