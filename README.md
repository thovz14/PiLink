# Pi-Link Pro 📱

[![badge](https://github.com/Botspot/pi-apps/blob/master/icons/badge-light.png?raw=true)](https://github.com/Botspot/pi-apps)

Pi-Link Pro is a professional mobile dashboard for Raspberry Pi users. It creates a seamless bridge between your smartphone and your Pi, allowing you to monitor activity and manage incoming calls directly from your desktop or touchscreen.

---

## ✨ Features
* **Call Management:** Receive notifications for incoming calls and answer or reject them through the interface.
* **Hardware Integration:** Deep integration with the Raspberry Pi Bluetooth stack using oFono and DBus.
* **Modern UI:** A clean, glassmorphism-inspired interface built with PyQt6.
* **Smart Connection:** Automatically remembers your last connected device for quick setup.
* **Activity Logs:** Track system activity and call history in real time.

## 🚀 Installation via Pi-Apps
This application is designed for the Raspberry Pi and is available through **Pi-Apps**.

1. Open Pi-Apps.
2. Search for `Pi-Link Pro`.
3. Click Install.
4. **Important:** Reboot your Raspberry Pi after installation to activate the required Bluetooth permissions.

---

## 📖 Usage

**Pairing:** First, pair your smartphone with your Raspberry Pi using the standard system Bluetooth settings.

**Launch:** Start Pi-Link Pro from your application menu.

**Setup:** Select your phone from the list inside the app to begin monitoring.

---

## 🔧 Feedback & Bugs

If you encounter issues or have suggestions:

* Open an Issue on this GitHub repository.
* Include your Raspberry Pi model and OS version.

---

## ⚖️ Copying & License

This project is provided "as is". You may use this software for personal use.  
For redistribution or commercial use, please contact the developer.

---

## 🛠 Manual Installation

If you prefer manual installation:

```bash
git clone https://github.com/thovz14/PiLink
cd PiLink
chmod +x install
./install
