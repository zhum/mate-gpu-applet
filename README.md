# Stock Applet

A comprehensive desktop panel applet for real-time stock price monitoring with customizable charts and displays. Available for both MATE and Cinnamon desktop environments.

![Stock Applet Screenshot](https://via.placeholder.com/800x200/2c3e50/ffffff?text=Stock+Applet+-+Real-time+Stock+Monitoring)

## 🚀 Features

- **📈 Real-time Stock Tracking**: Live price updates with configurable intervals (1-60 minutes)
- **🎨 Dual Display Modes**: Text display or interactive charts in your panel
- **📊 Historical Charts**: Mini-charts and detailed windows with price history
- **💡 Smart Tooltips**: Current price, daily range, and historical extremes with timestamps
- **🎨 Customizable Appearance**: Chart colors, transparency, and symbol display
- **📱 Dynamic Panel Integration**: Charts adapt to panel height automatically
- **💾 Persistent Data**: Local price history storage for trend analysis
- **🔐 Secure API**: Native HTTPS requests with Finnhub integration
- **⚡ Lightweight**: Minimal resource usage with efficient data management

## 🖥️ Desktop Support

### MATE Desktop Environment
- Full-featured implementation with preferences dialog
- Chart window with detailed analysis
- Dynamic panel sizing
- Comprehensive tooltips

### Cinnamon Desktop Environment
- Modern settings interface
- Popup chart display
- Color customization
- Real-time updates

## 📋 Requirements

- **MATE**: Python 3, PyGObject, MATE Panel
- **Cinnamon**: Cinnamon Desktop Environment
- **API**: Free Finnhub API token ([get yours here](https://finnhub.io))
- **Network**: Internet connection for stock data

## 🛠️ Installation

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/user/stocks-applet.git
   cd stocks-applet
   ```

2. **For MATE:**
   ```bash
   cd mate
   chmod +x install.sh
   ./install.sh
   mate-panel --replace &
   ```

3. **For Cinnamon:**
   ```bash
   cp -r cinnamon/stock-applet@cinnamon ~/.local/share/cinnamon/applets/
   # Restart Cinnamon (Alt+F2, type 'r', Enter)
   ```

4. **Add to panel:**
   - Right-click panel → "Add to Panel" → "Stock Applet"

### API Configuration

1. Get free API token at [Finnhub.io](https://finnhub.io)
2. Right-click applet → "Preferences"
3. Enter API token and stock symbol (e.g., NVDA, AAPL, TSLA)

## 📖 Usage

### Text Mode
```
NVDA: $875.50 [860.25..890.75]
```

### Chart Mode
- Mini real-time graphs in panel
- Historical price trends
- Customizable colors and transparency

### Tooltips
Hover for comprehensive information:
- Current symbol and price
- Today's trading range
- Historical extremes with timestamps

## ⚙️ Configuration Options

| Feature | Description | Options |
|---------|-------------|---------|
| **API Token** | Finnhub API key | Required for data |
| **Stock Symbol** | Symbol to monitor | NVDA, AAPL, TSLA, etc. |
| **Update Interval** | Data refresh rate | 1-60 minutes |
| **Display Mode** | Panel appearance | Text or Charts |
| **Chart Colors** | Line and fill colors | Color picker interface |
| **Symbol Display** | Show symbol on chart | On/Off |
| **Chart Size** | Panel integration | Auto-adapts to panel height |

## 🔧 Technical Details

### Architecture
- **MATE**: Python 3 + GTK + Cairo graphics
- **Cinnamon**: JavaScript + GJS + Soup HTTP

### Data Management
- Local price history (144 points = 24 hours)
- Automatic cleanup and rotation
- Efficient memory usage

### Network
- Native HTTPS libraries (no curl dependency)
- 10-second timeout for reliability
- Graceful error handling
- Secure API communication

### Performance
- Lightweight memory footprint
- Non-blocking UI updates
- Dynamic panel sizing
- Efficient data structures

## 🗂️ Project Structure

```
stocks-applet/
├── mate/                           # MATE Desktop version
│   ├── stock_applet.py            # Main applet code
│   ├── install.sh                 # Installation script
│   ├── README.md                  # MATE-specific documentation
│   └── *.mate-panel-applet       # MATE configuration files
├── cinnamon/                      # Cinnamon Desktop version
│   └── stock-applet@cinnamon/
│       ├── applet.js              # Main applet code
│       ├── metadata.json          # Applet metadata
│       └── settings-schema.json   # Settings configuration
└── README.md                      # This file
```

## 🚨 Troubleshooting

### No Data Displaying
- ✅ Verify API token is entered correctly
- ✅ Check internet connection
- ✅ Use valid stock symbols (AAPL, NVDA, MSFT)
- ✅ Check error messages in system logs

### Charts Not Showing
- ✅ Enable "Show Charts in Panel" in preferences
- ✅ Ensure panel height is sufficient (>16px)
- ✅ Verify chart width settings

### Performance Issues
- ✅ Increase update interval for slower networks
- ✅ Check system resources
- ✅ Restart panel if needed

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Finnhub.io](https://finnhub.io) for free stock market API
- MATE and Cinnamon desktop teams for excellent frameworks
- Community contributors and testers

---

**Made with ❤️ for Linux Desktop Users**