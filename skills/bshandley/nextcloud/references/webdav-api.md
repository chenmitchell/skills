# Nextcloud WebDAV API Reference

Generic WebDAV API documentation for any Nextcloud instance.

## Configuration

Set credentials via environment variables or config file:

```bash
# Environment variables
export NEXTCLOUD_URL="https://cloud.example.com"
export NEXTCLOUD_USER="admin"  
export NEXTCLOUD_PASS="app-password-from-nextcloud"

# Or use config file at ~/.config/nextcloud/config.json
python3 nextcloud_helper.py setup --url URL --user USER --pass PASS
```

## Base URL Format

```
{NEXTCLOUD_URL}/remote.php/dav/files/{USER}/{path}
```

Example:
```
https://cloud.example.com/remote.php/dav/files/admin/Documents/file.txt
```

## Operations

### PROPFIND - List Files

List files in a directory:

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X PROPFIND \
  -H "Depth: 1" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Documents/"
```

Depth levels:
- `0` - Properties of the resource only
- `1` - Resource and immediate children (recommended)
- `2` - Resource and all descendants

### PUT - Upload File

Standard upload:
```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -T local_file.txt \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Documents/file.txt"
```

**For large files** (>50MB), force HTTP/1.1:
```bash
curl --http1.1 -H "Expect:" \
  -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -T large_video.mp4 \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Videos/video.mp4"
```

The `--http1.1 -H "Expect:"` flags avoid HTTP/2 protocol errors with large uploads.

### GET - Download File

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -o local_file.txt \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Documents/file.txt"
```

### MKCOL - Create Folder

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X MKCOL \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/NewFolder/"
```

### DELETE - Delete File/Folder

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X DELETE \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/OldFolder/"
```

### MOVE - Rename/Move

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_PASS" \
  -X MOVE \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Documents/newname.txt" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Documents/oldname.txt"
```

## Response Format

PROPFIND returns XML with these properties:

| Property | Description |
|----------|-------------|
| `d:href` | Full path URL |
| `d:displayname` | Filename |
| `d:getcontentlength` | Size in bytes (files only) |
| `d:getlastmodified` | Last modified date |
| `d:getetag` | ETag for change detection |
| `d:resourcetype/d:collection` | Present if directory |

## Error Handling

| Status | Meaning | Fix |
|--------|---------|-----|
| 200, 201, 204 | Success | - |
| 401 | Authentication failed | Check credentials |
| 404 | Not found | Path doesn't exist |
| 409 | Conflict | Folder already exists or parent missing |
| 412 | Precondition failed | ETag mismatch (use If-Match) |
| 500, 502, 503 | Server error | Retry or check Nextcloud |
| 000 | Connection dropped | Use `--http1.1` for large files |

## Python Examples

### Browse files
```python
from nextcloud_helper import list_files
files = list_files("Documents", depth=1)
for f in files:
    print(f"{f['name']}: {'[dir]' if f['is_dir'] else f['size']}")
```

### Upload with retry
```python
from nextcloud_helper import upload_file

try:
    # Try standard upload first
    upload_file("file.txt", "Documents/file.txt")
except Exception:
    # Fall back to HTTP/1.1
    upload_file("file.txt", "Documents/file.txt", use_http11=True)
```

### Sync workflow
```python
from nextcloud_helper import sync_down, list_files

# Sync multiple folders
result = sync_down(["Documents/Notes", "Documents/Projects"], 
                   "~/sync/")
print(f"Synced {result['synced']}, errors: {len(result['errors'])}")

# Check for new files
new = list_files("Uploads", depth=1)
for f in new:
    if not f['is_dir']:
        print(f"New file: {f['name']} ({f['size']} bytes)")
```

## Authentication

Nextcloud supports two auth methods:

1. **Basic auth** with username + password/app password (used here)
2. **OAuth2** (not covered, requires token exchange)

**App passwords** (preferred): Generate in Nextcloud Settings → Security → Devices & sessions.

## Rate Limiting

Default Nextcloud limits: ~120 req/min per user. The helper includes automatic retry with exponential backoff for 429s.
