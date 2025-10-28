import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import click
import cv2
from cv2_enumerate_cameras import enumerate_cameras
from rich.live import Live
from rich.table import Table


def resolve_device(device_input: str) -> int:
    """Resolve device input (name, device_id, or index) to OpenCV device index.

    Args:
        device_input: Can be device name (e.g., 'Anker PowerConf C200'),
                     device_id (e.g., '1201'), or index (e.g., '0')

    Returns:
        OpenCV device index

    Raises:
        click.ClickException if device not found
    """
    cameras = list(enumerate_cameras())

    if not cameras:
        raise click.ClickException("No cameras found.")

    # Try to parse as integer first (could be device_id or index)
    try:
        int_value = int(device_input)

        # Check if it matches a device_id
        for camera in cameras:
            if camera.index == int_value:
                return camera.index

        # Check if it's a valid list index
        if 0 <= int_value < len(cameras):
            return cameras[int_value].index

        raise click.ClickException(
            f"Device '{device_input}' not found. Use 'timelapse devices' to list available cameras."
        )

    except ValueError:
        # Not an integer, treat as device name
        for camera in cameras:
            if camera.name and device_input.lower() in camera.name.lower():
                return camera.index

        raise click.ClickException(
            f"No camera found matching '{device_input}'. Use 'timelapse devices' to list available cameras."
        )


@click.group()
def cli():
    """Timelapse recording tool for capturing images at regular intervals."""
    pass


@cli.command()
def devices():
    """List available recording devices."""
    click.echo("Scanning for available cameras...")

    cameras = list(enumerate_cameras())

    if not cameras:
        click.echo("No cameras found.")
        sys.exit(1)

    click.echo(f"\nFound {len(cameras)} device(s):")
    for idx, camera_info in enumerate(cameras):
        click.echo(f"  [{idx}] {camera_info.index}: {camera_info.name}")


@cli.command()
@click.option('-d', '--device', default='0', type=str, help='Device name, device_id, or index (default: 0)')
@click.option('-s', '--interval', default=1, type=float, help='Interval between captures in seconds (default: 1)')
@click.argument('output_dir', type=click.Path(), required=False)
def start(device, interval, output_dir):
    """Start timelapse recording to OUTPUT_DIR.

    Press Ctrl-C to stop recording.

    If OUTPUT_DIR is not specified, defaults to capture-YYYYMMDD-HHMMSS/

    DEVICE can be specified as:
      - Index from the devices list: 0, 1, 2, etc.
      - Device ID: 1200, 1201, 1202, etc.
      - Device name (partial match): "Anker", "FaceTime", etc.
    """
    # Use timestamp-based directory if not specified
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = f"capture-{timestamp}"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Resolve device input to actual OpenCV device index
    device_index = resolve_device(device)

    # Setup signal handler for graceful shutdown
    stop_recording = {'flag': False}

    def signal_handler(sig, frame):
        click.echo("\nStopping recording...")
        stop_recording['flag'] = True

    signal.signal(signal.SIGINT, signal_handler)

    # Open camera
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        click.echo(f"Error: Could not open device {device_index}", err=True)
        sys.exit(1)

    click.echo(f"Recording from device {device_index} to {output_path}")
    click.echo(f"Capture interval: {interval} second(s)")
    click.echo("Press Ctrl-C to stop\n")

    frame_count = 0
    start_time = datetime.now()

    def generate_table():
        """Generate status table for live display."""
        # Calculate current duration
        duration = datetime.now() - start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Status", "Recording")
        table.add_row("Started", start_time.isoformat(sep=' ', timespec='seconds'))
        table.add_row("Duration", duration_str)
        table.add_row("Output", str(output_path))
        table.add_row("Frames", str(frame_count))
        if frame_count > 0:
            table.add_row("Latest", f"frame_{frame_count-1:06d}.jpg")
        return table

    # Create live display
    with Live(generate_table(), refresh_per_second=4) as live:
        try:
            while not stop_recording['flag']:
                ret, frame = cap.read()
                if not ret:
                    click.echo("Error: Failed to capture frame", err=True)
                    break

                # Save frame with zero-padded filename
                filename = output_path / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(filename), frame)

                frame_count += 1
                live.update(generate_table())

                # Wait for the interval
                time.sleep(interval)

        finally:
            cap.release()
            click.echo(f"\nRecording stopped. Captured {frame_count} frame(s).")


if __name__ == "__main__":
    cli()
