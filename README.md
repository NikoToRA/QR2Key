# QR2Key

QR2Key is a cross-platform utility that converts QR-code data arriving on a USB virtual COM port into immediate keyboard strokes.

## Overview

QR2Key automatically detects QR readers connected via CH340 USB-to-Serial adapters, buffers incoming data, and:
- On macOS: Displays the decoded text in the console
- On Windows: Injects the decoded text as keyboard input (with IME disabled)

This tool is designed for offline use in environments where direct keyboard input is needed from QR code scans.

## Features

- Auto-detection of QR reader's CH340 port with user override
- Buffering of byte stream until EOL or 50ms idle
- Decoding of Shift_JIS to Unicode
- Platform-specific output handling
- Robust reconnect on cable unplug
- Minimal logging to stdout

## Requirements

- Python 3.11 or higher
- Required Python packages:
  - pyserial
  - loguru
  - pywin32 (Windows only)
  - keyboard (Windows fallback)

## Installation

### Clone the repository

```bash
git clone https://github.com/NikoToRA/QR2Key.git
cd QR2Key
```

### Install dependencies

```bash
# macOS
pip install pyserial loguru

# Windows
pip install pyserial loguru pywin32 keyboard
```

## Configuration

QR2Key uses a `config.json` file in the root directory with the following settings:

```json
{
    "port": null,
    "baud": 9600,
    "buffer_ms": 50,
    "ime_off": true
}
```

- `port`: Serial port to use (null for auto-detection)
- `baud`: Baud rate for serial communication
- `buffer_ms`: Idle timeout in milliseconds to consider a buffer complete
- `ime_off`: Whether to disable IME on Windows before sending keystrokes

## Usage

Run the script directly:

```bash
python src/qr2key.py
```

Or with a custom config file:

```bash
python src/qr2key.py path/to/config.json
```

## Testing on macOS

1. Connect your QR code reader device to your Mac
2. Install dependencies:
   ```bash
   pip install pyserial loguru
   ```
3. Run the script:
   ```bash
   python src/qr2key.py
   ```
4. The script will auto-detect the CH340 port or you can specify it in the config.json
5. Scan a QR code and the decoded text will be displayed in the console
6. To exit, press Ctrl+C

## Building for Windows

### Local Build (on Windows)

1. Install Python 3.11 and required packages:
   ```bash
   pip install pyserial loguru pywin32 keyboard pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller --onefile --name QR2Key src/qr2key.py
   ```
3. The executable will be in the `dist` folder

### Cross-Platform Build (via GitHub Actions)

QR2Key includes a GitHub Actions workflow that automatically builds Windows executables:

1. Push your changes to GitHub
2. The workflow will:
   - Use a Windows 2022 runner
   - Install Python 3.11 and dependencies
   - Build both x86 and x64 executables using PyInstaller
   - Upload the executables as artifacts

To download the built executables:
1. Go to the GitHub repository
2. Navigate to Actions tab
3. Select the latest workflow run
4. Download the artifacts from the workflow summary

## Windows Usage

1. Download the appropriate executable (x86 or x64) for your system
2. Place the executable and config.json in the same directory
3. Run the executable
4. Connect your QR code reader
5. The application will auto-detect the reader and inject scanned QR codes as keyboard input

## Troubleshooting

### Port Detection Issues

If the CH340 port is not automatically detected:

1. Check that the device is properly connected
2. Manually specify the port in config.json:
   ```json
   {
       "port": "COM3",  // On Windows
       "port": "/dev/tty.wchusbserial1420",  // On macOS
       "baud": 9600,
       "buffer_ms": 50,
       "ime_off": true
   }
   ```

### Windows Keyboard Input Issues

If keyboard input is not working on Windows:

1. Ensure you have administrator privileges
2. Try running the application as administrator
3. If using the native API fails, the application will fall back to the keyboard module

## License

This project is licensed under the MIT License - see the LICENSE file for details.
