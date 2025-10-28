# Makefile for generating timelapse videos from capture directories
#
# Usage:
#   make capture-20251028-150225.mp4
#
# This will compile all JPG frames in capture-20251028-150225/ into a video

# Default settings
FRAMERATE ?= 30
FONTFILE ?= /Users/spierce/Library/Fonts/InputMonoNarrow-Thin.ttf
PRESET ?= veryslow

# Pattern rule: %.mp4 depends on %/ directory
%.mp4: %
	@echo "Generating video: $@"
	@echo "Source directory: $<"
	@if [ ! -d "$<" ]; then \
		echo "Error: Directory '$<' does not exist"; \
		exit 1; \
	fi
	@if [ -z "$$(ls -A $</*.jpg 2>/dev/null)" ]; then \
		echo "Error: No JPG files found in '$<'"; \
		exit 1; \
	fi
	ffmpeg -framerate $(FRAMERATE) \
		-pattern_type glob -i '$</*.jpg' \
		-vf "drawtext=fontfile=$(FONTFILE):text='Frame %{frame_num}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.25:boxborderw=5:x=10:y=10" \
		-c:v libx264 -pix_fmt yuv420p \
		-preset $(PRESET) \
		-y $@
	@echo "Video created: $@"

# Clean up all generated mp4 files
.PHONY: clean
clean:
	rm -f *.mp4

# List all capture directories
.PHONY: list
list:
	@echo "Available capture directories:"
	@ls -d capture-* 2>/dev/null || echo "No capture directories found"

# Help target
.PHONY: help
help:
	@echo "Timelapse Video Generator"
	@echo ""
	@echo "Usage:"
	@echo "  make <directory-name>.mp4    Generate video from directory"
	@echo "  make list                    List available capture directories"
	@echo "  make clean                   Remove all generated mp4 files"
	@echo ""
	@echo "Options (can be overridden):"
	@echo "  FRAMERATE=$(FRAMERATE)           Frames per second"
	@echo "  PRESET=$(PRESET)             FFmpeg encoding preset (ultrafast, fast, medium, slow, veryslow)"
	@echo ""
	@echo "Example:"
	@echo "  make capture-20251028-150225.mp4"
	@echo "  make FRAMERATE=60 capture-20251028-150225.mp4"
