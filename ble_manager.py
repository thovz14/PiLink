import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from bleak import BleakClient

class BLEWorker(QThread):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, address):
        super().__init__()
        self.address = address
        self.running = True

    def run(self):
        asyncio.run(self.loop())

    async def loop(self):
        while self.running:
            try:
                async with BleakClient(self.address) as client:
                    if not client.is_connected:
                        raise Exception("BLE connect failed")

                    self.connected.emit(self.address)

                    while client.is_connected and self.running:
                        await asyncio.sleep(1)

            except Exception as e:
                self.error.emit(str(e))
                self.disconnected.emit()
                await asyncio.sleep(3)  # reconnect delay

    def stop(self):
        self.running = False


class BLEManager(QObject):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None

    def connect_device(self, address):
        if self.worker:
            self.worker.stop()
        self.worker = BLEWorker(address)
        self.worker.connected.connect(self.connected)
        self.worker.disconnected.connect(self.disconnected)
        self.worker.error.connect(self.error)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
