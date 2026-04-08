#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Scrapling browser dependencies
"""

from scrapling.cli import install

print("Installing Scrapling browser dependencies...")
print("This may take a few minutes...\n")

# Install browsers
install([], standalone_mode=False)

print("\n[OK] Browser dependencies installed successfully!")
