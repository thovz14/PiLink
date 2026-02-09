# Pi-Link Pro 📱

[![badge](https://github.com/Botspot/pi-apps/blob/master/icons/badge.png?raw=true)](https://github.com/Botspot/pi-apps)

**Pi-Link Pro** is a professional mobile dashboard for Raspberry Pi users. It creates a seamless bridge between your smartphone and your Pi, allowing you to monitor activity and handle incoming calls directly from your desktop or touchscreen.

---

## ✨ Features
* **Call Management:** Receive notifications for incoming calls and answer/reject them via the interface.
* **Hardware Integration:** Deep integration with the Raspberry Pi Bluetooth stack using oFono and DBus.
* **Modern UI:** A clean, glassmorphism-inspired interface built with PyQt6.
* **Smart Connection:** Automatically remembers your last connected device for a quick setup.
* **Activity Logs:** Keep track of your system and call history in real-time.

## 🚀 Installation via Pi-Apps
This application is designed specifically for the Raspberry Pi and is compatible with **Pi-Apps**.

1. Open **Pi-Apps**.
2. Search for `Pi-Link Pro`.
3. Click **Install**.
4. **Important:** Reboot your Raspberry Pi after installation to activate the necessary Bluetooth permissions.

## 🛠 Manual Installation
If you prefer to install manually:
```bash
git clone [https://github.com/thovz14/PiLink](https://github.com/thovz14/PiLink)
cd PiLink
chmod +x install
./install
