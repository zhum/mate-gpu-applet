# MATE GPU Applet

A comprehensive MATE desktop panel applet that monitors GPU performance with both text and graphical display modes.

## Features

- **GPU Monitoring**: Real-time GPU utilization, temperature, and memory usage
- **Dual Display Modes**: Switch between text display and graphical charts in panel
- **Chart Visualization**: Individual mini-charts for each metric with customizable width
- **Full Chart Window**: Detailed performance charts with grid lines and legends
- **Configurable Display**: Enable/disable specific metrics (GPU load, temperature, memory)
- **GPU Support**: NVIDIA (via nvidia-smi) and AMD (via radeontop) GPUs
- **Persistent Settings**: Preferences saved automatically
- **Real-time Updates**: Data refreshes every 2 seconds
- **Lightweight**: Minimal resource usage

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

## Usage

### Text Display Mode
The applet shows GPU information as text in the panel: `GPU: 45% | 65°C | Mem: 78%`

### Chart Display Mode
Switch to chart mode for mini real-time graphs in the panel showing trends for each enabled metric.

### Preferences
Right-click the applet and select "Preferences" to:
- Enable/disable individual metrics (GPU load, temperature, memory)
- Switch between text and chart display modes
- Adjust chart width (30-100 pixels)

### Full Chart Window
Right-click the applet and select "Show Charts" to open a detailed chart window with:
- Multi-line graphs for all enabled metrics
- Grid lines and value labels
- Color-coded legend
- 2-minute data history (60 data points)

## Development

To test the applet without installing:
```bash
python3 mate_gpu_applet.py
```

## Configuration

Settings are automatically saved to `~/.config/mate-gpu-applet.json` and include:
- Which metrics to display
- Text vs chart display mode preference
- Chart width setting

## Screenshots

### Text Mode
```
GPU: 45% | 65°C | Mem: 78%
```

### Chart Mode
Mini real-time charts showing trend lines for each enabled metric.

### Chart Window
Full-featured chart window with detailed graphs, grid, and legend.

## Files

- `mate_gpu_applet.py` - Main applet code (606 lines)
- `org.mate.panel.GPUApplet.mate-panel-applet` - MATE applet configuration
- `org.mate.panel.applet.GPUAppletFactory.service` - D-Bus service file
- `mate-gpu-applet.desktop` - Desktop entry
- `setup.py` - Python setup script
- `install.sh` - Installation script

## License

GPL-3.0 License