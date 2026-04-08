#!/bin/bash

# Upgrade pip first
pip install --upgrade pip

# Install pandas with no cache dir to avoid compilation issues
pip install --no-cache-dir pandas==2.0.3

# Install other dependencies
pip install --no-cache-dir -r requirements.txt

echo "Build completed successfully!"
