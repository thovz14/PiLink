import sys, os, json, datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from ble_manager import BLEManager
from notification_manager import NotificationManager
from overlays import CallOverlay

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

STYLE_SHEET = """
QMainWindow { background-color: #0b0b1a; }
QWidget { color: #ffffff; font-family: 'Segoe UI'; }
#FloatingContainer {
    background-color: rgba(22,22,45,0.98);
    border-radius: 25px;
    border: 2px solid rgba(79,172,254,0.5);
}
QPushButton { background-color: #4facfe; border-radius: 12px; padding: 12px; font-weight: bold; }
#AcceptBtn { background-color: #28a745; border-radius: 35px; font-size: 26px; }
#RejectBtn { background-color: #ff3b30; border-radius: 35px; font-size: 26px; }
#LogEntry {
    background-color: #161632;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 8px;
    border-left: 5px solid #4facfe;
}
"""

class PiLinkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Link Pro")
        self.setMinimumSize(800, 480)
        self.setStyleSheet(STYLE_SHEET)

        self.overlay = None
        self.seconds_active = 0

        # Managers
        self.ble = BLEManager()
        self.ble.connected.connect(self.on_ble_connected)
        self.ble.disconnected.connect(self.on_ble_disconnected)
        self.ble.error.connect(self.on_ble_error)

        self.notifications = NotificationManager()
        self.notifications.incoming_call.connect(self.show_call_popup)

        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.tick_call_time)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.init_welcome()
        self.init_bluetooth()
        self.init_dashboard()
        self.init_logs()
        self.load_settings()

    # ---------- UI ----------
    def init_welcome(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.addStretch()
        title = QLabel("Pi-Link Pro")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #4facfe;")
        btn = QPushButton("Start Setup")
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        l.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addStretch()
        self.stack.addWidget(page)

    def init_bluetooth(self):
        page = QWidget()
        l = QVBoxLayout(page)
        self.status_lbl = QLabel("Select your phone")
        self.next_btn = QPushButton("Go to Dashboard")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        l.addWidget(self.status_lbl)
        l.addWidget(self.next_btn)
        self.stack.addWidget(page)

    def init_dashboard(self):
        page = QWidget()
        l = QVBoxLayout(page)
        self.conn_status = QLabel("📱 Not connected")
        self.conn_status.setStyleSheet("font-size: 22px; color: #4facfe;")
        l.addWidget(self.conn_status)
        self.stack.addWidget(page)

    def init_logs(self):
        page = QWidget()
        l = QVBoxLayout(page)
        self.log_layout = QVBoxLayout()
        scroll = QScrollArea()
        c = QWidget()
        c.setLayout(self.log_layout)
        scroll.setWidget(c)
        scroll.setWidgetResizable(True)
        l.addWidget(scroll)
        self.stack.addWidget(page)

    # ---------- LOGIC ----------
    def on_ble_connected(self, addr):
        self.conn_status.setText(f"📱 Connected: {addr}")
        self.add_log("BLE connected")

    def on_ble_disconnected(self):
        self.conn_status.setText("📱 Disconnected (reconnecting...)")
        self.add_log("BLE disconnected")

    def on_ble_error(self, err):
        self.add_log(f"BLE error: {err}")

    def show_call_popup(self, name):
        if self.overlay:
            return
        self.overlay = CallOverlay(name, self.accept_call, self.reject_call)
        self.overlay.show_overlay()

    def accept_call(self):
        self.call_timer.start(1000)
        self.add_log("Call accepted")

    def reject_call(self):
        if self.overlay:
            self.overlay.close()
            self.overlay = None
        self.call_timer.stop()
        self.seconds_active = 0
        self.add_log("Call rejected")

    def tick_call_time(self):
        self.seconds_active += 1

    def add_log(self, text):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        lbl = QLabel(f"[{t}] {text}")
        lbl.setObjectName("LogEntry")
        self.log_layout.insertWidget(0, lbl)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE) as f:
                device = json.load(f).get("device")
                if device:
                    self.stack.setCurrentIndex(2)
                    self.ble.connect_device(device)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PiLinkApp()
    win.show()
    sys.exit(app.exec())
