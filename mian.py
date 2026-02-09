import sys
import asyncio
import json
import os
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QRect, QEasingCurve

# --- HARDWARE IMPORTS ---
try:
    from bleak import BleakScanner
    from pydbus import SystemBus
    from gi.repository import GLib
    DBUS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    DBUS_AVAILABLE = False

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# --- PRODUCTION STYLING ---
STYLE_SHEET = """
QMainWindow { background-color: #0b0b1a; }
QWidget { color: #ffffff; font-family: 'Segoe UI', sans-serif; }

#FloatingContainer {
    background-color: rgba(22, 22, 45, 0.98); 
    border-radius: 25px; 
    border: 2px solid rgba(79, 172, 254, 0.5);
}

QPushButton { 
    background-color: #4facfe; 
    border-radius: 12px; 
    padding: 12px; 
    font-weight: bold; 
    border: none; 
}

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

class CallMonitorThread(QThread):
    """REAL-TIME HARDWARE LISTENER"""
    incoming_call = pyqtSignal(str)

    def run(self):
        if not DBUS_AVAILABLE: return
        try:
            bus = SystemBus()
            # Subscribe to oFono for hardware call events
            bus.subscribe(sender='org.ofono', signal='CallAdded', callback=self.on_call_added)
            loop = GLib.MainLoop()
            loop.run()
        except: pass

    def on_call_added(self, path, properties):
        caller = properties.get('LineIdentification', 'Incoming Call')
        self.incoming_call.emit(str(caller))

class ScanThread(QThread):
    devices_found = pyqtSignal(list)
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            devices = loop.run_until_complete(BleakScanner.discover(timeout=5.0))
            self.devices_found.emit(list(devices))
        except: self.devices_found.emit([])

class PiLinkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Link Pro")
        self.setMinimumSize(800, 480) 
        self.setStyleSheet(STYLE_SHEET)
        
        self.active_popup = None
        self.seconds_active = 0
        
        # Start Hardware Monitor
        self.monitor = CallMonitorThread()
        self.monitor.incoming_call.connect(self.show_call_popup)
        self.monitor.start()

        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.tick_call_time)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.init_welcome()
        self.init_bluetooth()
        self.init_dashboard()
        self.init_logs()
        self.load_settings()

    def init_welcome(self):
        page = QWidget(); layout = QVBoxLayout(page)
        lbl = QLabel("Pi-Link Pro"); lbl.setStyleSheet("font-size: 60px; font-weight: bold; color: #4facfe;")
        sub = QLabel("Professional Mobile Interface"); sub.setStyleSheet("color: #666; font-size: 18px;")
        btn = QPushButton("Start Setup"); btn.setFixedSize(280, 70)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addStretch()
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.stack.addWidget(page)

    def init_bluetooth(self):
        page = QWidget(); layout = QVBoxLayout(page)
        header = QHBoxLayout()
        self.status_lbl = QLabel("Pair your phone via system settings first")
        self.btn_re = QPushButton("🔄 Scan Nearby"); self.btn_re.setFixedSize(160, 45)
        self.btn_re.clicked.connect(self.start_scan)
        header.addWidget(self.status_lbl); header.addStretch(); header.addWidget(self.btn_re)
        
        self.device_list_layout = QVBoxLayout()
        scroll = QScrollArea(); c = QWidget(); c.setLayout(self.device_list_layout); scroll.setWidget(c); scroll.setWidgetResizable(True)
        
        self.next_btn = QPushButton("Go to Dashboard"); self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        layout.addLayout(header); layout.addWidget(scroll); layout.addWidget(self.next_btn)
        self.stack.addWidget(page)

    def init_dashboard(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.conn_status = QLabel("📱 Status: Connected & Monitoring")
        self.conn_status.setStyleSheet("font-size: 22px; color: #4facfe;")
        
        btn_logs = QPushButton("📞 Call History & Activity"); btn_logs.setFixedSize(350, 80)
        btn_logs.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        btn_reset = QPushButton("Reset Setup"); btn_reset.setFixedSize(180, 40); btn_reset.setStyleSheet("background: #222;")
        btn_reset.clicked.connect(self.reset_system)
        
        layout.addWidget(self.conn_status); layout.addStretch()
        layout.addWidget(btn_logs, alignment=Qt.AlignmentFlag.AlignCenter); layout.addStretch()
        layout.addWidget(btn_reset, alignment=Qt.AlignmentFlag.AlignRight)
        self.stack.addWidget(page)

    def init_logs(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.log_layout = QVBoxLayout()
        scroll = QScrollArea(); c = QWidget(); c.setLayout(self.log_layout); scroll.setWidget(c); scroll.setWidgetResizable(True)
        btn = QPushButton("Back"); btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addWidget(QLabel("SYSTEM ACTIVITY")); layout.addWidget(scroll); layout.addWidget(btn)
        self.stack.addWidget(page)

    def start_scan(self):
        self.status_lbl.setText("Searching...")
        self.btn_re.setEnabled(False)
        self.thread = ScanThread(); self.thread.devices_found.connect(self.update_list); self.thread.start()

    def update_list(self, devices):
        self.btn_re.setEnabled(True)
        for i in reversed(range(self.device_list_layout.count())): 
            if self.device_list_layout.itemAt(i).widget(): self.device_list_layout.itemAt(i).widget().setParent(None)
        for d in [d for d in devices if d.name]:
            card = QFrame(); card.setStyleSheet("background: #161632; border-radius: 10px; padding: 8px;")
            cl = QHBoxLayout(card)
            cl.addWidget(QLabel(f"📱 {d.name}"))
            btn = QPushButton("Select"); btn.setFixedSize(90, 35)
            btn.clicked.connect(lambda ch, n=d.name: self.select_device(n))
            cl.addWidget(btn); self.device_list_layout.addWidget(card)

    def select_device(self, name):
        self.conn_status.setText(f"📱 Active: {name}")
        self.next_btn.setEnabled(True); self.add_log(f"Device Selected: {name}")
        with open(SETTINGS_FILE, "w") as f: json.dump({"device": name}, f)

    def show_call_popup(self, name):
        if self.active_popup: return
        self.active_popup = QWidget()
        self.active_popup.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.active_popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.active_popup.setFixedSize(480, 160)
        
        frame = QFrame(self.active_popup); frame.setObjectName("FloatingContainer"); frame.setFixedSize(480, 160); frame.setStyleSheet(STYLE_SHEET)
        l = QHBoxLayout(frame)
        
        v = QVBoxLayout()
        v.addWidget(QLabel("INCOMING CALL"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_name = QLabel(name); self.lbl_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        v.addWidget(self.lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_a = QPushButton("📞"); btn_a.setObjectName("AcceptBtn"); btn_a.setFixedSize(75,75); btn_a.clicked.connect(self.handle_accept)
        btn_r = QPushButton("✕"); btn_r.setObjectName("RejectBtn"); btn_r.setFixedSize(75,75); btn_r.clicked.connect(self.handle_reject)
        
        l.addLayout(v); l.addStretch(); l.addWidget(btn_a); l.addWidget(btn_r)
        
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 480) // 2
        self.anim = QPropertyAnimation(self.active_popup, b"geometry")
        self.anim.setDuration(700); self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.setStartValue(QRect(x, -200, 480, 160)); self.anim.setEndValue(QRect(x, 50, 480, 160))
        self.active_popup.show(); self.anim.start()

    def handle_accept(self):
        if DBUS_AVAILABLE:
            try:
                bus = SystemBus()
                modem = bus.get('org.ofono', '/hfp/modem_0')
                calls = modem.GetCalls()
                if calls:
                    call_obj = bus.get('org.ofono', calls[0][0])
                    call_obj.Answer()
            except: pass
        self.call_timer.start(1000); self.add_log("Call Picked Up")

    def handle_reject(self):
        if DBUS_AVAILABLE:
            try:
                bus = SystemBus()
                modem = bus.get('org.ofono', '/hfp/modem_0')
                modem.HangupAll()
            except: pass
        if self.active_popup: self.active_popup.close(); self.active_popup = None
        self.call_timer.stop(); self.seconds_active = 0; self.add_log("Call Ended")

    def tick_call_time(self):
        self.seconds_active += 1; m, s = divmod(self.seconds_active, 60)
        self.lbl_name.setText(f"In Call: {m:02d}:{s:02d}")

    def add_log(self, text):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        lbl = QLabel(f"[{now}] {text}"); lbl.setObjectName("LogEntry")
        self.log_layout.insertWidget(0, lbl)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    name = json.load(f).get("device")
                    self.conn_status.setText(f"📱 {name}"); self.stack.setCurrentIndex(2)
            except: pass

    def reset_system(self):
        if os.path.exists(SETTINGS_FILE): os.remove(SETTINGS_FILE)
        self.stack.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PiLinkApp(); window.show(); sys.exit(app.exec())
