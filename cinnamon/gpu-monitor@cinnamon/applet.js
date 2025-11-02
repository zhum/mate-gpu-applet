const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const St = imports.gi.St;
const GLib = imports.gi.GLib;
const Util = imports.misc.util;
const Lang = imports.lang;
const Settings = imports.ui.settings;
const Mainloop = imports.mainloop;
const Cairo = imports.cairo;
const Clutter = imports.gi.Clutter;

function MyApplet(orientation, panel_height, instance_id) {
    this._init(orientation, panel_height, instance_id);
}

MyApplet.prototype = {
    __proto__: Applet.TextIconApplet.prototype,

    _init: function(orientation, panel_height, instance_id) {
        Applet.TextIconApplet.prototype._init.call(this, orientation, panel_height, instance_id);

        try {
            this.set_applet_icon_symbolic_name("utilities-system-monitor");
            this.set_applet_tooltip(_("GPU Monitor"));

            // Initialize settings
            this.settings = new Settings.AppletSettings(this, "gpu-monitor@cinnamon", instance_id);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "show-gpu-load", "showGpuLoad", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "show-temperature", "showTemperature", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "show-memory", "showMemory", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "show-chart", "showChart", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "chart-width", "chartWidth", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "chart-transparency", "chartTransparency", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "background-transparency", "backgroundTransparency", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "chart-font-size", "chartFontSize", this.on_settings_changed, null);
            this.settings.bindProperty(Settings.BindingDirection.BIDIRECTIONAL,
                                     "enable-logging", "enableLogging", this.on_settings_changed, null);

            // Data storage for charts (last 60 data points = 2 minutes)
            this.maxDataPoints = 60;
            this.gpuData = [];
            this.tempData = [];
            this.memoryData = [];
            this.timestamps = [];

            // Initialize chart container
            this.chartContainer = new St.BoxLayout({ style_class: 'gpu-charts' });
            this.chartAreas = {};
            this.createChartAreas();

            // Initialize display
            this.set_applet_label("GPU: --");

            // Setup context menu
            this.menuManager = new PopupMenu.PopupMenuManager(this);
            this.menu = new Applet.AppletPopupMenu(this, orientation);
            this.menuManager.addMenu(this.menu);

            this._contentSection = new PopupMenu.PopupMenuSection();
            this.menu.addMenuItem(this._contentSection);

            // Add preferences menu item
            let prefsItem = new PopupMenu.PopupMenuItem(_("Preferences"));
            prefsItem.connect('activate', Lang.bind(this, this.openPreferences));
            this.menu.addMenuItem(prefsItem);

            // Add chart window menu item
            let chartItem = new PopupMenu.PopupMenuItem(_("Show Charts"));
            chartItem.connect('activate', Lang.bind(this, this.showChartWindow));
            this.menu.addMenuItem(chartItem);

            // Start monitoring
            this.timeout = Mainloop.timeout_add_seconds(2, Lang.bind(this, this.updateGpuInfo));
            this.updateGpuInfo();

        } catch (e) {
            global.logError(e);
        }
    },

    on_applet_clicked: function() {
        this.menu.toggle();
    },

    log: function(message) {
        if (this.enableLogging) {
            global.log("GPU Monitor: " + message);
        }
    },

    on_settings_changed: function() {
        // Update chart sizes if width changed
        if (this.chartWidth) {
            for (let chart in this.chartAreas) {
                this.chartAreas[chart].set_width(this.chartWidth);
            }
        }

        this.updateDisplay();

        // Force updates based on current mode
        if (this.showChart) {
            // Force chart repaints when in chart mode to apply new settings
            for (let chart in this.chartAreas) {
                this.chartAreas[chart].queue_repaint();
            }
        } else {
            // Ensure text mode is properly displayed when switching from chart mode
            this.updateDisplay();
        }
    },

    openPreferences: function() {
        Util.spawn(['cinnamon-settings', 'applets', 'gpu-monitor@cinnamon']);
    },

    showChartWindow: function() {
        // For now, just show a notification - chart window would need more complex implementation
        this.log("Chart window feature not yet implemented in Cinnamon version");
    },

    getGpuInfo: function() {
        try {
            // Try NVIDIA first
            let [success, stdout] = GLib.spawn_command_line_sync('nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total --format=csv,noheader,nounits');

            if (success && stdout) {
                let output = stdout.toString().trim();
                if (output && !output.includes('not found') && !output.includes('command not found')) {
                    let parts = output.split(',');
                    if (parts.length >= 4) {
                        let gpuLoad = parseInt(parts[0].trim());
                        let temp = parseInt(parts[1].trim());
                        let memUsed = parseInt(parts[2].trim());
                        let memTotal = parseInt(parts[3].trim());
                        let memPercent = Math.round((memUsed / memTotal) * 100);

                        return {
                            gpuLoad: isNaN(gpuLoad) ? null : gpuLoad,
                            temperature: isNaN(temp) ? null : temp,
                            memoryPercent: isNaN(memPercent) ? null : memPercent,
                            vendor: 'NVIDIA'
                        };
                    }
                }
            }

            // Try AMD with radeontop
            [success, stdout] = GLib.spawn_command_line_sync('timeout 3 radeontop -d - -l 1');

            if (success && stdout) {
                let output = stdout.toString();
                let gpuMatch = output.match(/gpu\s+(\d+\.\d+)%/);
                let tempMatch = output.match(/(\d+\.\d+)C/);
                let vramMatch = output.match(/vram\s+(\d+\.\d+)%/);

                if (gpuMatch || tempMatch || vramMatch) {
                    return {
                        gpuLoad: gpuMatch ? Math.round(parseFloat(gpuMatch[1])) : null,
                        temperature: tempMatch ? Math.round(parseFloat(tempMatch[1])) : null,
                        memoryPercent: vramMatch ? Math.round(parseFloat(vramMatch[1])) : null,
                        vendor: 'AMD'
                    };
                }
            }

            return {
                gpuLoad: null,
                temperature: null,
                memoryPercent: null,
                vendor: 'Unknown'
            };

        } catch (e) {
            global.logError("Error getting GPU info: " + e);
            return {
                gpuLoad: null,
                temperature: null,
                memoryPercent: null,
                vendor: 'Error'
            };
        }
    },

    updateGpuInfo: function() {
        let info = this.getGpuInfo();

        // Store data for charts
        let now = new Date().getTime();
        this.timestamps.push(now);
        this.gpuData.push(info.gpuLoad);
        this.tempData.push(info.temperature);
        this.memoryData.push(info.memoryPercent);

        // Keep only last maxDataPoints
        if (this.timestamps.length > this.maxDataPoints) {
            this.timestamps.shift();
            this.gpuData.shift();
            this.tempData.shift();
            this.memoryData.shift();
        }

        this.updateDisplay(info);

        // Update charts if in chart mode
        if (this.showChart) {
            for (let chart in this.chartAreas) {
                this.chartAreas[chart].queue_repaint();
            }
        }

        return true; // Continue the timer
    },

    updateDisplay: function(info) {
        if (!info) {
            // Get latest info if not provided
            info = this.getGpuInfo();
        }

        this.log("updateDisplay called, showChart=" + this.showChart);

        if (this.showChart) {
            // Chart mode - hide text label and icon, show charts
            this.log("Switching to chart mode");
            this.hide_applet_icon();
            this.updateChartDisplay();
        } else {
            // Text mode - remove chart container, hide icon, show text label
            this.log("Switching to text mode");

            // Remove chart container if it exists
            if (this.chartContainer && this.chartContainer.get_parent()) {
                this.actor.remove_child(this.chartContainer);
                this.log("Removed chart container");
            }

            // Hide icon and show the text label
            this.hide_applet_icon();
            this.hide_applet_label(false);

            let displayParts = [];

            if (this.showGpuLoad && info.gpuLoad !== null) {
                displayParts.push("G: " + info.gpuLoad + "%");
            }

            if (this.showTemperature && info.temperature !== null) {
                displayParts.push("T: " + info.temperature + "°C");
            }

            if (this.showMemory && info.memoryPercent !== null) {
                displayParts.push("M: " + info.memoryPercent + "%");
            }

            let text = displayParts.length > 0 ? displayParts.join(" | ") : "GPU: --";
            this.log("Setting text: " + text);
            this.set_applet_label(text);
        }

        // Update tooltip
        let tooltip = "GPU Monitor\n";
        if (info.vendor !== 'Unknown' && info.vendor !== 'Error') {
            tooltip += "Vendor: " + info.vendor + "\n";
        }
        if (info.gpuLoad !== null) {
            tooltip += "GPU Load: " + info.gpuLoad + "%\n";
        }
        if (info.temperature !== null) {
            tooltip += "Temperature: " + info.temperature + "°C\n";
        }
        if (info.memoryPercent !== null) {
            tooltip += "Memory: " + info.memoryPercent + "%";
        }
        this.set_applet_tooltip(tooltip);
    },

    createChartAreas: function() {
        // Create individual chart drawing areas
        this.chartAreas.gpu = new St.DrawingArea({ style_class: 'gpu-chart' });
        this.chartAreas.temp = new St.DrawingArea({ style_class: 'temp-chart' });
        this.chartAreas.memory = new St.DrawingArea({ style_class: 'memory-chart' });

        // Set initial size
        let chartWidth = this.chartWidth || 50;
        let chartHeight = 24; // Panel height

        for (let chart in this.chartAreas) {
            this.chartAreas[chart].set_width(chartWidth);
            this.chartAreas[chart].set_height(chartHeight);
            this.chartAreas[chart].connect('repaint', Lang.bind(this, function(area) {
                this.drawChart(area, chart);
            }));
        }
    },

    updateChartDisplay: function() {
        // Hide text label and add charts
        this.hide_applet_label(true);

        // Add enabled charts to the container
        this.chartContainer.remove_all_children();

        if (this.showGpuLoad) {
            this.chartContainer.add_child(this.chartAreas.gpu);
        }
        if (this.showTemperature) {
            this.chartContainer.add_child(this.chartAreas.temp);
        }
        if (this.showMemory) {
            this.chartContainer.add_child(this.chartAreas.memory);
        }

        this.actor.add_child(this.chartContainer);

        // Trigger repaints
        for (let chart in this.chartAreas) {
            this.chartAreas[chart].queue_repaint();
        }
    },

    drawChart: function(area, chartType) {
        let [width, height] = area.get_surface_size();
        let cr = area.get_context();

        // Chart configuration
        let config = {
            'gpu': { data: this.gpuData, color: [0.3, 0.7, 1.0], label: 'g' },
            'temp': { data: this.tempData, color: [1.0, 0.5, 0.2], label: 't' },
            'memory': { data: this.memoryData, color: [0.2, 0.8, 0.2], label: 'm' }
        };

        let chartConfig = config[chartType];
        if (!chartConfig) return;

        // Clear background
        cr.setOperator(Cairo.Operator.CLEAR);
        cr.paint();
        cr.setOperator(Cairo.Operator.OVER);

        // Draw semi-transparent background
        let bgTransparency = (this.backgroundTransparency || 80) / 100.0;
        cr.setSourceRGBA(0.5, 0.5, 0.5, bgTransparency);
        cr.paint();

        // Draw border
        cr.setSourceRGB(0.3, 0.3, 0.3);
        cr.setLineWidth(1);
        cr.rectangle(0.5, 0.5, width - 1, height - 1);
        cr.stroke();

        if (!this.timestamps || this.timestamps.length < 2) {
            // No data yet
            cr.setSourceRGB(0.6, 0.6, 0.6);
            cr.selectFontFace("Arial", Cairo.FontSlant.NORMAL, Cairo.FontWeight.NORMAL);
            cr.setFontSize(10);
            let text = chartConfig.label;
            let textExtents = cr.textExtents(text);
            cr.moveTo((width - textExtents.width) / 2, height / 2 + 2);
            cr.showText(text);
            return;
        }

        let data = chartConfig.data;
        let color = chartConfig.color;

        if (!data || data.length === 0) {
            // No valid data
            cr.setSourceRGB(0.5, 0.5, 0.5);
            cr.selectFontFace("Arial", Cairo.FontSlant.NORMAL, Cairo.FontWeight.NORMAL);
            cr.setFontSize(10);
            let text = "N/A";
            let textExtents = cr.textExtents(text);
            cr.moveTo((width - textExtents.width) / 2, height / 2 + 2);
            cr.showText(text);
            return;
        }

        // Draw chart
        let margin = 2;
        let chartWidth = width - (margin * 2);
        let chartHeight = height - (margin * 2);

        // Calculate transparency alpha value (0-1)
        let transparency = (this.chartTransparency || 50) / 100.0;

        // Draw filled area
        cr.setSourceRGBA(color[0], color[1], color[2], transparency);
        let firstPoint = true;
        for (let i = 0; i < data.length; i++) {
            let value = data[i];
            if (value !== null && value !== undefined) {
                let x = margin + (chartWidth * i / (data.length - 1));
                let y = margin + chartHeight - (chartHeight * value / 100);

                if (firstPoint) {
                    cr.moveTo(x, y);
                    firstPoint = false;
                } else {
                    cr.lineTo(x, y);
                }
            }
        }

        // Close the path
        if (!firstPoint) {
            let lastX = margin + chartWidth;
            let firstX = margin;
            cr.lineTo(lastX, margin + chartHeight);
            cr.lineTo(firstX, margin + chartHeight);
            cr.closePath();
            cr.fill();
        }

        // Draw line border
        cr.setSourceRGB(color[0], color[1], color[2]);
        cr.setLineWidth(1.5);
        firstPoint = true;
        for (let i = 0; i < data.length; i++) {
            let value = data[i];
            if (value !== null && value !== undefined) {
                let x = margin + (chartWidth * i / (data.length - 1));
                let y = margin + chartHeight - (chartHeight * value / 100);

                if (firstPoint) {
                    cr.moveTo(x, y);
                    firstPoint = false;
                } else {
                    cr.lineTo(x, y);
                }
            }
        }
        cr.stroke();

        // Draw current value
        let currentValue = data[data.length - 1];
        if (currentValue !== null && currentValue !== undefined) {
            cr.setSourceRGB(1, 1, 1);
            cr.selectFontFace("Arial", Cairo.FontSlant.NORMAL, Cairo.FontWeight.BOLD);
            cr.setFontSize(this.chartFontSize || 10);

            let text;
            if (chartType === 'temp') {
                text = chartConfig.label + ":" + Math.round(currentValue) + "°";
            } else {
                text = chartConfig.label + ":" + Math.round(currentValue) + "%";
            }

            cr.moveTo(3, (this.chartFontSize || 10) + 2);
            cr.showText(text);
        }
    },

    parseColor: function(colorString) {
        // Parse rgba color string like "rgba(51, 204, 51, 1.0)"
        let match = colorString.match(/rgba?\(([^)]+)\)/);
        if (match) {
            let values = match[1].split(',').map(v => parseFloat(v.trim()));
            if (values.length >= 3) {
                return {
                    r: values[0] / 255,
                    g: values[1] / 255,
                    b: values[2] / 255,
                    a: values.length > 3 ? values[3] : 1.0
                };
            }
        }
        // Fallback for hex colors or invalid input
        return { r: 1.0, g: 1.0, b: 1.0, a: 1.0 };
    },

    on_applet_removed_from_panel: function() {
        if (this.timeout) {
            Mainloop.source_remove(this.timeout);
        }
    }
};

function main(metadata, orientation, panel_height, instance_id) {
    return new MyApplet(orientation, panel_height, instance_id);
}