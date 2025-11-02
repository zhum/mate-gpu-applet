# GPU Monitor Applet

A comprehensive desktop panel applet that monitors GPU performance with both text and graphical display modes. Available for both MATE and Cinnamon desktop environments.

## Features

- **GPU Monitoring**: Real-time GPU utilization, temperature, and memory usage
- **Chart Visualization**: Individual mini-charts for each metric with customizable width
- **GPU Support**: NVIDIA (via nvidia-smi) and AMD (via radeontop, UNTESTED!) GPUs
- **Persistent Settings**: Preferences saved automatically
- **Real-time Updates**: Data refreshes every 2 seconds, tunable
- **Lightweight**: Minimal resource usage

## Requirements

### MATE Version

- MATE Desktop Environment
- Python 3
- PyGObject (python3-gi)

### Cinnamon Version

- Cinnamon Desktop Environment

### GPU Support (Both Versions)

- For NVIDIA: nvidia-smi (usually comes with NVIDIA drivers)
- For AMD: radeontop package

## Installation

### MATE Version install

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

### Cinnamon Version install

1. Install dependencies:

   ```bash
   # For AMD support:
   sudo apt install radeontop
   ```

2. Run the install script:

   ```bash
   cd cinnamon
   chmod +x install-cinnamon.sh
   ./install-cinnamon.sh
   ```

3. Add to panel:
   - Right-click on Cinnamon panel
   - Select "Applets"
   - Find "GPU Monitor" in the Installed tab and click the '+' button
   - You may need to restart Cinnamon (Alt+F2, type 'r', press Enter)

## Usage

### Text Display Mode

The applet shows GPU information as text in the panel: `GPU: 45% | 65°C | Mem: 78%`

### Chart Display Mode

Switch to chart mode for mini real-time graphs in the panel showing trends for each enabled metric.

### Preferences

**MATE Version**: Right-click the applet and select "Preferences"

**Cinnamon Version**: Right-click the applet and select "Configure..." or use Cinnamon Settings > Applets

Available options:

- Enable/disable individual metrics (GPU load, temperature, memory)
- Switch between text and chart display modes
- Adjust chart width (30-100 pixels)
- Chart transparency and font size settings

### Full Chart Window

**MATE Version**: Right-click the applet and select "Show Charts" to open a detailed chart window with:

- Multi-line graphs for all enabled metrics
- Grid lines and value labels
- Color-coded legend
- 2-minute data history (60 data points)

**Note**: The Cinnamon version currently displays data in text format only.

## Development

### MATE Version development

To test the applet without installing:

```bash
python3 mate_gpu_applet.py
```

### Cinnamon Version development

To test the applet:

1. Copy the applet to the development location:

   ```bash
   mkdir -p ~/.local/share/cinnamon/applets/gpu-monitor@cinnamon
   cp cinnamon/gpu-monitor@cinnamon/* ~/.local/share/cinnamon/applets/gpu-monitor@cinnamon/
   ```

2. Restart Cinnamon (Alt+F2, type 'r', press Enter) and add the applet through the Applets menu

## Configuration

### MATE Version config

Settings are automatically saved to `~/.config/mate-gpu-applet.json`

### Cinnamon Version config

Settings are managed through Cinnamon's configuration system and accessed via the applet settings

Both versions include:

- Which metrics to display
- Text vs chart display mode preference
- Chart width, transparency, and font size settings

## Files

### MATE Version files

- `mate_gpu_applet.py` - Main applet code
- `org.mate.panel.GPUApplet.mate-panel-applet` - MATE applet configuration
- `org.mate.panel.applet.GPUAppletFactory.service` - D-Bus service file
- `mate-gpu-applet.desktop` - Desktop entry
- `setup.py` - Python setup script
- `install.sh` - Installation script

### Cinnamon Version files

- `cinnamon/gpu-monitor@cinnamon/applet.js` - Main applet code (JavaScript)
- `cinnamon/gpu-monitor@cinnamon/metadata.json` - Applet metadata
- `cinnamon/gpu-monitor@cinnamon/settings-schema.json` - Settings configuration
- `cinnamon/install-cinnamon.sh` - Installation script

## License

Apache-2.0 License

(C) Sergey Zhumatiy <sergzhum@gmail.com> 2025
