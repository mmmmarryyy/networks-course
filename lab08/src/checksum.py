def calculate_checksum(data, k=16):
    sum = 0
    for i in range(0, len(data), k):
        value = int.from_bytes(data[i:i+k], byteorder='big', signed=False)
        sum = ((sum + value) & 0xffff) + ((sum + value) >> 16)
    return ~sum & 0xffff

def verify_checksum(data, checksum, k=16):
    sum = checksum
    for i in range(0, len(data), k):
        value = int.from_bytes(data[i:i+k], byteorder='big', signed=False)
        sum = ((sum + value) & 0xffff) + ((sum + value) >> 16)
    return (sum & 0xffff) == 0xffff


data = bytes([0x12, 0x34, 0x56, 0x78])
checksum = calculate_checksum(data)
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(data, checksum))
assert verify_checksum(data, checksum) == True

data = bytes([0x12, 0x34, 0x56, 0x78])
checksum = calculate_checksum(data) + 90
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(data, checksum))
assert verify_checksum(data, checksum) == False

data = bytes([0x12, 0x34, 0x56, 0x78]) 
checksum = calculate_checksum(data)
broken_data = bytes([0x13, 0x34, 0x56, 0x78])
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(broken_data, checksum))
assert verify_checksum(broken_data, checksum) == False

data = bytes([0x12, 0x34, 0x56, 0x78])
checksum = calculate_checksum(data, k=32)
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(data, checksum, k=32))
assert verify_checksum(data, checksum, k=32) == True

data = bytes([0x12, 0x34, 0x56, 0x78])
checksum = calculate_checksum(data, k=32) + 90
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(data, checksum, k=32))
assert verify_checksum(data, checksum, k=32) == False

data = bytes([0x12, 0x34, 0x56, 0x78]) 
checksum = calculate_checksum(data, k=32)
broken_data = bytes([0x13, 0x34, 0x56, 0x78])
print("Checksum: ", checksum)
print("Verify result: ", verify_checksum(broken_data, checksum, k=32))
assert verify_checksum(broken_data, checksum, k=32) == False