# MATE GPU Applet

A MATE desktop panel applet that monitors GPU usage and temperature.

## Features

- Displays GPU utilization percentage
- Shows GPU temperature (when available)
- Supports both NVIDIA (via nvidia-smi) and AMD (via radeontop) GPUs
- Updates every 2 seconds
- Lightweight and minimal resource usage

## Requirements

- MATE Desktop Environment
- Python 3
- PyGObject (python3-gi)
- For NVIDIA: nvidia-smi (usually comes with NVIDIA drivers)
- For AMD: radeontop package

## Installation

1. Install dependencies:
   ```bash
   sudo apt install python3-gi mate-panel-dev
   # For AMD support:
   sudo apt install radeontop
   ```

2. Run the install script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Add to panel:
   - Right-click on MATE panel
   - Select "Add to Panel..."
   - Find "GPU Monitor" and add it

## Development

To test the applet without installing:
```bash
python3 mate_gpu_applet.py
```

## Files

- `mate_gpu_applet.py` - Main applet code
- `org.mate.panel.GPUApplet.mate-panel-applet` - MATE applet configuration
- `mate-gpu-applet.desktop` - Desktop entry
- `setup.py` - Python setup script
- `install.sh` - Installation script