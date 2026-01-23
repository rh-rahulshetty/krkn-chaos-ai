#!/bin/bash

#******************************************************************************
# File: setup-krknctl.sh
# Author: Rahul Shetty (Perf & Scale)
# Date: 2025-05-13
#
# Description:
# Setup Krkn CLI locally.
#
#
# Usage:
# ./setup-krknctl.sh
#
# Pre-requisite:
# - jq
# - curl
#
#******************************************************************************

set -e  # Exit on error

# Create temp-directory
TMP_DIR=$(mktemp -d)
cd $TMP_DIR

cleanup() {
  echo "Cleaning up..."
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT  # Run cleanup on exit (success or error)

# Download the archive
LATEST_TAG=$(curl -s https://api.github.com/repos/krkn-chaos/krknctl/releases/latest | jq -r .tag_name)
echo "Downloading Krkn CLI Version: $LATEST_TAG"
curl -LO "https://krkn-chaos.gateway.scarf.sh/krknctl-${LATEST_TAG}-linux-amd64.tar.gz"

# Extract tar.gz file
tar -xvzf "krknctl-${LATEST_TAG}-linux-amd64.tar.gz"

# Move the binary to ~/.local/bin
mkdir -p ~/.local/bin
mv krknctl ~/.local/bin/
chmod +x ~/.local/bin/krknctl

# Verify installation
krknctl --version
