"""
QR2Key - A utility that converts QR-code data arriving on a USB virtual COM port into immediate keyboard strokes.

This script implements the following functionality:
- Auto-detection of QR reader's CH340 port with user override
- Buffering of byte stream until EOL or 50ms idle
- Decoding of Shift_JIS to Unicode
- Platform-specific output (macOS console vs Windows keystrokes)
- Robust reconnect on cable unplug
- Minimal logging to stdout

MIT License

Copyright (c) 2025 Suguru Hirayama

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import serial
import serial.tools.list_ports
from loguru import logger

if platform.system() == "Windows":
    try:
        import win32api
        import win32con
        import win32gui
        WINDOWS_NATIVE_API = True
    except ImportError:
        WINDOWS_NATIVE_API = False
        import keyboard  # Fallback for Windows

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>")

class SerialBuffer:
    """Buffer for serial data that accumulates until EOL or timeout."""
    
    def __init__(self, idle_timeout_ms: int = 50):
        """
        Initialize the serial buffer.
        
        Args:
            idle_timeout_ms: Timeout in milliseconds to consider the buffer complete if no new data arrives
        """
        self.buffer = bytearray()
        self.last_data_time = 0
        self.idle_timeout_ms = idle_timeout_ms
    
    def add_data(self, data: bytes) -> None:
        """
        Add data to the buffer.
        
        Args:
            data: Bytes to add to the buffer
        """
        self.buffer.extend(data)
        self.last_data_time = time.time() * 1000  # Convert to milliseconds
    
    def is_complete(self) -> bool:
        """
        Check if the buffer is complete (contains EOL or idle timeout reached).
        
        Returns:
            True if buffer is complete, False otherwise
        """
        if b'\r' in self.buffer or b'\n' in self.buffer:
            return True
        
        current_time = time.time() * 1000  # Convert to milliseconds
        return (current_time - self.last_data_time) >= self.idle_timeout_ms and len(self.buffer) > 0
    
    def get_data(self) -> bytes:
        """
        Get the buffered data and clear the buffer.
        
        Returns:
            Buffered data as bytes
        """
        data = bytes(self.buffer)
        self.buffer.clear()
        return data
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()


class QR2Key:
    """Main class for QR2Key application."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize QR2Key.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.serial_port = None
        self.buffer = SerialBuffer(idle_timeout_ms=self.config.get("buffer_ms", 50))
        self.running = False
        self.reconnect_delay = 1.0  # Initial reconnect delay in seconds
        self.max_reconnect_delay = 5.0  # Maximum reconnect delay in seconds
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration as a dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return {
                "port": None,  # Auto-detect
                "baud": 9600,
                "buffer_ms": 50,
                "ime_off": True
            }
    
    def _detect_ch340_port(self) -> Optional[str]:
        """
        Auto-detect CH340 USB-to-Serial port.
        
        Returns:
            Port name if found, None otherwise
        """
        logger.info("Detecting CH340 port...")
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            if "CH340" in port.description or any("CH340" in hwid for hwid in port.hwid.split()):
                logger.info(f"Found CH340 port: {port.device}")
                return port.device
        
        logger.warning("No CH340 port found")
        return None
    
    def _open_serial_port(self) -> bool:
        """
        Open the serial port.
        
        Returns:
            True if successful, False otherwise
        """
        port = self.config.get("port")
        if port is None:
            port = self._detect_ch340_port()
            if port is None:
                return False
        
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.config.get("baud", 9600),
                timeout=0.1  # Non-blocking read
            )
            logger.info(f"Connected to {port} at {self.config.get('baud', 9600)} baud")
            self.reconnect_delay = 1.0  # Reset reconnect delay on successful connection
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {port}: {e}")
            return False
    
    def _close_serial_port(self) -> None:
        """Close the serial port if open."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            logger.info("Serial port closed")
    
    def _decode_shift_jis(self, data: bytes) -> str:
        """
        Decode Shift_JIS encoded bytes to Unicode string.
        
        Args:
            data: Shift_JIS encoded bytes
            
        Returns:
            Decoded Unicode string
        """
        try:
            return data.decode('shift_jis').strip()
        except UnicodeDecodeError:
            logger.warning("Failed to decode as Shift_JIS, trying UTF-8")
            try:
                return data.decode('utf-8').strip()
            except UnicodeDecodeError:
                logger.error("Failed to decode as UTF-8, using replacement characters")
                return data.decode('shift_jis', errors='replace').strip()
    
    def _process_data(self, data: bytes) -> None:
        """
        Process the received data.
        
        Args:
            data: Data received from the serial port
        """
        if not data:
            return
        
        decoded_text = self._decode_shift_jis(data)
        if not decoded_text:
            return
        
        logger.info(f"Decoded: {decoded_text}")
        
        if platform.system() == "Windows":
            self._send_windows_keystrokes(decoded_text)
        else:
            print(f"QR Data: {decoded_text}")
    
    def _send_windows_keystrokes(self, text: str) -> None:
        """
        Send keystrokes on Windows.
        
        Args:
            text: Text to send as keystrokes
        """
        if not platform.system() == "Windows":
            return
        
        if self.config.get("ime_off", True):
            self._disable_ime()
        
        if WINDOWS_NATIVE_API:
            self._send_windows_native_keystrokes(text)
        else:
            keyboard.write(text)
            logger.info("Sent keystrokes using keyboard module")
    
    def _disable_ime(self) -> None:
        """Disable IME on Windows."""
        if not platform.system() == "Windows":
            return
        
        if WINDOWS_NATIVE_API:
            try:
                hwnd = win32gui.GetForegroundWindow()
                
                result = win32api.SendMessage(hwnd, win32con.WM_IME_CONTROL, 0x0006, 0)
                logger.debug(f"IME disable result: {result}")
            except Exception as e:
                logger.error(f"Failed to disable IME: {e}")
    
    def _send_windows_native_keystrokes(self, text: str) -> None:
        """
        Send keystrokes using Windows native API.
        
        Args:
            text: Text to send as keystrokes
        """
        if not WINDOWS_NATIVE_API:
            return
        
        try:
            
            hwnd = win32gui.GetForegroundWindow()
            for char in text:
                win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
            
            logger.info("Sent keystrokes using Windows native API")
        except Exception as e:
            logger.error(f"Failed to send keystrokes: {e}")
            if 'keyboard' in sys.modules:
                keyboard.write(text)
                logger.info("Sent keystrokes using keyboard module (fallback)")
    
    def start(self) -> None:
        """Start the QR2Key service."""
        self.running = True
        logger.info("Starting QR2Key service")
        
        while self.running:
            if not self.serial_port or not self.serial_port.is_open:
                if not self._open_serial_port():
                    logger.info(f"Retrying connection in {self.reconnect_delay:.1f} seconds...")
                    time.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 1.5, self.max_reconnect_delay)
                    continue
            
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.buffer.add_data(data)
                
                if self.buffer.is_complete():
                    self._process_data(self.buffer.get_data())
                
                time.sleep(0.01)
                
            except serial.SerialException as e:
                logger.error(f"Serial port error: {e}")
                self._close_serial_port()
                self.buffer.clear()
            
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                self.stop()
            
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
        
        self._close_serial_port()
    
    def stop(self) -> None:
        """Stop the QR2Key service."""
        self.running = False
        logger.info("Stopping QR2Key service")


def main():
    """Main entry point for QR2Key."""
    config_path = "config.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    qr2key = QR2Key(config_path)
    
    try:
        qr2key.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        qr2key.stop()


if __name__ == "__main__":
    main()
