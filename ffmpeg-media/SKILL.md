---
name: ffmpeg-media
description: FFmpeg media processing patterns covering video encoding, audio extraction, format conversion, streaming, filters, subtitles, thumbnails, and batch processing.
---

# FFmpeg Media Processing

This skill should be used when processing media files with FFmpeg. It covers video encoding, audio extraction, format conversion, streaming, filters, subtitles, and batch processing.

## When to Use This Skill

Use this skill when you need to:

- Convert video/audio between formats
- Extract audio or frames from video
- Apply filters (resize, crop, overlay, watermark)
- Generate thumbnails and video previews
- Set up streaming pipelines

## Basic Operations

```bash
# Convert format
ffmpeg -i input.mp4 output.webm

# Convert with codec specification
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -b:a 128k output.mp4

# Extract audio
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# Extract audio as WAV
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 44100 audio.wav

# Remove audio from video
ffmpeg -i input.mp4 -an -c:v copy output_silent.mp4

# Get media info
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Video Encoding

```bash
# H.264 high quality
ffmpeg -i input.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  output.mp4

# H.265/HEVC (smaller files)
ffmpeg -i input.mp4 \
  -c:v libx265 -preset medium -crf 22 \
  -c:a aac -b:a 128k \
  output_hevc.mp4

# VP9 for web
ffmpeg -i input.mp4 \
  -c:v libvpx-vp9 -b:v 2M -crf 30 \
  -c:a libopus -b:a 128k \
  output.webm

# AV1 (best compression)
ffmpeg -i input.mp4 \
  -c:v libaom-av1 -crf 30 -b:v 0 \
  -c:a libopus \
  output_av1.webm

# Two-pass encoding for target bitrate
ffmpeg -i input.mp4 -c:v libx264 -b:v 4M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 4M -pass 2 output.mp4
```

## Filters

```bash
# Resize
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4
ffmpeg -i input.mp4 -vf "scale=-2:720" output.mp4  # maintain aspect ratio

# Crop (width:height:x:y)
ffmpeg -i input.mp4 -vf "crop=640:480:100:50" output.mp4

# Rotate
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4  # 90 degrees clockwise

# Speed up / slow down
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" fast.mp4
ffmpeg -i input.mp4 -vf "setpts=2.0*PTS" -af "atempo=0.5" slow.mp4

# Add watermark
ffmpeg -i input.mp4 -i watermark.png \
  -filter_complex "overlay=W-w-10:H-h-10" \
  output.mp4

# Combine filters
ffmpeg -i input.mp4 \
  -vf "scale=1280:720,eq=brightness=0.05:contrast=1.1:saturation=1.2" \
  output.mp4
```

## Thumbnails and Previews

```bash
# Single frame at timestamp
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 thumbnail.jpg

# Thumbnail grid (4x4)
ffmpeg -i input.mp4 \
  -vf "select='not(mod(n,100))',scale=320:180,tile=4x4" \
  -frames:v 1 preview_grid.jpg

# Extract frame every N seconds
ffmpeg -i input.mp4 -vf "fps=1/10" frame_%04d.jpg

# Animated GIF
ffmpeg -i input.mp4 \
  -ss 00:00:05 -t 3 \
  -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  output.gif

# Video preview (short clip)
ffmpeg -i input.mp4 -ss 00:00:30 -t 10 -c copy preview.mp4
```

## Trimming and Joining

```bash
# Trim (fast, no re-encode)
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:30 -c copy trimmed.mp4

# Trim with re-encode (precise cuts)
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:30 \
  -c:v libx264 -c:a aac trimmed.mp4

# Concatenate files
# First create concat list: file 'part1.mp4'\nfile 'part2.mp4'
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

## Subtitles

```bash
# Burn subtitles into video
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# Add subtitle stream
ffmpeg -i input.mp4 -i subs.srt \
  -c copy -c:s mov_text \
  output.mp4

# Extract subtitles
ffmpeg -i input.mp4 -map 0:s:0 subtitles.srt
```

## Node.js Integration

```typescript
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

async function convertVideo(input: string, output: string): Promise<void> {
  await execFileAsync("ffmpeg", [
    "-i", input,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "-c:a", "aac",
    "-b:a", "128k",
    "-movflags", "+faststart",
    "-y",
    output,
  ]);
}

async function getMetadata(file: string) {
  const { stdout } = await execFileAsync("ffprobe", [
    "-v", "quiet",
    "-print_format", "json",
    "-show_format",
    "-show_streams",
    file,
  ]);
  return JSON.parse(stdout);
}
```

## Additional Resources

- FFmpeg Docs: https://ffmpeg.org/documentation.html
- FFmpeg Filters: https://ffmpeg.org/ffmpeg-filters.html
- FFmpeg Wiki: https://trac.ffmpeg.org/wiki
