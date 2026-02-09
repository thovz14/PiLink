#!/bin/bash
# Pi-Link Pro - Production Installer for Pi-Apps

echo "🚀 Starting Pi-Link Pro Installation..."

# Update and install system dependencies
sudo apt-get update
echo "📦 Installing system components (Bluetooth & Telephony)..."
sudo apt-get install -y python3-pip python3-pyqt6 ofono bluez dbus python3-gi python3-dbus

# Install Python libraries
echo "🐍 Installing Python requirements..."
pip3 install bleak pydbus --break-system-packages

# Configure Bluetooth permissions
echo "🔒 Configuring hardware access..."
sudo usermod -a -G bluetooth $USER

# Enable oFono Service (Required for HFP/Calls)
echo "📲 Starting telephony services..."
sudo systemctl enable ofono
sudo systemctl start ofono

echo "✅ Done! PLEASE REBOOT YOUR PI after installation to activate Bluetooth permissions."