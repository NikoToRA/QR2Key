"""Main module for QR2Key application."""

import sys
import os
import platform
import qrcode
from PIL import Image
from cryptography.fernet import Fernet

if platform.system() == 'Windows':
    try:
        import win32clipboard
        import win32con
        WIN32_AVAILABLE = True
    except ImportError:
        print("Warning: pywin32 is not installed. Some features will be disabled.")
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False


def generate_key():
    """Generate a new cryptographic key."""
    return Fernet.generate_key()


def key_to_qr(key, output_path='key_qr.png'):
    """Convert a cryptographic key to a QR code image.
    
    Args:
        key: The cryptographic key as bytes
        output_path: Path to save the QR code image
        
    Returns:
        The path to the saved QR code image
    """
    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(key_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path


def copy_to_clipboard(text):
    """Copy text to clipboard.
    
    On Windows, uses pywin32. On other platforms, prints a message.
    
    Args:
        text: The text to copy to clipboard
    """
    if WIN32_AVAILABLE:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        print("Text copied to clipboard.")
    else:
        print("Clipboard functionality is only available on Windows.")
        print(f"Text to copy: {text}")


def main():
    """Main function to run the QR2Key application."""
    print("QR2Key - Convert QR codes to cryptographic keys and vice versa")
    print(f"Running on {platform.system()} {platform.architecture()[0]}")
    print("Windows-specific features:", "Available" if WIN32_AVAILABLE else "Not available")
    
    key = generate_key()
    print(f"Generated key: {key}")
    
    qr_path = key_to_qr(key)
    print(f"QR code saved to {qr_path}")
    
    copy_to_clipboard(key.decode('utf-8') if isinstance(key, bytes) else str(key))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
