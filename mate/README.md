# Stock Applet

A comprehensive desktop panel applet that monitors stock prices with both text and graphical display modes. Features real-time price tracking, historical charts, and customizable display options. Available for both MATE and Cinnamon desktop environments.

## Features

- **Almost Real-time Stock Monitoring**: Live stock price updates with configurable intervals (Check https://finnhub.io for available limits!!!)
- **Dual Display Modes**: Switch between text display and graphical charts in panel
- **Historical Charts**: Mini-charts and detailed chart windows with price history
- **Comprehensive Tooltips**: Shows current price, daily range, and historical extremes with timestamps
- **Customizable Colors**: Line and fill colors for charts with color picker interface
- **Optional Symbol Display**: Show stock symbol on charts (configurable)
- **Dynamic Panel Sizing**: Charts automatically adapt to panel height
- **Persistent Data**: Price history stored locally for trend analysis
- **Secure API Integration**: Native HTTPS requests (no external dependencies)
- **Lightweight**: Minimal resource usage with efficient data management

## Requirements

### MATE Version
- MATE Desktop Environment
- Python 3
- PyGObject (python3-gi)
- Internet connection for stock data

### Cinnamon Version
- Cinnamon Desktop Environment
- Internet connection for stock data

### API Requirements (Both Versions)
- Finnhub API token (free at https://finnhub.io)

## Installation

### MATE Version

1. Install dependencies:

   ```bash
   sudo apt install python3-gi mate-panel-dev
   ```

2. Run the install script:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. Restart MATE panel:

   ```bash
   mate-panel --replace &
   ```

4. Add to panel:
   - Right-click on MATE panel
   - Select "Add to Panel..."
   - Find "Stock Applet" and add it

### Cinnamon Version

1. Copy applet to user directory:

   ```bash
   mkdir -p ~/.local/share/cinnamon/applets/
   cp -r cinnamon/stock-applet@cinnamon ~/.local/share/cinnamon/applets/
   ```

2. Restart Cinnamon:

   ```bash
   # Press Alt+F2, type 'r', press Enter
   # OR
   cinnamon --replace &
   ```

3. Add to panel:
   - Right-click on Cinnamon panel
   - Select "Applets"
   - Find "Stock Applet" in the Downloaded tab and click '+'

## Configuration

### API Setup

1. Get a free API token from https://finnhub.io
2. Open applet preferences
3. Enter your API token in the "API Token" field
4. Configure your preferred stock symbol (e.g., NVDA, AAPL, TSLA)

### Preferences

**MATE Version**: Right-click the applet and select "Preferences"

**Cinnamon Version**: Right-click the applet and select "Configure..." or use Cinnamon Settings > Applets

Available options:
- **API Token**: Your Finnhub API key (required)
- **Stock Symbol**: Symbol to monitor (e.g., NVDA, AAPL, TSLA)
- **Update Interval**: How often to fetch new data (1-60 minutes)
- **Display Options**: Show current price and/or daily range
- **Chart Mode**: Switch between text and chart display
- **Chart Appearance**: Width, transparency, font size
- **Chart Colors**: Customizable line and fill colors
- **Symbol on Chart**: Show stock symbol on charts

## Usage

### Text Display Mode

The applet shows stock information as text: `NVDA: $875.50 [860.25..890.75]`

### Chart Display Mode

Switch to chart mode for mini real-time graphs in the panel showing price trends.

### Tooltips

Hover over the applet for comprehensive information:
- Current stock symbol and price
- Today's trading range (high/low)
- Chart period extremes with timestamps
- Historical data from displayed timeframe

### Chart Windows

**MATE Version**: Right-click and select "Show Charts" for detailed charts with:
- Historical price trends
- Grid lines and value labels
- Customizable colors
- Stock symbol display (optional)

**Cinnamon Version**: Click the applet to show popup chart with price history

## Technical Details

### Data Storage
- Price history stored in `~/.local/share/cinnamon/applets/stock-applet@cinnamon/price_history.txt` (Cinnamon)
- Settings stored in `~/.config/stock-applet.json` (MATE)
- Keeps last 144 data points (24 hours at 10-minute intervals)

### Network
- Uses native HTTPS libraries (no curl dependency)
- Secure API communication with Finnhub
- 10-second timeout for reliability
- Graceful error handling

### Performance
- Lightweight memory footprint
- Efficient data structures with automatic cleanup
- Responsive UI with non-blocking updates
- Dynamic sizing based on panel configuration

## Development

### MATE Version
To test without installing:

```bash
python3 stock_applet.py
```

### Cinnamon Version
To test during development:

1. Copy to development location:
   ```bash
   mkdir -p ~/.local/share/cinnamon/applets/stock-applet@cinnamon
   cp cinnamon/stock-applet@cinnamon/* ~/.local/share/cinnamon/applets/stock-applet@cinnamon/
   ```

2. Restart Cinnamon and add through Applets menu

## Files

### MATE Version
- `stock_applet.py` - Main applet code
- `org.mate.panel.StockApplet.mate-panel-applet` - MATE applet configuration
- `org.mate.panel.applet.StockAppletFactory.service` - D-Bus service file
- `stock-applet.desktop` - Desktop entry
- `install.sh` - Installation script

### Cinnamon Version
- `cinnamon/stock-applet@cinnamon/applet.js` - Main applet code
- `cinnamon/stock-applet@cinnamon/metadata.json` - Applet metadata
- `cinnamon/stock-applet@cinnamon/settings-schema.json` - Settings configuration

## Troubleshooting

### No Data Showing
- Verify API token is correctly entered
- Check internet connection
- Ensure stock symbol is valid (use common symbols like AAPL, NVDA)
- Check applet logs for error messages

### Charts Not Displaying
- Ensure "Show Charts in Panel" is enabled in preferences
- Check that panel has sufficient height for chart display
- Verify chart width settings are appropriate

### Performance Issues
- Increase update interval if network is slow
- Reduce chart history if using limited storage

## License

Apache-2.0 License