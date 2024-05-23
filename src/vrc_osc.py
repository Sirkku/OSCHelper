import struct
from enum import Enum
from typing import Optional, Callable

from PyQt6.QtCore import QObject, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QHostAddress


class OSCValueType():
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


def print_to_stdout_handler(osc_msg: OscMessage) -> None:
    osc_path, _, osc_value = osc_msg
    print(osc_path + " " + str(osc_value))


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
            return osc_path, OSCValueType.INT, struct.unpack(">i", osc_bytes[j + 3:j + 7])[0]
        case 102:  # b'f'[0]
            return osc_path, OSCValueType.FLOAT, struct.unpack(">f", osc_bytes[j + 3:j + 7])[0]


class VrcOscService(QObject):
    """
    VrcOscService provides functionality for sending and receiving OSC messages limited to the scope of VRChat and uses
    Qt Networking API for UDP.

    Being limited to VRChat means:
     1. only ",f", ",i", ",T", "F" (floats, ints, bools) are supported
     2. bundles are not implemented

     Usage:
     Call set_handler and then connect. Packages are now received and handled via Qt Event system.


    """

    def __init__(self):
        super(QObject, self).__init__()
        self.out_port: int = 9000
        self.out_ip: QHostAddress = QHostAddress("127.0.0.1")
        self.in_port: int = 9001
        self.in_ip: QHostAddress = QHostAddress("127.0.0.1")
        self.handler: Optional[Callable[[OscMessage], None]] = None
        self.udp_socket = QUdpSocket(self)

        self.udp_socket.readyRead.connect(self._read_pending_diagrams)

    def send(self, path, value_type, value):
        osc_bytes = encode_osc_message((path, value_type, value))
        self.udp_socket.writeDatagram(osc_bytes, self.out_ip, self.out_port)

    def set_handler(self, handler: Callable[[OscMessage], None]) -> None:
        self.handler = handler

    def connect(self, in_addr: QHostAddress, in_port: int, out_addr: QHostAddress, out_port: int):
        self.in_ip = in_addr
        self.in_port = in_port

        self.out_ip = out_addr
        self.out_port = out_port

        self.udp_socket.bind(self.in_ip, self.in_port)

    def _read_pending_diagrams(self):
        while self.udp_socket.hasPendingDatagrams():
            data: bytes
            (data, _, _) = self.udp_socket.readDatagram(1024)
            osc_msg = decode_osc_message(data)
            if osc_msg is None:
                return

            if self.handler is not None:
                self.handler(osc_msg)
