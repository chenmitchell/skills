---
name: video-download
description: Download videos from 1800+ websites and generate subtitles using Whisper AI. Use when user wants to download videos from YouTube, Bilibili, Twitter, TikTok, Facebook, Vimeo, or any other supported video site, extract audio, or transcribe video content to text/subtitles.
metadata:
  {
    "openclaw":
      {
        "homepage": "https://github.com/upupc/video-download",
        "emoji": "🎬",
        "requires": { "bins": ["python3", "ffmpeg"], "env": [] },
        "primaryEnv": "",
        "install": [
          {
            "id": "pip",
            "kind": "pip",
            "packages": ["yt-dlp", "ffmpeg-python", "openai-whisper"],
            "label": "Install dependencies (pip)",
          }
        ],
      },
  }
---

# Video Download & Subtitle Generation

This skill downloads videos from 1800+ websites and generates subtitles using Whisper AI.

## Supported Websites

This skill supports downloading from virtually any video website thanks to yt-dlp. Some popular ones include:

**Video Platforms:**
- YouTube, YouTube Shorts
- Bilibili (哔哩哔哩), Niconico (ニコニコ動画)
- TikTok, Douyin (抖音)
- Twitter/X, Facebook, Instagram
- Vimeo, Dailymotion
- Twitch (clips, VODs), Kick
- Rutube, VK Video

**Chinese Platforms:**
- iQiyi (爱奇艺), Youku (优酷), MangoTV (芒果TV)
- Weibo Video, Douyu (斗鱼), Huya (虎牙)

**International:**
- Netflix, Disney+, HBO Max, Amazon Prime Video
- BBC iPlayer, ITV, Channel 4
- ARD, ZDF, Arte

For the complete list of 1800+ supported sites, see: [yt-dlp supported extractors](references/supportedsites.md)

## Prerequisites

Ensure the following Python packages are installed:
- `yt-dlp` - For downloading videos from any supported site
- `ffmpeg-python` - For audio extraction
- `openai-whisper` - For speech-to-text transcription

Install via pip:
```bash
pip install yt-dlp ffmpeg-python openai-whisper
```

ffmpeg must also be installed on your system

## Usage

### Command Line

```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads"}'
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | array | Yes | List of video URLs from any supported website |
| `output` | string | No | Output directory (default: "./downloads") |
| `model` | string | No | Whisper model size: tiny, base, small, medium, large, turbo (default: "turbo") |
| `transcribe` | boolean | No | Whether to transcribe video to subtitle (default: true) |
| `subtitle_format` | string | No | Subtitle format: txt, srt, vtt, json (default: "txt") |
| `download_subtitle` | boolean | No | Download video's built-in subtitles if available (default: false) |

## Output

The skill will:
1. Create a folder for each video (named after the video title)
2. Download the video file to that folder
3. Extract audio as WAV file
4. Generate transcript using Whisper
5. Save subtitle as .txt file

Output structure:
```
downloads/
└── Video Title/
    ├── Video Title.mp4
    ├── Video Title.wav
    └── Video Title.txt
```

## Examples

### Download YouTube video:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],"output":"./my_videos"}'
```

### Download Bilibili video:
```bash
python scripts/video_parser.py '{"urls":["https://www.bilibili.com/video/BV1xx411c7XD"],"output":"./downloads"}'
```

### Download TikTok video:
```bash
python scripts/video_parser.py '{"urls":["https://www.tiktok.com/@username/video/1234567890"],"output":"./tiktok"}'
```

### Download multiple videos from different sites:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO1","https://www.bilibili.com/video/BV1xx","https://twitter.com/user/status/123"],"output":"./videos"}'
```

### Download Twitch clip:
```bash
python scripts/video_parser.py '{"urls":["https://www.twitch.tv//channel/clip/ClipName"],"output":"./clips"}'
```

### Download only (without transcription):
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads","transcribe":false}'
```

### Generate SRT subtitle:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads","subtitle_format":"srt"}'
```

### Generate VTT subtitle:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads","subtitle_format":"vtt"}'
```

### Download video with built-in subtitles:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads","download_subtitle":true}'
```

### Download with custom Whisper model:
```bash
python scripts/video_parser.py '{"urls":["https://www.youtube.com/watch?v=VIDEO_ID"],"output":"./downloads","model":"large"}'
```

## Troubleshooting

- **ffmpeg not found**: Install ffmpeg via `brew install ffmpeg` (macOS) or your system's package manager
- **Whisper model download slow**: The first run will download the model (~75MB for turbo). This is normal.
- **Download fails**: Some videos may be geo-restricted, age-gated, or unavailable. Check the video URL and try again.
- **Cookie/auth required**: Some sites need authentication. You can pass cookies via yt-dlp options if needed.
