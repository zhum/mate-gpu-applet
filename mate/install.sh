#!/bin/bash

# Install script for MATE GPU Applet

echo "Installing MATE GPU Applet..."

# Make applet executable
chmod +x mate_gpu_applet.py

# Copy files to system directories
sudo cp mate_gpu_applet.py /usr/lib/mate-applets/
sudo cp org.mate.panel.GPUApplet.mate-panel-applet /usr/share/mate-panel/applets/
sudo cp mate-gpu-applet.desktop /usr/share/applications/
sudo cp org.mate.panel.applet.GPUAppletFactory.service /usr/share/dbus-1/services/

# Set proper permissions
sudo chmod +x /usr/lib/mate-applets/mate_gpu_applet.py

echo "Installation complete!"
echo "Restart MATE panel: mate-panel --replace &"
echo "You can now add the GPU Monitor applet to your MATE panel by:"
echo "1. Right-clicking on the panel"
echo "2. Selecting 'Add to Panel...'"
echo "3. Finding 'GPU Monitor' in the list"
