"""
Unit tests for the Shift-JIS decoder functionality in QR2Key.

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

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qr2key import QR2Key


class TestDecoder(unittest.TestCase):
    """Test cases for the Shift-JIS decoder functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.qr2key = QR2Key()
    
    def test_decode_shift_jis_ascii(self):
        """Test decoding ASCII data from Shift-JIS."""
        test_data = b'Hello, World!'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, 'Hello, World!')
    
    def test_decode_shift_jis_japanese(self):
        """Test decoding Japanese data from Shift-JIS."""
        test_data = b'\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd\x90\xa2\x8a\x45'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, 'こんにちは世界')
    
    def test_decode_shift_jis_mixed(self):
        """Test decoding mixed ASCII and Japanese data from Shift-JIS."""
        test_data = b'Hello, \x90\xa2\x8a\x45!'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, 'Hello, 世界!')
    
    def test_decode_shift_jis_with_newline(self):
        """Test decoding Shift-JIS data with newline characters."""
        test_data = b'\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd\x0a\x90\xa2\x8a\x45'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, 'こんにちは\n世界')
    
    def test_decode_utf8_fallback(self):
        """Test fallback to UTF-8 when Shift-JIS decoding fails."""
        test_data = b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, 'こんにちは')
    
    def test_decode_invalid_data(self):
        """Test decoding invalid data with replacement characters."""
        test_data = b'\xFF\xFE\xFD\xFC'
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertTrue('�' in decoded)
    
    def test_decode_empty_data(self):
        """Test decoding empty data."""
        test_data = b''
        decoded = self.qr2key._decode_shift_jis(test_data)
        self.assertEqual(decoded, '')


if __name__ == '__main__':
    unittest.main()
