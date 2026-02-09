from PyQt6.QtCore import QObject, pyqtSignal

class NotificationManager(QObject):
    incoming_call = pyqtSignal(str)
    message = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def handle_notification(self, data: bytes):
        """
        Verwacht payloads zoals:
        CALL:John
        MSG:WhatsApp:Hallo
        """
        try:
            text = data.decode(errors="ignore")
            if text.startswith("CALL:"):
                self.incoming_call.emit(text[5:])
            elif text.startswith("MSG:"):
                self.message.emit(text[4:])
        except Exception:
            pass
