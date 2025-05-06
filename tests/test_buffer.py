"""
Unit tests for the SerialBuffer class in QR2Key.

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
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qr2key import SerialBuffer


class TestSerialBuffer(unittest.TestCase):
    """Test cases for the SerialBuffer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.buffer = SerialBuffer(idle_timeout_ms=50)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.buffer.clear()
    
    def test_init(self):
        """Test initialization of SerialBuffer."""
        self.assertEqual(self.buffer.idle_timeout_ms, 50)
        self.assertEqual(len(self.buffer.buffer), 0)
    
    def test_add_data(self):
        """Test adding data to the buffer."""
        test_data = b'test data'
        self.buffer.add_data(test_data)
        self.assertEqual(bytes(self.buffer.buffer), test_data)
    
    def test_is_complete_with_cr(self):
        """Test is_complete with CR in buffer."""
        self.buffer.add_data(b'test\rdata')
        self.assertTrue(self.buffer.is_complete())
    
    def test_is_complete_with_lf(self):
        """Test is_complete with LF in buffer."""
        self.buffer.add_data(b'test\ndata')
        self.assertTrue(self.buffer.is_complete())
    
    def test_is_complete_with_timeout(self):
        """Test is_complete with timeout."""
        self.buffer.add_data(b'test data')
        self.buffer.last_data_time = time.time() * 1000 - 100  # 100ms ago
        self.assertTrue(self.buffer.is_complete())
    
    def test_is_not_complete(self):
        """Test is_complete when buffer is not complete."""
        self.buffer.add_data(b'test data')
        self.assertFalse(self.buffer.is_complete())
    
    def test_get_data(self):
        """Test getting and clearing buffer data."""
        test_data = b'test data'
        self.buffer.add_data(test_data)
        data = self.buffer.get_data()
        self.assertEqual(data, test_data)
        self.assertEqual(len(self.buffer.buffer), 0)  # Buffer should be cleared
    
    def test_clear(self):
        """Test clearing the buffer."""
        self.buffer.add_data(b'test data')
        self.buffer.clear()
        self.assertEqual(len(self.buffer.buffer), 0)


if __name__ == '__main__':
    unittest.main()
