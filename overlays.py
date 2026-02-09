from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve

class CallOverlay(QWidget):
    def __init__(self, caller, on_accept, on_reject):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 160)

        frame = QFrame(self)
        frame.setObjectName("FloatingContainer")
        frame.setFixedSize(480, 160)

        layout = QHBoxLayout(frame)

        info = QVBoxLayout()
        info.addWidget(QLabel("INCOMING CALL"), alignment=Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(caller)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")
        info.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_accept = QPushButton("📞")
        btn_accept.setObjectName("AcceptBtn")
        btn_accept.setFixedSize(75, 75)
        btn_accept.clicked.connect(on_accept)

        btn_reject = QPushButton("✕")
        btn_reject.setObjectName("RejectBtn")
        btn_reject.setFixedSize(75, 75)
        btn_reject.clicked.connect(on_reject)

        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(btn_accept)
        layout.addWidget(btn_reject)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 480) // 2

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.setStartValue(QRect(x, -200, 480, 160))
        self.anim.setEndValue(QRect(x, 40, 480, 160))

    def show_overlay(self):
        self.show()
        self.anim.start()
