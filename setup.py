"""Setup script for QR2Key."""

import os
import platform
from setuptools import setup, find_packages

install_requires = [
    'qrcode>=7.3.1',
    'pillow>=9.0.0',
    'pyzbar>=0.1.9',
    'cryptography>=38.0.0',
]

if platform.system() == 'Windows':
    install_requires.append('pywin32>=303')

setup(
    name="qr2key",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'qr2key=qr2key.main:main',
        ],
    },
)
