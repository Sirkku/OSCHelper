import struct
from enum import Enum
from typing import Optional

from PyQt6.QtCore import QObject, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QHostAddress


class OSCValueType(Enum):
    FLOAT: str = "Float"
    BOOL: str = "Bool"
    INT: str = "Int"
    UNDEFINED: str = "Undefined"

    single_letter = {
        FLOAT: "F",
        BOOL: "B",
        INT: "I",
        UNDEFINED: "?"
    }


type OscMessage = tuple[str, OSCValueType, bool | float | int]


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
            osc_msg = self.decode_osc_message(data)
            if osc_msg is None:
                return

    def process(self, path: str, value_type: OSCValueType, value: float | int | bool):
        pass

    @staticmethod
    def encode_osc_message(osc_msg: OscMessage) -> bytes:
        (osc_path, osc_value_type, osc_value) = osc_msg

        osc_path_bytes = osc_path.encode('ascii', errors='backslashreplace')
        # zero terminator and 4-byte align
        osc_path_bytes += b'\x00' * (4 - len(osc_path_bytes) % 4)

        match osc_value_type:
            case OSCValueType.BOOL:
                if osc_value:
                    return osc_path_bytes + b',T\x00\x00'
                else:
                    return osc_path_bytes + b',F\x00\x00'
            case OSCValueType.FLOAT:
                return osc_path_bytes + b',f\x00\x00' + struct.pack(">f", osc_value)
            case OSCValueType.INT:
                return osc_path_bytes + b',i\x00\x00' + struct.pack(">i", osc_value)

    @staticmethod
    def decode_osc_message(osc_bytes: bytes) -> Optional[OscMessage]:
        osc_path: str
        i = 0
        path_end = 0
        while i < len(osc_bytes):
            if osc_bytes[i] == 0:
                path_end = i
                break
            i = i + 1
        else:  # format violation
            return

        osc_path = osc_bytes[0:path_end].decode("unicode-escape")
        j = 4 * (path_end // 4 + 1) + 1

        match osc_bytes[j]:
            case 84:  # b'T'[0]
                return osc_path, OSCValueType.BOOL, True
            case 70:  # b'F'[0]
                return osc_path, OSCValueType.BOOL, False
            case 105:  # b'i'[0]
                return osc_path, OSCValueType.INT, struct.unpack(">i", osc_bytes[j+3:j+7])[0]
            case 102:  # b'f'[0]
                return osc_path, OSCValueType.FLOAT, struct.unpack(">f", osc_bytes[j+3:j+7])[0]
