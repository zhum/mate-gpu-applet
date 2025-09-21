#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('MatePanelApplet', '4.0')

from gi.repository import Gtk, GObject, MatePanelApplet, GLib
import subprocess
import re

class GPUApplet:
    def __init__(self, applet):
        self.applet = applet
        
        self.label = Gtk.Label()
        self.label.set_text("GPU: --")
        
        self.applet.add(self.label)
        self.applet.show_all()
        
        self.update_gpu_info()
        GLib.timeout_add_seconds(2, self.update_gpu_info)
        
    def get_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    usage, temp = lines[0].split(', ')
                    return f"GPU: {usage}% {temp}°C"
        except:
            pass
        
        try:
            result = subprocess.run(['radeontop', '-d', '-l1'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'gpu (\d+\.\d+)%', result.stdout)
                if match:
                    usage = match.group(1)
                    return f"GPU: {usage}%"
        except:
            pass
            
        return "GPU: N/A"
    
    def update_gpu_info(self):
        gpu_info = self.get_gpu_usage()
        self.label.set_text(gpu_info)
        return True

def applet_factory(applet, iid, data):
    if iid != "GPUApplet":
        return False
    
    GPUApplet(applet)
    return True

def main():
    import sys
    import signal
    
    # Handle SIGINT and SIGTERM gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    
    try:
        MatePanelApplet.Applet.factory_main("GPUAppletFactory", True,
                                            MatePanelApplet.Applet.__gtype__,
                                            applet_factory, None)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()