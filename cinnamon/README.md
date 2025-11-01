# GPU Monitor Cinnamon Applet

A Cinnamon desktop applet that monitors GPU performance and displays real-time usage, temperature, and memory information in the panel.

## Installation

1. Run the installation script:

   ```bash
   chmod +x install-cinnamon.sh
   ./install-cinnamon.sh
   ```

2. Add to panel:
   - Right-click on Cinnamon panel
   - Select "Applets"
   - Find "GPU Monitor" and click the '+' button
   - You may need to restart Cinnamon (Alt+F2, type 'r', press Enter)

## Requirements

- Cinnamon Desktop Environment
- For NVIDIA GPUs: nvidia-smi (usually comes with NVIDIA drivers)
- For AMD GPUs: radeontop package (`sudo apt install radeontop`)

## Features

- Real-time GPU utilization, temperature, and memory monitoring
- Support for both NVIDIA and AMD GPUs
- Configurable display options
- Automatic data refresh every 2 seconds
- Informative tooltips

## Configuration

Right-click the applet and select "Configure..." to access settings:

- Enable/disable individual metrics (GPU load, temperature, memory)
- Chart display options (currently for future use)
- Chart appearance settings

## Files

- `applet.js` - Main applet code
- `metadata.json` - Applet metadata and compatibility info
- `settings-schema.json` - Configuration schema
- `install-cinnamon.sh` - Installation script

## License

Apache-2.0 License
