---
name: dl
description: Download media smartly into Media Server folders and play on TV directly.
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://github.com/guoqiao/skills/blob/main/dl/dl/SKILL.md","os":["darwin","linux","win32"],"requires":{"bins":["uv"]}}}
triggers:
- "/dl <url>"
- "Download this video ..."
- "Download this music ..."
---

# Smart Media Downloader

Download media (via yt-dlp,  more tools comming) with expected formats and folders, and optionally, auto share with Media Server in LAN, watch on TV directly.

For Agent: use this skill when the user types `/dl <url>` or asks to download a video/music from YouTube/Bilibili/X/etc url.

## Usage

Just run this python uv script:
```
uv run --script ${baseDir}/dl.py $url
```
Which will auto detect Video/Music and Single/Playlist info from the url, and save to corresponding locations.

## Examples

Video:
- `https://youtube.com/watch?v=<id>`  -> save to `~/Movies/<name>.mp4`
- `https://youtube.com/playlist?list=PL...`  -> save to `~/Movies/<playlist>/*.mp4`

Music:
- `https://music.youtube.com/watch?v=<id>`  -> save to `~/Music/<name>.m4a`
- `https://music.youtube.com/playlist?list=PL...`  -> save to `~/Music/<playlist>/*.m4a`


## Extra Setup For Human

To make this skill really useful and different from other media downloaders:
- Install a DLNA/UPnP Media Server on this machine, e.g.: Universal Media Server(preferred on mac), miniDLNA, Jellyfin, etc.
- Add the ~/Music and ~/Movies (or ~/Videos) folders to the media server to share over LAN.
- Downloaded media with this skill, it will save media into these folders automatically.
- Play the media on other devices(e.g.: TV) directly, which will be shared by the media server.
