#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('MatePanelApplet', '4.0')

from gi.repository import Gtk, GObject, MatePanelApplet, GLib, Gio
import subprocess
import re
import json
import os

class GPUApplet:
    def __init__(self, applet):
        self.applet = applet
        self.config_file = os.path.expanduser("~/.config/mate-gpu-applet.json")
        
        # Load preferences
        self.preferences = {
            'show_gpu_load': True,
            'show_temperature': True,
            'show_memory': True
        }
        self.load_preferences()
        
        self.label = Gtk.Label()
        self.label.set_text("GPU: --")
        
        self.applet.add(self.label)
        self.applet.show_all()
        
        # Setup context menu
        self.setup_menu()
        
        self.update_gpu_info()
        GLib.timeout_add_seconds(2, self.update_gpu_info)
        
    def get_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    usage, mem_used, mem_total, temp = lines[0].split(', ')
                    mem_percent = round((int(mem_used) / int(mem_total)) * 100)
                    return self.format_display(usage=usage, temp=temp, mem_percent=mem_percent)
        except:
            pass
        
        try:
            result = subprocess.run(['radeontop', '-d', '-l1'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_match = re.search(r'gpu (\d+\.\d+)%', result.stdout)
                vram_match = re.search(r'vram (\d+\.\d+)%', result.stdout)
                if gpu_match:
                    usage = gpu_match.group(1)
                    vram = vram_match.group(1) if vram_match else None
                    return self.format_display(usage=usage, mem_percent=vram)
        except:
            pass
            
        return "GPU: N/A"
    
    def format_display(self, usage=None, temp=None, mem_percent=None):
        """Format display string based on preferences"""
        parts = []
        
        if usage is not None and self.preferences['show_gpu_load']:
            parts.append(f"GPU: {usage}%")
        
        if temp is not None and self.preferences['show_temperature']:
            parts.append(f"{temp}°C")
            
        if mem_percent is not None and self.preferences['show_memory']:
            parts.append(f"Mem: {mem_percent}%")
        
        if not parts:
            return "GPU: --"
        
        return " | ".join(parts) if len(parts) > 1 else parts[0]
    
    def update_gpu_info(self):
        gpu_info = self.get_gpu_usage()
        self.label.set_text(gpu_info)
        return True
    
    def load_preferences(self):
        """Load preferences from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_prefs = json.load(f)
                    self.preferences.update(saved_prefs)
        except Exception:
            pass  # Use defaults if loading fails
    
    def save_preferences(self):
        """Save preferences to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception:
            pass  # Silently fail if saving fails
    
    def setup_menu(self):
        """Setup right-click context menu"""
        action_group = Gtk.ActionGroup("GPUAppletActions")
        
        preferences_action = Gtk.Action("Preferences", "Preferences", "Configure GPU monitor", None)
        preferences_action.connect("activate", self.show_preferences)
        action_group.add_action(preferences_action)
        
        self.applet.setup_menu('<menuitem name="Preferences" action="Preferences" />', action_group)
    
    def show_preferences(self, action):
        """Show preferences dialog"""
        dialog = Gtk.Dialog("GPU Monitor Preferences", None, 
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.set_default_size(300, 200)
        
        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_border_width(10)
        
        # Create checkboxes
        self.gpu_load_check = Gtk.CheckButton("Show GPU Load")
        self.gpu_load_check.set_active(self.preferences['show_gpu_load'])
        content.pack_start(self.gpu_load_check, False, False, 0)
        
        self.temp_check = Gtk.CheckButton("Show Temperature")
        self.temp_check.set_active(self.preferences['show_temperature'])
        content.pack_start(self.temp_check, False, False, 0)
        
        self.memory_check = Gtk.CheckButton("Show Memory Usage")
        self.memory_check.set_active(self.preferences['show_memory'])
        content.pack_start(self.memory_check, False, False, 0)
        
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Save preferences
            self.preferences['show_gpu_load'] = self.gpu_load_check.get_active()
            self.preferences['show_temperature'] = self.temp_check.get_active()
            self.preferences['show_memory'] = self.memory_check.get_active()
            self.save_preferences()
        
        dialog.destroy()

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