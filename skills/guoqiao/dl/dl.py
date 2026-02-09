#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "yt-dlp",
# ]
# ///

"""Smart Media Downloader.

Tips:
- `%(title).240B`: limite filename to 240 chars in output template, to avoid `file name too long` errors.
- `--max-filesize=2000M`: limit single file max size to 2G, to avoid huge file download.
- `--max-downloads=30`: limit max playlist item to 30, to avoid huage list download.
- `--no-playlist`: avoid downloading playlist unexpectedly for single item url like `https://www.youtube.com/watch?v=UVCa8...&list=PL...`
- macOS defaults `~/Movies` and `~/Music` are used here.
- `uvx yt-dlp@latest` will ensure `yt-dlp` is always up to date.
- `yt-dlp` will be blocked quickly if the host machine is in Cloud/DataCenter, use a residential IP if you can.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yt_dlp

MAX_VIDEO_SIZE = 2_000 * 1024 * 1024  # 2000M
MAX_AUDIO_SIZE = 30 * 1024 * 1024  # 30M
PLAYLIST_LIMIT = 30


HERE = Path(__file__).parent


def get_dir(candidates: list[str], default: Path = HERE) -> Path:
    for candidate in candidates:
        if candidate:
            path = Path(candidate).expanduser().resolve()
            if path.is_dir():
                return path.expanduser().resolve()
    return default


def get_video_dir():
    candidates = [
        os.getenv("DL_VIDEO_DIR"),
        os.getenv("VIDEO_DIR"),
        "~/Movies",
        "~/Videos",
        "~/Downloads",
    ]
    return get_dir(candidates, default=HERE)


def get_music_dir():
    candidates = [
        os.getenv("DL_MUSIC_DIR"),
        os.getenv("MUSIC_DIR"),
        "~/Music",
        "~/Audio",
        "~/Downloads",
    ]
    return get_dir(candidates, default=HERE)


VIDEO_DIR = get_video_dir()
MUSIC_DIR = get_music_dir()


def fmt_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def tee_json(obj: Any, file=sys.stdout) -> Any:
    print(fmt_json(obj), file=file)
    return obj


class MediaKind(Enum):
    VIDEO = "video"
    MUSIC = "music"


@dataclass(frozen=True)
class DownloadPlan:
    id: str
    url: str
    kind: MediaKind
    target_dir: Path
    is_playlist: bool
    extractor: str


def detect_kind(info: dict[str, Any], url: str) -> MediaKind:
    host = (urlparse(url).hostname or "").lower()
    if "music." in host:
        return MediaKind.MUSIC

    ie_key = (info.get("extractor_key") or info.get("extractor") or "").lower()
    if "music" in ie_key or "soundcloud" in ie_key or "spotify" in ie_key:
        return MediaKind.MUSIC

    categories = [c.lower() for c in info.get("categories") or []]
    if any("music" in cat for cat in categories):
        return MediaKind.MUSIC

    if info.get("track") or info.get("artist") or info.get("album"):
        return MediaKind.MUSIC

    return MediaKind.VIDEO


def detect_playlist(info: dict[str, Any]) -> bool:
    entry_type = info.get("_type")
    if entry_type in {"playlist", "multi_video", "multi_track", "multi_song"}:
        return True
    if "entries" in info:
        return True
    return bool(info.get("playlist_count"))


def probe(args) -> DownloadPlan:
    url = args.url
    probe_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "discard_in_playlist",
        "ignoreerrors": True,
        "noplaylist": False,
    }
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    id = info.get("id")
    if args.verbose:
        with open(f'info-{id}.json', 'w') as f:
            tee_json(info, file=f)

    kind = detect_kind(info, url)
    if kind is MediaKind.MUSIC:
        target_dir = args.music_dir
    else:
        target_dir = args.video_dir
    return DownloadPlan(
        id=info.get("id"),
        url=info.get("webpage_url", url),
        kind=kind,
        target_dir=target_dir,
        is_playlist=detect_playlist(info),
        extractor=info.get("extractor") or info.get("extractor_key") or "unknown",
    )


def build_options(plan: DownloadPlan) -> dict[str, Any]:
    outtmpl = (
        "%(playlist_title)s/%(title).240B.%(ext)s"
        if plan.is_playlist
        else "%(title).240B.%(ext)s"
    )

    opts: dict[str, Any] = {
        "outtmpl": {"default": outtmpl},
        "paths": {
            "home": str(plan.target_dir),
        },
        "noplaylist": not plan.is_playlist,
        "max_downloads": PLAYLIST_LIMIT if plan.is_playlist else None,
        "quiet": False,
        "concurrent_fragment_downloads": 4,
        "retries": 3,
    }

    if plan.kind is MediaKind.VIDEO:
        opts.update(
            format="bestvideo[vcodec^=avc1]+bestaudio/best",
            merge_output_format="mp4",
            max_filesize=MAX_VIDEO_SIZE,
        )
    else:
        opts.update(
            format="bestaudio/best",
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "0",
                },
            ],
            max_filesize=MAX_AUDIO_SIZE,
        )

    if opts["max_downloads"] is None:
        opts.pop("max_downloads")

    return opts


def print_plan(plan: DownloadPlan) -> None:
    playlist_label = "yes" if plan.is_playlist else "no"
    lines = [
        "Download Plan:",
        f"  url: {plan.url}",
        f"  id: {plan.id}",
        f"  kind: {plan.kind.value}",
        f"  playlist: {playlist_label}",
        f"  extractor: {plan.extractor}",
        f"  target_dir: {plan.target_dir}",
    ]
    print("\n".join(lines))


def download(plan: DownloadPlan) -> None:
    opts = build_options(plan)
    print_plan(plan)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([plan.url])


def cli():
    parser = argparse.ArgumentParser(
        prog="Smart Media Downloader",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("url", help="Media URL to download")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose logging",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Probe and print the plan without downloading",
    )
    parser.add_argument(
        "-m", "--music", action="store_true",
        help="Download best quality audio from url",
    )
    parser.add_argument(
        "-a", "--audio", action="store_true",
        help="Download decent quality audio from url",
    )
    parser.add_argument(
        "-s", "--subtitle", action="store_true",
        help="Download subtitle from url",
    )
    parser.add_argument(
        "-f", "--format",
        help="yt-dlp format string",
    )
    parser.add_argument(
        "-M", "--music_dir",
        default=MUSIC_DIR,
        help="Music directory",
    )
    parser.add_argument(
        "-V", "--video_dir",
        default=VIDEO_DIR,
        help="Video directory",
    )
    return parser.parse_args()


def main() -> None:
    args = cli()
    plan = probe(args)
    print_plan(plan)

    if args.dry_run:
        return

    try:
        download(plan)
    except yt_dlp.utils.DownloadError as exc:  # type: ignore[attr-defined]
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
