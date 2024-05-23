import unittest

def crc_calculate(data, poly):
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
    return crc & 0xFFFF

def crc_check(data, poly, crc):
    return crc_calculate(data, poly) == crc

class TestCRC(unittest.TestCase):
    def test_crc_calculation(self):
        data = b"Hello, World!"
        poly = 0x1021
        expected_crc = 26586
        self.assertEqual(crc_calculate(data, poly), expected_crc)

    def test_crc_check_correct_data(self):
        data = b"Hello, world!"
        poly = 0x1021
        crc = crc_calculate(data, poly)
        self.assertTrue(crc_check(data, poly, crc))

    def test_crc_check_incorrect_data(self):
        data = b"Hello, world!"
        poly = 0x1021
        crc = crc_calculate(data, poly)

        data_with_error = bytearray(data)
        data_with_error[1] ^= 1 
        self.assertFalse(crc_check(data_with_error, poly, crc))

    def test_packet_processing(self):
        text = "This is a test message for CRC-16."
        data = text.encode('utf-8')
        poly = 0x1021
        packet_size = 5

        original_packets = [data[i:i+packet_size] for i in range(0, len(data), packet_size)]
        packets = [data[i:i+packet_size] for i in range(0, len(data), packet_size)]

        packets[1] = bytearray(packets[1])
        packets[1][2] ^= 1
        packets[3] = bytearray(packets[3])
        packets[3][0] ^= 1
        print()

        for i, packet in enumerate(packets):
            crc = crc_calculate(original_packets[i], poly)
            encoded_packet = original_packets[i] + crc.to_bytes(2, byteorder='big')
            print(f"Пакет {i+1}:")
            print(f"    Оригинальные данные: {original_packets[i].decode('utf-8')}")
            print(f"    CRC: {crc:04x}")
            print(f"    Закодированный пакет: {encoded_packet.hex()}")
            print(f"    Измененные данные: {packet.decode('utf-8')}")
            
            if crc_check(packet, poly, crc):
                print("    Данные верны")
            else:
                print("    Данные повреждены")
            print("-" * 20)

if __name__ == '__main__':
    unittest.main()


