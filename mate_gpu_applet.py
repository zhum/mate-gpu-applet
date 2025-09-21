#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('MatePanelApplet', '4.0')

from gi.repository import Gtk, GObject, MatePanelApplet, GLib, Gio
import subprocess
import re
import json
import os
import cairo
import math
from collections import deque
import time

class GPUApplet:
    def __init__(self, applet):
        self.applet = applet
        self.config_file = os.path.expanduser("~/.config/mate-gpu-applet.json")
        
        # Load preferences
        self.preferences = {
            'show_gpu_load': True,
            'show_temperature': True,
            'show_memory': True,
            'show_chart': False,
            'chart_width': 50  # Width of each individual chart
        }
        self.load_preferences()
        
        # Data storage for charts (last 60 data points = 2 minutes)
        self.max_data_points = 60
        self.gpu_data = deque(maxlen=self.max_data_points)
        self.temp_data = deque(maxlen=self.max_data_points)
        self.memory_data = deque(maxlen=self.max_data_points)
        self.timestamps = deque(maxlen=self.max_data_points)
        
        self.chart_window = None
        
        # Create container for switching between label and drawing area
        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.applet.add(self.container)
        
        # Initialize display widgets
        self.label = Gtk.Label()
        self.label.set_text("GPU: --")
        
        # Individual chart drawing areas
        self.chart_areas = {}
        self.create_chart_areas()
        
        # Add appropriate widget based on preferences
        self.update_panel_display()
            
        self.applet.show_all()
        
        # Setup context menu
        self.setup_menu()
        
        self.update_gpu_info()
        GLib.timeout_add_seconds(2, self.update_gpu_info)
        
    def get_gpu_data(self):
        """Get raw GPU data and return as dict"""
        data = {'usage': None, 'temp': None, 'memory': None}
        
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    usage, mem_used, mem_total, temp = lines[0].split(', ')
                    data['usage'] = float(usage)
                    data['temp'] = float(temp)
                    data['memory'] = round((int(mem_used) / int(mem_total)) * 100)
                    return data
        except:
            pass
        
        try:
            result = subprocess.run(['radeontop', '-d', '-l1'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_match = re.search(r'gpu (\d+\.\d+)%', result.stdout)
                vram_match = re.search(r'vram (\d+\.\d+)%', result.stdout)
                if gpu_match:
                    data['usage'] = float(gpu_match.group(1))
                    if vram_match:
                        data['memory'] = float(vram_match.group(1))
                    return data
        except:
            pass
            
        return data
    
    def get_gpu_usage(self):
        """Get formatted GPU usage string"""
        data = self.get_gpu_data()
        return self.format_display(usage=data['usage'], temp=data['temp'], mem_percent=data['memory'])
    
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
        # Get raw data and store for charts
        data = self.get_gpu_data()
        current_time = time.time()
        
        self.timestamps.append(current_time)
        self.gpu_data.append(data['usage'])
        self.temp_data.append(data['temp'])
        self.memory_data.append(data['memory'])
        
        # Update chart window if open
        if self.chart_window and self.chart_window.get_visible():
            self.chart_drawing_area.queue_draw()
        
        # Update panel display based on mode
        if self.preferences['show_chart']:
            for area in self.chart_areas.values():
                area.queue_draw()
        else:
            gpu_info = self.format_display(usage=data['usage'], temp=data['temp'], mem_percent=data['memory'])
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
        
        chart_action = Gtk.Action("Chart", "Show Charts", "Show GPU performance charts", None)
        chart_action.connect("activate", self.show_chart)
        action_group.add_action(chart_action)
        
        preferences_action = Gtk.Action("Preferences", "Preferences", "Configure GPU monitor", None)
        preferences_action.connect("activate", self.show_preferences)
        action_group.add_action(preferences_action)
        
        menu_xml = '''
        <menuitem name="Chart" action="Chart" />
        <separator/>
        <menuitem name="Preferences" action="Preferences" />
        '''
        
        self.applet.setup_menu(menu_xml, action_group)
    
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
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content.pack_start(separator, False, False, 5)
        
        self.chart_view_check = Gtk.CheckButton("Show Charts in Panel (instead of text)")
        self.chart_view_check.set_active(self.preferences['show_chart'])
        content.pack_start(self.chart_view_check, False, False, 0)
        
        # Chart width control
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        width_label = Gtk.Label("Chart Width:")
        width_box.pack_start(width_label, False, False, 0)
        
        self.chart_width_spin = Gtk.SpinButton()
        self.chart_width_spin.set_range(30, 100)
        self.chart_width_spin.set_increments(5, 10)
        self.chart_width_spin.set_value(self.preferences['chart_width'])
        width_box.pack_start(self.chart_width_spin, False, False, 0)
        
        content.pack_start(width_box, False, False, 0)
        
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Save preferences
            old_chart_mode = self.preferences['show_chart']
            old_chart_width = self.preferences['chart_width']
            self.preferences['show_gpu_load'] = self.gpu_load_check.get_active()
            self.preferences['show_temperature'] = self.temp_check.get_active()
            self.preferences['show_memory'] = self.memory_check.get_active()
            self.preferences['show_chart'] = self.chart_view_check.get_active()
            self.preferences['chart_width'] = int(self.chart_width_spin.get_value())
            self.save_preferences()
            
            # Switch display mode if chart preference changed
            if old_chart_mode != self.preferences['show_chart']:
                self.switch_display_mode()
            # Update chart size if width changed
            elif self.preferences['show_chart'] and old_chart_width != self.preferences['chart_width']:
                self.update_chart_sizes()
        
        dialog.destroy()
    
    def show_chart(self, action):
        """Show chart window"""
        if self.chart_window:
            self.chart_window.present()
            return
            
        self.chart_window = Gtk.Window()
        self.chart_window.set_title("GPU Monitor Charts")
        self.chart_window.set_default_size(600, 400)
        self.chart_window.set_position(Gtk.WindowPosition.CENTER)
        
        # Create drawing area
        self.chart_drawing_area = Gtk.DrawingArea()
        self.chart_drawing_area.connect('draw', self.on_chart_draw)
        
        self.chart_window.add(self.chart_drawing_area)
        self.chart_window.connect('delete-event', self.on_chart_window_delete)
        self.chart_window.show_all()
    
    def on_chart_window_delete(self, window, event):
        """Handle chart window close"""
        window.hide()
        return True  # Don't destroy, just hide
    
    def on_chart_draw(self, widget, cr):
        """Draw the charts"""
        allocation = widget.get_allocation()
        width = allocation.width
        height = allocation.height
        
        # Clear background
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()
        
        if not self.timestamps or len(self.timestamps) < 2:
            # No data yet
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(16)
            text = "Collecting data..."
            text_extents = cr.text_extents(text)
            cr.move_to((width - text_extents.width) / 2, height / 2)
            cr.show_text(text)
            return
        
        # Chart area margins
        margin_left = 60
        margin_right = 20
        margin_top = 20
        margin_bottom = 40
        
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        # Draw enabled charts
        charts_to_draw = []
        if self.preferences['show_gpu_load']:
            charts_to_draw.append(('GPU Load (%)', self.gpu_data, (0.3, 0.7, 1.0), 100))
        if self.preferences['show_temperature']:
            charts_to_draw.append(('Temperature (°C)', self.temp_data, (1.0, 0.5, 0.2), 100))
        if self.preferences['show_memory']:
            charts_to_draw.append(('Memory (%)', self.memory_data, (0.2, 0.8, 0.2), 100))
        
        if not charts_to_draw:
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(16)
            text = "No charts enabled"
            text_extents = cr.text_extents(text)
            cr.move_to((width - text_extents.width) / 2, height / 2)
            cr.show_text(text)
            return
        
        # Draw grid
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.set_line_width(1)
        
        # Vertical grid lines
        for i in range(0, 11):
            x = margin_left + (chart_width * i / 10)
            cr.move_to(x, margin_top)
            cr.line_to(x, margin_top + chart_height)
            cr.stroke()
        
        # Horizontal grid lines
        for i in range(0, 6):
            y = margin_top + (chart_height * i / 5)
            cr.move_to(margin_left, y)
            cr.line_to(margin_left + chart_width, y)
            cr.stroke()
        
        # Draw Y-axis labels
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)
        
        for i in range(0, 6):
            value = 100 - (i * 20)
            y = margin_top + (chart_height * i / 5)
            cr.move_to(5, y + 4)
            cr.show_text(f"{value}")
        
        # Draw charts
        for name, data, color, max_val in charts_to_draw:
            if not any(d is not None for d in data):
                continue
                
            cr.set_source_rgb(*color)
            cr.set_line_width(2)
            
            valid_points = [(i, val) for i, val in enumerate(data) if val is not None]
            if len(valid_points) < 2:
                continue
            
            # Draw line
            first_point = True
            for i, value in valid_points:
                x = margin_left + (chart_width * i / (len(data) - 1))
                y = margin_top + chart_height - (chart_height * value / max_val)
                
                if first_point:
                    cr.move_to(x, y)
                    first_point = False
                else:
                    cr.line_to(x, y)
            
            cr.stroke()
        
        # Draw legend
        legend_y = margin_top + 10
        for i, (name, data, color, max_val) in enumerate(charts_to_draw):
            cr.set_source_rgb(*color)
            cr.rectangle(margin_left + 10, legend_y + i * 20, 15, 3)
            cr.fill()
            
            cr.set_source_rgb(1, 1, 1)
            cr.move_to(margin_left + 30, legend_y + i * 20 + 10)
            cr.show_text(name)
    
    def create_chart_areas(self):
        """Create individual drawing areas for each chart type"""
        chart_height = 24
        chart_width = self.preferences['chart_width']
        
        # GPU Load chart
        self.chart_areas['gpu'] = Gtk.DrawingArea()
        self.chart_areas['gpu'].set_size_request(chart_width, chart_height)
        self.chart_areas['gpu'].connect('draw', lambda w, cr: self.draw_individual_chart(w, cr, 'gpu'))
        
        # Temperature chart
        self.chart_areas['temp'] = Gtk.DrawingArea()
        self.chart_areas['temp'].set_size_request(chart_width, chart_height)
        self.chart_areas['temp'].connect('draw', lambda w, cr: self.draw_individual_chart(w, cr, 'temp'))
        
        # Memory chart
        self.chart_areas['memory'] = Gtk.DrawingArea()
        self.chart_areas['memory'].set_size_request(chart_width, chart_height)
        self.chart_areas['memory'].connect('draw', lambda w, cr: self.draw_individual_chart(w, cr, 'memory'))
    
    def draw_individual_chart(self, widget, cr, chart_type):
        """Draw individual chart for specific metric"""
        allocation = widget.get_allocation()
        width = allocation.width
        height = allocation.height
        
        # Chart configuration
        config = {
            'gpu': {'data': self.gpu_data, 'color': (0.3, 0.7, 1.0), 'label': 'GPU', 'enabled': self.preferences['show_gpu_load']},
            'temp': {'data': self.temp_data, 'color': (1.0, 0.5, 0.2), 'label': 'TEMP', 'enabled': self.preferences['show_temperature']},
            'memory': {'data': self.memory_data, 'color': (0.2, 0.8, 0.2), 'label': 'MEM', 'enabled': self.preferences['show_memory']}
        }
        
        chart_config = config[chart_type]
        
        # Clear background
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()
        
        # Draw border
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, width - 1, height - 1)
        cr.stroke()
        
        if not self.timestamps or len(self.timestamps) < 2:
            # No data yet - show loading
            cr.set_source_rgb(0.6, 0.6, 0.6)
            cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(10)
            text = chart_config['label']
            text_extents = cr.text_extents(text)
            cr.move_to((width - text_extents.width) / 2, height / 2 + 2)
            cr.show_text(text)
            return
        
        data = chart_config['data']
        color = chart_config['color']
        
        if not any(d is not None for d in data):
            # No valid data
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(10)
            text = "N/A"
            text_extents = cr.text_extents(text)
            cr.move_to((width - text_extents.width) / 2, height / 2 + 2)
            cr.show_text(text)
            return
        
        # Draw chart
        margin = 2
        chart_width = width - (margin * 2)
        chart_height = height - (margin * 2)
        
        cr.set_source_rgb(*color)
        cr.set_line_width(1.5)
        
        valid_points = [(i, val) for i, val in enumerate(data) if val is not None]
        if len(valid_points) >= 2:
            # Draw line chart
            first_point = True
            for i, value in valid_points:
                x = margin + (chart_width * i / (len(data) - 1))
                y = margin + chart_height - (chart_height * value / 100)
                
                if first_point:
                    cr.move_to(x, y)
                    first_point = False
                else:
                    cr.line_to(x, y)
            
            cr.stroke()
        
        # Draw current value
        current_value = data[-1] if data[-1] is not None else 0
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11)
        if chart_type == 'temp':
            text = f"{int(current_value)}°"
        else:
            text = f"{int(current_value)}%"
        text_extents = cr.text_extents(text)
        cr.move_to(width - text_extents.width - 2, height - 2)
        cr.show_text(text)
    
    def update_panel_display(self):
        """Update panel display based on preferences"""
        # Remove all children
        for child in self.container.get_children():
            self.container.remove(child)
        
        if self.preferences['show_chart']:
            # Add enabled charts
            if self.preferences['show_gpu_load']:
                self.container.pack_start(self.chart_areas['gpu'], False, False, 1)
            if self.preferences['show_temperature']:
                self.container.pack_start(self.chart_areas['temp'], False, False, 1)
            if self.preferences['show_memory']:
                self.container.pack_start(self.chart_areas['memory'], False, False, 1)
        else:
            self.container.add(self.label)
        
        self.container.show_all()
    
    def switch_display_mode(self):
        """Switch between text and chart display modes"""
        self.update_panel_display()
    
    def update_chart_sizes(self):
        """Update chart sizes when width preference changes"""
        chart_width = self.preferences['chart_width']
        for area in self.chart_areas.values():
            area.set_size_request(chart_width, 24)
        
        # Force redraw
        for area in self.chart_areas.values():
            area.queue_draw()

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