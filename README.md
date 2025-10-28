# Time Lapse Python

A CLI tool for capturing timelapse images from cameras and generating videos.

## Installation

```bash
# Clone the repository
git clone https://github.com/ddrscott/timelapse-py.git
cd timelapse-py

# Install with uv
uv sync

# Or install with pip
pip install -e .
```

## Requirements

- Python 3.13+
- ffmpeg (for video generation)
- A camera device

## Usage

### Recording

List recording devices:
```bash
timelapse devices
```

Start a timelapse recording:
```bash
timelapse start -d 0 -s 1 [output_dir]
```
- `-d` can be device name ("Anker"), device ID (1201), or index (0)
- `-s 1` specifies a 1 second interval between captures
- `output_dir` is optional; defaults to `capture-YYYYMMDD-HHMMSS/`
- `ctrl-c` to stop recording

### Creating Videos

**Using the Makefile (recommended):**
```bash
make capture-20251028-150225.mp4
```
- Automatically generates video from matching directory
- Includes frame number overlay
- Uses high-quality encoding preset

Customize encoding:
```bash
make FRAMERATE=60 capture-20251028-150225.mp4
make PRESET=medium capture-20251028-150225.mp4
```

List available captures:
```bash
make list
```

**Manual ffmpeg commands:**

Basic video (no overlay):
```bash
ffmpeg -framerate 30 -pattern_type glob -i 'capture-20251028-150225/*.jpg' -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

With frame number overlay (macOS):
```bash
ffmpeg -framerate 30 -pattern_type glob -i 'capture-20251028-150225/*.jpg' \
  -vf "drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='Frame %{frame_num}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.25:boxborderw=5:x=10:y=10" \
  -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```
