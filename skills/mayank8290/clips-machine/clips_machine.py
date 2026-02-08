#!/usr/bin/env python3
"""
Clips Machine - Transform long videos into viral short-form clips
100% Free tools - Whisper + FFmpeg

Usage:
    python clips_machine.py "https://youtube.com/watch?v=VIDEO_ID"
    python clips_machine.py /path/to/video.mp4 --clips 10
    python clips_machine.py VIDEO --style hormozi
"""

import os
import sys
import json
import argparse
import tempfile
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Add shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
from video_utils import (
    transcribe_with_timestamps,
    download_video,
    cut_video,
    add_captions,
    crop_to_vertical,
    get_video_duration,
    OUTPUT_DIR
)


# =============================================================================
# VIRAL MOMENT DETECTION
# =============================================================================

VIRAL_DETECTION_PROMPT = """Analyze this transcript and find the most viral-worthy moments for short-form video clips (TikTok, YouTube Shorts, Reels).

TRANSCRIPT:
{transcript}

Find moments that have:
1. HOOK POTENTIAL - Strong opening that grabs attention in first 3 seconds
2. EMOTIONAL PEAKS - Passion, excitement, surprise, humor
3. QUOTABLE LINES - Memorable statements people would share
4. CONTROVERSIAL TAKES - Opinions that spark debate
5. SURPRISING FACTS - "I didn't know that" moments
6. STORY CLIMAXES - Resolution of tension or conflict
7. ACTIONABLE ADVICE - Clear, specific takeaways

For each moment, provide:
- start_time: timestamp in seconds
- end_time: timestamp in seconds (aim for 30-60 second clips)
- score: virality score 1-100
- hook: the opening line (first 10 words)
- reason: why this moment is viral-worthy

Return as JSON array, sorted by score (highest first):
[
  {{
    "start_time": 125.5,
    "end_time": 172.3,
    "score": 95,
    "hook": "Here's the thing nobody tells you about...",
    "reason": "Strong hook + controversial opinion + clear takeaway"
  }},
  ...
]

Return the top {num_clips} moments."""


def detect_viral_moments(
    transcript: List[Dict],
    num_clips: int = 5,
    min_score: int = 50
) -> List[Dict]:
    """
    Analyze transcript to find viral-worthy moments

    This uses pattern matching + heuristics for standalone mode.
    In OpenClaw, this would use the LLM for smarter detection.
    """
    moments = []

    # Convert segments to full text with timestamps
    full_text = ""
    word_timestamps = []

    for seg in transcript:
        start = seg.get("start", 0)
        end = seg.get("end", start + 5)
        text = seg.get("text", "")
        full_text += f"[{start:.1f}s] {text}\n"

        # Track word positions
        words = text.split()
        duration = end - start
        for i, word in enumerate(words):
            word_time = start + (i / len(words)) * duration
            word_timestamps.append({"word": word, "time": word_time})

    # Pattern-based viral moment detection
    viral_patterns = [
        # Strong hooks
        (r"here'?s the thing|the truth is|nobody tells you|secret is|what if i told you", 30),
        (r"i'm going to (show|tell|reveal|share)", 25),
        (r"the (biggest|number one|most important|real) (mistake|problem|issue|secret)", 28),

        # Questions (engagement)
        (r"(have you ever|did you know|what if|why do|how (do|can|does))[^.?]*\?", 20),

        # Emotional intensity
        (r"(absolutely|literally|honestly|seriously|actually) (insane|crazy|wild|incredible|unbelievable)", 25),
        (r"this (changed|blew|shocked|surprised) (my|everything)", 22),
        (r"i (couldn'?t believe|was shocked|never expected)", 20),

        # Controversy/bold claims
        (r"(everyone|most people|nobody) (is wrong|gets this wrong|misses this)", 28),
        (r"(stop|don'?t|never|always) (doing|saying|believing)", 22),
        (r"(controversial|unpopular) (opinion|take|thought)", 30),

        # Story elements
        (r"(and then|suddenly|that'?s when|at that moment)", 15),
        (r"(the turning point|everything changed|that'?s when i realized)", 25),

        # Actionable advice
        (r"(step (one|two|three|1|2|3)|first thing|here'?s (how|what))", 20),
        (r"(you (need to|should|must|have to)|the key is|the trick is)", 18),

        # Numbers/lists
        (r"(three|four|five|3|4|5|10) (things|ways|tips|secrets|mistakes|reasons)", 22),
    ]

    # Scan transcript for patterns
    text_lower = full_text.lower()

    for pattern, base_score in viral_patterns:
        for match in re.finditer(pattern, text_lower):
            # Find timestamp for this position
            match_pos = match.start()
            lines_before = text_lower[:match_pos].count('\n')

            # Get approximate timestamp
            if lines_before < len(transcript):
                seg = transcript[lines_before]
                start_time = seg.get("start", 0)

                # Calculate clip end (30-60 seconds)
                clip_duration = 45  # Default
                end_time = start_time + clip_duration

                # Extract hook text
                hook_text = match.group(0)[:50]

                # Boost score based on position (earlier = more important as hook)
                position_bonus = max(0, 10 - (lines_before / len(transcript)) * 10)

                moments.append({
                    "start_time": max(0, start_time - 2),  # Start 2s before for context
                    "end_time": end_time,
                    "score": min(100, base_score + position_bonus + 20),  # Add base score
                    "hook": hook_text.strip(),
                    "reason": f"Matched pattern: {pattern[:30]}...",
                    "pattern": pattern
                })

    # Remove duplicates (clips that overlap significantly)
    filtered_moments = []
    for moment in sorted(moments, key=lambda x: x["score"], reverse=True):
        # Check if this overlaps with existing clips
        overlaps = False
        for existing in filtered_moments:
            if (moment["start_time"] < existing["end_time"] and
                moment["end_time"] > existing["start_time"]):
                overlaps = True
                break

        if not overlaps and moment["score"] >= min_score:
            filtered_moments.append(moment)

        if len(filtered_moments) >= num_clips:
            break

    # If we didn't find enough, add evenly spaced clips
    if len(filtered_moments) < num_clips and transcript:
        total_duration = transcript[-1].get("end", 60)
        interval = total_duration / (num_clips + 1)

        for i in range(num_clips - len(filtered_moments)):
            start = interval * (i + 1)
            filtered_moments.append({
                "start_time": start,
                "end_time": min(start + 45, total_duration),
                "score": 40,
                "hook": f"Segment at {start:.0f}s",
                "reason": "Evenly distributed segment"
            })

    return filtered_moments[:num_clips]


# =============================================================================
# CAPTION STYLES
# =============================================================================

CAPTION_STYLES = {
    "hormozi": {
        "fontname": "Arial Black",
        "fontsize": 60,
        "primary": "&H00FFFFFF",
        "highlight": "&H0000FFFF",  # Yellow
        "outline": "&H00000000",
        "outline_width": 4,
        "shadow": 3,
        "alignment": 2,
        "marginv": 100,
        "words_per_highlight": 3
    },
    "minimal": {
        "fontname": "Helvetica Neue",
        "fontsize": 48,
        "primary": "&H00FFFFFF",
        "outline": "&H40000000",
        "outline_width": 2,
        "shadow": 0,
        "alignment": 2,
        "marginv": 80
    },
    "karaoke": {
        "fontname": "Arial Black",
        "fontsize": 54,
        "primary": "&H00FFFFFF",
        "highlight": "&H0000FF00",  # Green
        "outline": "&H00000000",
        "outline_width": 3,
        "shadow": 2,
        "alignment": 2,
        "marginv": 90,
        "word_by_word": True
    },
    "news": {
        "fontname": "Arial",
        "fontsize": 42,
        "primary": "&H00FFFFFF",
        "background": "&H80000000",
        "outline_width": 0,
        "shadow": 0,
        "alignment": 1,  # Bottom left
        "marginv": 50,
        "marginl": 50
    },
    "meme": {
        "fontname": "Impact",
        "fontsize": 70,
        "primary": "&H00FFFFFF",
        "outline": "&H00000000",
        "outline_width": 5,
        "shadow": 0,
        "alignment": 2,
        "marginv": 30,
        "all_caps": True
    }
}


def create_styled_captions(
    video_path: str,
    output_path: str,
    segments: List[Dict],
    style: str = "hormozi"
) -> str:
    """
    Create animated captions in various viral styles
    """
    style_config = CAPTION_STYLES.get(style, CAPTION_STYLES["hormozi"])

    # Generate ASS file with style
    ass_file = tempfile.mktemp(suffix=".ass")

    ass_header = f"""[Script Info]
Title: Clips Machine Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style_config['fontname']},{style_config['fontsize']},{style_config['primary']},{style_config.get('highlight', style_config['primary'])},{style_config['outline']},&H80000000,1,0,0,0,100,100,0,0,1,{style_config['outline_width']},{style_config.get('shadow', 2)},{style_config['alignment']},10,10,{style_config['marginv']},1
Style: Highlight,{style_config['fontname']},{style_config['fontsize']},{style_config.get('highlight', '&H0000FFFF')},{style_config['primary']},{style_config['outline']},&H80000000,1,0,0,0,100,100,0,0,1,{style_config['outline_width']},{style_config.get('shadow', 2)},{style_config['alignment']},10,10,{style_config['marginv']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = ""

    for seg in segments:
        start = format_ass_time(seg.get("start", 0))
        end = format_ass_time(seg.get("end", 0))
        text = seg.get("text", "")

        # Apply style transformations
        if style_config.get("all_caps"):
            text = text.upper()

        # Escape special characters
        text = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

        events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    with open(ass_file, "w") as f:
        f.write(ass_header + events)

    # Burn captions into video
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ], capture_output=True)

    os.unlink(ass_file)
    return output_path


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS timestamp (H:MM:SS.cc)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_video(
    source: str,
    num_clips: int = 5,
    style: str = "hormozi",
    no_captions: bool = False,
    start_time: float = None,
    end_time: float = None,
    min_score: int = 50,
    output_name: str = None
) -> Dict:
    """
    Process a video into viral clips

    Args:
        source: YouTube URL or local file path
        num_clips: Number of clips to generate
        style: Caption style (hormozi, minimal, karaoke, news, meme)
        no_captions: Skip caption generation
        start_time: Only process from this timestamp
        end_time: Only process until this timestamp
        min_score: Minimum virality score to include
        output_name: Custom output folder name

    Returns:
        Dict with paths to generated files
    """
    print(f"\n✂️ Clips Machine: Processing video")
    print("=" * 60)

    # Determine output directory
    if output_name is None:
        if source.startswith("http"):
            output_name = f"clips-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        else:
            output_name = f"clips-{Path(source).stem}"

    output_dir = OUTPUT_DIR / output_name
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {"directory": str(output_dir), "clips": []}

    # ==========================================================================
    # STEP 1: Download/Load Video
    # ==========================================================================
    print("\n📥 Step 1/5: Loading video...")

    if source.startswith("http"):
        print(f"   Downloading from: {source[:50]}...")
        video_path = str(output_dir / "source.mp4")
        download_video(source, video_path)
    else:
        video_path = source

    if not os.path.exists(video_path):
        print(f"   ❌ Video not found: {video_path}")
        return results

    duration = get_video_duration(video_path)
    print(f"   ✓ Video loaded ({duration:.1f}s)")

    results["source"] = video_path
    results["duration"] = duration

    # ==========================================================================
    # STEP 2: Transcribe
    # ==========================================================================
    print("\n🎤 Step 2/5: Transcribing audio...")

    transcript = transcribe_with_timestamps(video_path)

    # Save transcript
    transcript_path = output_dir / "transcript.json"
    with open(transcript_path, "w") as f:
        json.dump(transcript, f, indent=2)

    results["transcript"] = str(transcript_path)
    print(f"   ✓ Transcribed {len(transcript)} segments")

    # ==========================================================================
    # STEP 3: Detect Viral Moments
    # ==========================================================================
    print("\n🔍 Step 3/5: Detecting viral moments...")

    # Filter transcript by time range if specified
    if start_time or end_time:
        filtered = []
        for seg in transcript:
            seg_start = seg.get("start", 0)
            seg_end = seg.get("end", 0)
            if (start_time is None or seg_start >= start_time) and \
               (end_time is None or seg_end <= end_time):
                filtered.append(seg)
        transcript = filtered

    moments = detect_viral_moments(transcript, num_clips=num_clips, min_score=min_score)

    # Save moments
    moments_path = output_dir / "viral_moments.json"
    with open(moments_path, "w") as f:
        json.dump(moments, f, indent=2)

    results["viral_moments"] = str(moments_path)
    print(f"   ✓ Found {len(moments)} viral moments")

    for i, m in enumerate(moments):
        print(f"      {i+1}. [{m['score']}] {m['hook'][:40]}...")

    # ==========================================================================
    # STEP 4: Cut Clips
    # ==========================================================================
    print("\n✂️ Step 4/5: Cutting clips...")

    clip_paths = []
    for i, moment in enumerate(moments):
        clip_name = f"clip_{i+1:03d}.mp4"
        clip_path = str(output_dir / clip_name)

        # Cut the segment
        temp_clip = str(output_dir / f"temp_{i}.mp4")
        cut_video(
            video_path,
            temp_clip,
            moment["start_time"],
            moment["end_time"]
        )

        # Convert to vertical
        vertical_clip = str(output_dir / f"vertical_{i}.mp4")
        crop_to_vertical(temp_clip, vertical_clip)

        clip_paths.append({
            "path": vertical_clip,
            "moment": moment,
            "final_path": clip_path
        })

        print(f"   ✓ Cut clip {i+1}/{len(moments)}")

        # Cleanup temp
        if os.path.exists(temp_clip):
            os.unlink(temp_clip)

    # ==========================================================================
    # STEP 5: Add Captions
    # ==========================================================================
    if not no_captions:
        print(f"\n💬 Step 5/5: Adding {style} captions...")

        for i, clip_info in enumerate(clip_paths):
            # Get transcript segments for this clip
            moment = clip_info["moment"]
            clip_segments = []

            for seg in transcript:
                seg_start = seg.get("start", 0)
                seg_end = seg.get("end", 0)

                # Check if segment overlaps with clip
                if seg_start < moment["end_time"] and seg_end > moment["start_time"]:
                    # Adjust timestamps relative to clip start
                    clip_segments.append({
                        "start": max(0, seg_start - moment["start_time"]),
                        "end": seg_end - moment["start_time"],
                        "text": seg.get("text", "")
                    })

            # Add captions
            create_styled_captions(
                clip_info["path"],
                clip_info["final_path"],
                clip_segments,
                style=style
            )

            results["clips"].append(clip_info["final_path"])
            print(f"   ✓ Captioned clip {i+1}/{len(clip_paths)}")

            # Cleanup intermediate
            if os.path.exists(clip_info["path"]):
                os.unlink(clip_info["path"])
    else:
        print("\n⏭️ Step 5/5: Skipping captions...")
        for clip_info in clip_paths:
            # Just rename vertical to final
            os.rename(clip_info["path"], clip_info["final_path"])
            results["clips"].append(clip_info["final_path"])

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    summary = f"""# Clips Machine Output

Source: {source}
Duration: {duration:.1f}s
Clips Generated: {len(results['clips'])}
Caption Style: {style}

## Viral Moments Detected

"""
    for i, moment in enumerate(moments):
        summary += f"""### Clip {i+1} (Score: {moment['score']})
- **Time:** {moment['start_time']:.1f}s - {moment['end_time']:.1f}s
- **Hook:** {moment['hook']}
- **Reason:** {moment['reason']}
- **File:** clip_{i+1:03d}.mp4

"""

    summary_path = output_dir / "summary.md"
    with open(summary_path, "w") as f:
        f.write(summary)

    results["summary"] = str(summary_path)

    print("\n" + "=" * 60)
    print("✅ CLIPS GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output folder: {output_dir}")
    print(f"\n🎬 Generated {len(results['clips'])} clips:")
    for clip in results["clips"]:
        print(f"   • {Path(clip).name}")
    print(f"\n🚀 Ready to upload to TikTok, Reels, and Shorts!")

    return results


# =============================================================================
# CLI
# =============================================================================

def parse_timestamp(ts: str) -> float:
    """Parse timestamp string (MM:SS or HH:MM:SS) to seconds"""
    parts = ts.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return float(ts)


def main():
    parser = argparse.ArgumentParser(
        description="Clips Machine - Turn long videos into viral clips"
    )
    parser.add_argument("source", help="YouTube URL or local video path")
    parser.add_argument("--clips", type=int, default=5,
                        help="Number of clips to generate")
    parser.add_argument("--style", default="hormozi",
                        choices=["hormozi", "minimal", "karaoke", "news", "meme"],
                        help="Caption style")
    parser.add_argument("--no-captions", action="store_true",
                        help="Skip caption generation")
    parser.add_argument("--start", type=str,
                        help="Start timestamp (MM:SS)")
    parser.add_argument("--end", type=str,
                        help="End timestamp (MM:SS)")
    parser.add_argument("--min-score", type=int, default=50,
                        help="Minimum virality score")
    parser.add_argument("--output", help="Custom output folder name")

    args = parser.parse_args()

    start_time = parse_timestamp(args.start) if args.start else None
    end_time = parse_timestamp(args.end) if args.end else None

    process_video(
        source=args.source,
        num_clips=args.clips,
        style=args.style,
        no_captions=args.no_captions,
        start_time=start_time,
        end_time=end_time,
        min_score=args.min_score,
        output_name=args.output
    )


if __name__ == "__main__":
    main()
