"""
QR2Key Runner Script
This script runs the QR2Key application directly without needing to build an executable.
For use in Windows environments like UTM.
"""

import sys
import os
import platform

if platform.system() != 'Windows':
    print("This application is designed to run on Windows.")
    print(f"Current platform: {platform.system()}")
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

try:
    import qrcode
    from PIL import Image
    from cryptography.fernet import Fernet
    import win32clipboard
    import win32con
    print("All dependencies are installed.")
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("\nPlease install the required dependencies:")
    print("pip install -r requirements.txt")
    print("pip install -r requirements-win.txt")
    sys.exit(1)

try:
    from qr2key.main import main
    sys.exit(main())
except Exception as e:
    print(f"Error running QR2Key: {e}")
    sys.exit(1)
