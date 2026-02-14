#!/usr/bin/env python3
"""
Link Brain - Your personal knowledge base for saved links.

Save any URL with a summary and tags. Search by topic, keyword, or date.
Uses SQLite with FTS5 for fast full-text search.

Commands:
  save      Save a URL with title, summary, and tags
  search    Search saved links by keyword/topic
  recent    Show recently saved links
  tags      List all tags or filter by tag
  get       Get full details for a saved link
  delete    Delete a saved link by ID
  stats     Show collection stats
  export    Export all links as JSON
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DB_DIR = Path(os.environ.get("LINK_BRAIN_DIR", Path.home() / ".link-brain"))
DB_PATH = DB_DIR / "brain.db"


def get_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '',
            source_type TEXT NOT NULL DEFAULT 'article',
            saved_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS link_tags (
            link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (link_id, tag_id)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS links_fts USING fts5(
            title, summary, tags, url,
            content='links',
            content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS links_ai AFTER INSERT ON links BEGIN
            INSERT INTO links_fts(rowid, title, summary, tags, url)
            VALUES (new.id, new.title, new.summary, new.tags, new.url);
        END;

        CREATE TRIGGER IF NOT EXISTS links_ad AFTER DELETE ON links BEGIN
            INSERT INTO links_fts(links_fts, rowid, title, summary, tags, url)
            VALUES ('delete', old.id, old.title, old.summary, old.tags, old.url);
        END;

        CREATE TRIGGER IF NOT EXISTS links_au AFTER UPDATE ON links BEGIN
            INSERT INTO links_fts(links_fts, rowid, title, summary, tags, url)
            VALUES ('delete', old.id, old.title, old.summary, old.tags, old.url);
            INSERT INTO links_fts(rowid, title, summary, tags, url)
            VALUES (new.id, new.title, new.summary, new.tags, new.url);
        END;
    """)
    return db


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def ensure_tags(db, tag_names):
    tag_ids = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        db.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        row = db.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
        if row:
            tag_ids.append(row["id"])
    return tag_ids


def link_to_dict(row):
    d = dict(row)
    if d.get("tags"):
        d["tags"] = [t.strip() for t in d["tags"].split(",") if t.strip()]
    else:
        d["tags"] = []
    return d


# -- Commands --

def cmd_save(args):
    db = get_db()
    now = now_iso()

    tag_list = []
    if args.tags:
        tag_list = [t.strip().lower() for t in args.tags.split(",") if t.strip()]
    tags_str = ", ".join(tag_list)

    # Detect source type from URL
    source_type = "article"
    url_lower = args.url.lower()
    if any(x in url_lower for x in ["youtube.com", "youtu.be", "vimeo.com"]):
        source_type = "video"
    elif any(x in url_lower for x in ["podcasts.apple", "spotify.com/episode", "overcast.fm"]):
        source_type = "podcast"
    elif url_lower.endswith(".pdf"):
        source_type = "pdf"
    elif any(x in url_lower for x in ["twitter.com", "x.com", "threads.net", "mastodon"]):
        source_type = "social"
    elif any(x in url_lower for x in ["github.com", "gitlab.com"]):
        source_type = "repo"

    cursor = db.execute(
        """INSERT INTO links (url, title, summary, tags, source_type, saved_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (args.url, args.title or "", args.summary or "", tags_str, source_type, now, now)
    )
    link_id = cursor.lastrowid

    # Link tags
    tag_ids = ensure_tags(db, tag_list)
    for tid in tag_ids:
        db.execute("INSERT OR IGNORE INTO link_tags (link_id, tag_id) VALUES (?, ?)",
                   (link_id, tid))

    db.commit()

    link = db.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    print(json.dumps({"status": "saved", "link": link_to_dict(link)}))


def cmd_search(args):
    db = get_db()
    query = args.query
    limit = args.limit or 20

    # FTS5 search with ranking
    # Escape special FTS chars
    fts_query = re.sub(r'[^\w\s]', ' ', query)
    terms = fts_query.split()
    if not terms:
        print(json.dumps([]))
        return

    # Use prefix matching for better recall
    fts_expr = " OR ".join(f'"{t}"*' for t in terms if t)

    rows = db.execute(
        """SELECT links.*, rank
           FROM links_fts
           JOIN links ON links.id = links_fts.rowid
           WHERE links_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (fts_expr, limit)
    ).fetchall()

    results = [link_to_dict(r) for r in rows]

    # If FTS returns nothing, fall back to LIKE search
    if not results:
        like_pattern = f"%{query}%"
        rows = db.execute(
            """SELECT * FROM links
               WHERE title LIKE ? OR summary LIKE ? OR tags LIKE ? OR url LIKE ?
               ORDER BY saved_at DESC
               LIMIT ?""",
            (like_pattern, like_pattern, like_pattern, like_pattern, limit)
        ).fetchall()
        results = [link_to_dict(r) for r in rows]

    print(json.dumps(results, indent=2))


def cmd_recent(args):
    db = get_db()
    limit = args.limit or 20

    rows = db.execute(
        "SELECT * FROM links ORDER BY saved_at DESC LIMIT ?",
        (limit,)
    ).fetchall()

    results = [link_to_dict(r) for r in rows]
    print(json.dumps(results, indent=2))


def cmd_tags(args):
    db = get_db()

    if args.name:
        # Show links with this tag
        tag_name = args.name.lower()
        rows = db.execute(
            """SELECT links.* FROM links
               JOIN link_tags ON links.id = link_tags.link_id
               JOIN tags ON tags.id = link_tags.tag_id
               WHERE tags.name = ?
               ORDER BY links.saved_at DESC""",
            (tag_name,)
        ).fetchall()
        results = [link_to_dict(r) for r in rows]
        print(json.dumps(results, indent=2))
    else:
        # List all tags with counts
        rows = db.execute(
            """SELECT tags.name, COUNT(link_tags.link_id) as count
               FROM tags
               JOIN link_tags ON tags.id = link_tags.tag_id
               GROUP BY tags.name
               ORDER BY count DESC"""
        ).fetchall()
        print(json.dumps([dict(r) for r in rows], indent=2))


def cmd_get(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if row:
        print(json.dumps(link_to_dict(row), indent=2))
    else:
        print(json.dumps({"error": f"Link #{args.id} not found"}))


def cmd_delete(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if row:
        db.execute("DELETE FROM links WHERE id = ?", (args.id,))
        db.commit()
        print(json.dumps({"status": "deleted", "link": link_to_dict(row)}))
    else:
        print(json.dumps({"error": f"Link #{args.id} not found"}))


def cmd_stats(args):
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    by_type = db.execute(
        "SELECT source_type, COUNT(*) as n FROM links GROUP BY source_type ORDER BY n DESC"
    ).fetchall()
    tag_count = db.execute("SELECT COUNT(*) as n FROM tags").fetchone()["n"]
    recent = db.execute(
        "SELECT saved_at FROM links ORDER BY saved_at DESC LIMIT 1"
    ).fetchone()
    oldest = db.execute(
        "SELECT saved_at FROM links ORDER BY saved_at ASC LIMIT 1"
    ).fetchone()

    stats = {
        "total_links": total,
        "total_tags": tag_count,
        "by_type": {r["source_type"]: r["n"] for r in by_type},
        "newest": recent["saved_at"] if recent else None,
        "oldest": oldest["saved_at"] if oldest else None,
    }
    print(json.dumps(stats, indent=2))


def cmd_export(args):
    db = get_db()
    rows = db.execute("SELECT * FROM links ORDER BY saved_at DESC").fetchall()
    results = [link_to_dict(r) for r in rows]
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Link Brain - personal knowledge base for saved links")
    sub = parser.add_subparsers(dest="command", required=True)

    # save
    p_save = sub.add_parser("save", help="Save a URL")
    p_save.add_argument("url", help="URL to save")
    p_save.add_argument("--title", "-t", help="Title")
    p_save.add_argument("--summary", "-s", help="Summary text")
    p_save.add_argument("--tags", "-g", help="Comma-separated tags")

    # search
    p_search = sub.add_parser("search", help="Search saved links")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-n", type=int, default=20)

    # recent
    p_recent = sub.add_parser("recent", help="Show recent links")
    p_recent.add_argument("--limit", "-n", type=int, default=20)

    # tags
    p_tags = sub.add_parser("tags", help="List tags or show links for a tag")
    p_tags.add_argument("name", nargs="?", help="Tag name (optional)")

    # get
    p_get = sub.add_parser("get", help="Get full link details")
    p_get.add_argument("id", type=int, help="Link ID")

    # delete
    p_del = sub.add_parser("delete", help="Delete a link")
    p_del.add_argument("id", type=int, help="Link ID")

    # stats
    sub.add_parser("stats", help="Show collection stats")

    # export
    sub.add_parser("export", help="Export all links as JSON")

    args = parser.parse_args()

    if args.command == "save":
        cmd_save(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "recent":
        cmd_recent(args)
    elif args.command == "tags":
        cmd_tags(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "export":
        cmd_export(args)


if __name__ == "__main__":
    main()
