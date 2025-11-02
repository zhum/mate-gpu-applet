#!/bin/bash

# GPU Monitor Cinnamon Applet Installation Script

set -e

APPLET_UUID="gpu-monitor@cinnamon"
APPLET_DIR="$HOME/.local/share/cinnamon/applets/$APPLET_UUID"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing GPU Monitor Cinnamon Applet..."

# Check if Cinnamon is installed
if ! command -v cinnamon &> /dev/null; then
    echo "Error: Cinnamon desktop environment not found."
    echo "This applet is designed for the Cinnamon desktop environment."
    exit 1
fi

# Create applet directory
echo "Creating applet directory: $APPLET_DIR"
mkdir -p "$APPLET_DIR"

# Copy applet files
echo "Copying applet files..."
cp "$SCRIPT_DIR/$APPLET_UUID/applet.js" "$APPLET_DIR/"
cp "$SCRIPT_DIR/$APPLET_UUID/metadata.json" "$APPLET_DIR/"
cp "$SCRIPT_DIR/$APPLET_UUID/settings-schema.json" "$APPLET_DIR/"

echo "Installation completed successfully!"
echo
echo "To add the applet to your panel:"
echo "1. Right-click on the Cinnamon panel"
echo "2. Select 'Applets'"
echo "3. Click on 'Download' tab and search for 'GPU Monitor'"
echo "   OR click on 'Installed' tab and look for 'GPU Monitor'"
echo "4. Click the '+' button to add it to your panel"
echo
echo "For GPU monitoring to work, ensure you have the required tools:"
echo "- For NVIDIA GPUs: nvidia-smi (usually comes with NVIDIA drivers)"
echo "- For AMD GPUs: radeontop package"
echo "  Install with: sudo apt install radeontop"
echo
echo "You may need to restart Cinnamon (Alt+F2, type 'r', press Enter) or log out and back in."
