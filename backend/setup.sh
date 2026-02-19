#!/bin/bash

set -e  # stop on error

echo "Installing libpostal..."
brew install libpostal

echo "Configuring environment variables..."
export LIBPOSTAL_PREFIX="$(brew --prefix libpostal)"
export CFLAGS="-I$LIBPOSTAL_PREFIX/include"
export LDFLAGS="-L$LIBPOSTAL_PREFIX/lib"
export PKG_CONFIG_PATH="$LIBPOSTAL_PREFIX/lib/pkgconfig"

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Setup complete!"
