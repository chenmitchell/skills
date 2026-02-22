#!/usr/bin/env python3
"""Nextcloud WebDAV client with RAG sync integration.

Environment variables:
  NEXTCLOUD_URL       - Nextcloud base URL (default: https://nextcloud.example.com)
  NEXTCLOUD_USER      - Username (default: admin)
  NEXTCLOUD_PASS      - App password or user password
  NEXTCLOUD_RAG_PATH  - Local path for RAG sync (optional)

Config file: ~/.config/nextcloud/config.json
"""

import os
import sys
import json
import requests
from pathlib import Path
from urllib.parse import quote
from typing import List, Optional

CONFIG_PATH = Path.home() / ".config" / "nextcloud" / "config.json"

def load_config():
    """Load config from env vars or config file."""
    config = {
        "url": os.getenv("NEXTCLOUD_URL", "https://nextcloud.example.com"),
        "user": os.getenv("NEXTCLOUD_USER", "admin"),
        "pass": os.getenv("NEXTCLOUD_PASS", ""),
        "rag_path": os.getenv("NEXTCLOUD_RAG_PATH", ""),
    }
    
    # Override with config file if exists
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            file_config = json.load(f)
            config.update({k: v for k, v in file_config.items() if v})
    
    return config

def get_auth():
    """Get authentication tuple."""
    config = load_config()
    if not config["pass"]:
        raise ValueError("NEXTCLOUD_PASS not set and no config file found")
    return (config["user"], config["pass"])

def get_base_url():
    """Get Nextcloud base URL."""
    return load_config()["url"].rstrip("/")

def webdav_url(path: str) -> str:
    """Build WebDAV URL from relative path."""
    config = load_config()
    if not path.startswith("/"):
        path = "/" + path
    encoded = quote(path, safe="/")
    return f"{config['url']}/remote.php/dav/files/{config['user']}{encoded}"

def list_files(remote_path: str = "", depth: int = 1) -> List[dict]:
    """List files in a Nextcloud directory via WebDAV PROPFIND."""
    url = webdav_url(remote_path)
    headers = {"Depth": str(depth)}
    
    resp = requests.request(
        "PROPFIND", url, auth=get_auth(), headers=headers, timeout=30
    )
    resp.raise_for_status()
    
    from xml.etree import ElementTree as ET
    root = ET.fromstring(resp.content)
    
    ns = {"d": "DAV:"}
    files = []
    
    for response in root.findall("d:response", ns):
        href = response.find("d:href", ns).text if response.find("d:href", ns) is not None else ""
        prop = response.find("d:propstat/d:prop", ns)
        if prop is None:
            continue
        
        name = href.split("/")[-1] if href else ""
        is_dir = prop.find("d:resourcetype/d:collection", ns) is not None
        size_elem = prop.find("d:getcontentlength", ns)
        size = int(size_elem.text) if size_elem is not None and size_elem.text else 0
        modified_elem = prop.find("d:getlastmodified", ns)
        modified = modified_elem.text if modified_elem is not None else ""
        etag_elem = prop.find("d:getetag", ns)
        etag = etag_elem.text if etag_elem is not None else ""
        
        if depth == 1 and name == remote_path.split("/")[-1]:
            continue
        
        files.append({
            "name": name,
            "path": href.split(f"/remote.php/dav/files/{load_config()['user']}/")[-1],
            "is_dir": is_dir,
            "size": size,
            "modified": modified,
            "etag": etag,
        })
    
    return files

def upload_file(local_path: str, remote_path: str, use_http11: bool = True) -> bool:
    """Upload a file to Nextcloud via WebDAV PUT.
    
    Args:
        local_path: Path to local file
        remote_path: Destination path on Nextcloud
        use_http11: Force HTTP/1.1 for large files (avoids HTTP/2 errors)
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    
    url = webdav_url(remote_path)
    headers = {}
    if use_http11:
        headers["Expect"] = ""
    
    with open(local_path, "rb") as f:
        resp = requests.put(
            url, data=f, auth=get_auth(), headers=headers, timeout=600
        )
    
    resp.raise_for_status()
    return resp.status_code in [200, 201, 204]

def download_file(remote_path: str, local_path: str) -> bool:
    """Download a file from Nextcloud."""
    url = webdav_url(remote_path)
    resp = requests.get(url, auth=get_auth(), timeout=120)
    resp.raise_for_status()
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(resp.content)
    
    return True

def delete_file(remote_path: str) -> bool:
    """Delete a file from Nextcloud."""
    url = webdav_url(remote_path)
    resp = requests.delete(url, auth=get_auth(), timeout=30)
    return resp.status_code in [200, 204]

def create_folder(remote_path: str) -> bool:
    """Create a folder in Nextcloud via WebDAV MKCOL."""
    url = webdav_url(remote_path)
    resp = requests.request("MKCOL", url, auth=get_auth(), timeout=30)
    return resp.status_code in [200, 201, 409]  # 409 = already exists

def sync_down(remote_paths: List[str], local_base: str) -> dict:
    """Sync files from Nextcloud to local path.
    
    Args:
        remote_paths: List of remote paths to sync
        local_base: Local base path for downloads
    
    Returns:
        Dict with synced files count and any errors
    """
    synced = 0
    errors = []
    
    for remote_path in remote_paths:
        try:
            files = list_files(remote_path, depth=2)
            for file in files:
                if file["is_dir"]:
                    continue
                
                remote_file = file["path"]
                local_file = os.path.join(local_base, file["path"])
                
                # Check if needs update
                needs_update = True
                if os.path.exists(local_file):
                    local_stat = os.stat(local_file)
                    if local_stat.st_size == file["size"]:
                        needs_update = False
                
                if needs_update:
                    os.makedirs(os.path.dirname(local_file), exist_ok=True)
                    download_file(remote_file, local_file)
                    synced += 1
                
        except Exception as e:
            errors.append(f"{remote_path}: {str(e)}")
    
    return {"synced": synced, "errors": errors}

def find_files_by_ext(path: str, extensions: tuple, max_age_hours: int = 24) -> List[dict]:
    """Find files by extension, optionally filtered by recency.
    
    Args:
        path: Remote path to search
        extensions: Tuple of file extensions (e.g., ('.mp3', '.m4a'))
        max_age_hours: Only return files newer than this (0 = all)
    """
    from datetime import datetime, timedelta
    
    files = list_files(path, depth=1)
    
    result = []
    for f in files:
        if f["is_dir"]:
            continue
        if f["name"].lower().endswith(extensions):
            if max_age_hours > 0 and f["modified"]:
                # Simple recency check (parsing HTTP date)
                try:
                    mtime = datetime.strptime(f["modified"][:26], "%a, %d %b %Y %H:%M:%S")
                    if datetime.utcnow() - mtime < timedelta(hours=max_age_hours):
                        result.append(f)
                except:
                    result.append(f)
            else:
                result.append(f)
    
    return result

def setup_config(url: str, user: str, password: str, rag_path: str = ""):
    """Create config file at ~/.config/nextcloud/config.json"""
    config_dir = Path.home() / ".config" / "nextcloud"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "url": url,
        "user": user,
        "pass": password,
        "rag_path": rag_path,
    }
    
    config_path = config_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Set restrictive permissions
    os.chmod(config_path, 0o600)
    print(f"Config saved to {config_path}")
    return config_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nextcloud WebDAV client")
    sub = parser.add_subparsers(dest="command")
    
    # setup
    setup_p = sub.add_parser("setup", help="Configure credentials")
    setup_p.add_argument("--url", required=True, help="Nextcloud URL (e.g., https://cloud.example.com)")
    setup_p.add_argument("--user", required=True, help="Username")
    setup_p.add_argument("--pass", required=True, help="App password")
    setup_p.add_argument("--rag-path", default="", help="Local RAG sync path")
    
    # list
    list_p = sub.add_parser("list", help="List files")
    list_p.add_argument("path", nargs="?", default="", help="Remote path")
    list_p.add_argument("--depth", type=int, default=1, help="Recursion depth")
    
    # upload
    upload_p = sub.add_parser("upload", help="Upload file")
    upload_p.add_argument("local", help="Local file path")
    upload_p.add_argument("remote", help="Remote path")
    upload_p.add_argument("--http11", action="store_true", help="Force HTTP/1.1 for large files")
    
    # download
    dl_p = sub.add_parser("download", help="Download file")
    dl_p.add_argument("remote", help="Remote path")
    dl_p.add_argument("local", help="Local file path")
    
    # sync
    sync_p = sub.add_parser("sync", help="Sync remote to local")
    sync_p.add_argument("paths", nargs="+", help="Remote paths to sync")
    sync_p.add_argument("--local", required=True, help="Local base path")
    
    # find
    find_p = sub.add_parser("find", help="Find files by extension")
    find_p.add_argument("path", default="", help="Remote path to search")
    find_p.add_argument("--ext", default=".mp3,.m4a,.wav", help="File extensions (comma-separated)")
    find_p.add_argument("--recent", type=int, default=0, help="Only files newer than N hours")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_config(args.url, args.user, args.pass, args.rag_path)
    
    elif args.command == "list":
        files = list_files(args.path, args.depth)
        for f in files:
            print(f"{f['name']:<40} {f['size']:>10} {'[dir]' if f['is_dir'] else ''}")
    
    elif args.command == "upload":
        success = upload_file(args.local, args.remote, use_http11=args.http11)
        print("OK" if success else "FAILED")
    
    elif args.command == "download":
        success = download_file(args.remote, args.local)
        print("OK" if success else "FAILED")
    
    elif args.command == "sync":
        result = sync_down(args.paths, args.local)
        print(f"Synced: {result['synced']}")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
    
    elif args.command == "find":
        exts = tuple(args.ext.split(","))
        files = find_files_by_ext(args.path, exts, args.recent)
        for f in files:
            print(f"{f['modified'][:20]} {f['name']}")
    
    else:
        parser.print_help()
