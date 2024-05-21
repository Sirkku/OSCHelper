from PyQt6.QtCore import QObject, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QHostAddress


class VrcOscService(QObject):
    def __init__(self):
        super(QObject).__super__()
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.bind(QHostAddress.LocalHost, 7755)

        self.udp_socket.readyRead.connect(self.readPendingDatagrams)

    def send(self, path, value):
        # construct osc message here
        pass

    def readPendingDatagrams(self):
        while self.udp_socket.hasPendingDatagrams():
            data: bytes
            (data, _, _) = self.udp_socket.readDatagram(1024)

            i = 0
            path_end = 0
            # find address
            while i < len(data):
                if data[i] == b"\x00":
                    path_end = i
                    break
                i = i + 1
            else:
                return

            # advance alignment character
            while i < len(data):
                if data[i] != b"\x00":
                    break
                i = i + 1
            else:
                return

            if data[i:i+1] == b"\x2c\x54": # ,T
                self.process(data[0:path_end], bool, True)
            if data[i:i + 1] == b"\x2c\x46":  # ,F
                self.process(data[0:path_end], bool, False)
            if data[i:i + 1] == b"\x2c\x69":  # ,i
                self.process(data[0:path_end], int, False)
            if data[i:i + 1] == b"\x2c\x66":  # ,f
                self.process(data[0:path_end], float, False)

    def process(self, path, value_type, value):
        pass



