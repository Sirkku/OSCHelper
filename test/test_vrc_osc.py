from unittest import TestCase

from src.vrc_osc import OSCValueType, VrcOscService

# \u8863\u670d = 衣服
encoding_data: list[tuple[bytes, str, OSCValueType, bool | float | int]] = [
    (
        b"\x2f\x61\x76\x61\x74\x61\x72\x2f"
        b"\x70\x61\x72\x61\x6d\x65\x74\x65"
        b"\x72\x73\x2f\x5c\x75\x38\x38\x36"
        b"\x33\x5c\x75\x36\x37\x30\x64\x00"
        b"\x2c\x69\x00\x00\x00\x00\x00\x00",
        "/avatar/parameters/\u8863\u670d",
        OSCValueType.INT,
        0
    ), (
        b"\x2f\x61\x76\x61\x74\x61\x72\x2f"
        b"\x70\x61\x72\x61\x6d\x65\x74\x65"
        b"\x72\x73\x2f\x5c\x75\x38\x38\x36"
        b"\x33\x5c\x75\x36\x37\x30\x64\x00"
        b"\x2c\x69\x00\x00\x00\x00\x00\x01",
        "/avatar/parameters/\u8863\u670d",
        OSCValueType.INT,
        1
    ), (
        b"\x2f\x61\x76\x61\x74\x61\x72\x2f"
        b"\x70\x61\x72\x61\x6d\x65\x74\x65"
        b"\x72\x73\x2f\x56\x46\x33\x35\x5f"
        b"\x54\x43\x5f\x63\x75\x72\x72\x65"
        b"\x6e\x74\x5f\x74\x72\x61\x63\x6b"
        b"\x69\x6e\x67\x4d\x6f\x75\x74\x68"
        b"\x00\x00\x00\x00\x2c\x69\x00\x00"
        b"\xff\xff\xff\xff",
        "/avatar/parameters/VF35_TC_current_trackingMouth",
        OSCValueType.INT,
        -1
    ), (
        b"\x2f\x61\x76\x61\x74\x61\x72\x2f"
        b"\x70\x61\x72\x61\x6d\x65\x74\x65"
        b"\x72\x73\x2f\x5c\x75\x35\x39\x33"
        b"\x34\x5c\x75\x35\x33\x64\x31\x00"
        b"\x2c\x66\x00\x00\x3f\x80\x00\x00",
        "/avatar/parameters/\u5934\u53d1",
        OSCValueType.FLOAT,
        1.0
    )]


class TestVrcOscService(TestCase):

    def test_encode_osc_message_0(self):
        self.subtest_encode_osc_message(encoding_data[0])

    def test_encode_osc_message_1(self):
        self.subtest_encode_osc_message(encoding_data[1])

    def test_encode_osc_message_2(self):
        self.subtest_encode_osc_message(encoding_data[2])

    def test_encode_osc_message_3(self):
        self.subtest_encode_osc_message(encoding_data[3])

    def subtest_encode_osc_message(self, case):
        osc_bin, osc_path, osc_type, osc_value = case
        osc_bin_2 = VrcOscService.encode_osc_message((osc_path, osc_type, osc_value))
        self.assertEqual(osc_bin, osc_bin_2)

    def test_decode_osc_message_0(self):
        self.subtest_decode_osc_message(encoding_data[0])

    def test_decode_osc_message_1(self):
        self.subtest_decode_osc_message(encoding_data[1])

    def test_decode_osc_message_2(self):
        self.subtest_decode_osc_message(encoding_data[2])

    def test_decode_osc_message_3(self):
        self.subtest_decode_osc_message(encoding_data[3])

    def subtest_decode_osc_message(self, case):
        osc_bin, osc_path, osc_type, osc_value = case
        osc_path_2, osc_type_2, osc_value_2 = VrcOscService.decode_osc_message(osc_bin)
        self.assertEqual(osc_path, osc_path_2)
        self.assertEqual(osc_type, osc_type_2)
        self.assertEqual(osc_value, osc_value_2)
