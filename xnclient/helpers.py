
# Convert a single hex character to its decimal equivalent
def hextoint(c):
    return int(c, 16)

def fromhex(str):
    # Bytes require pairs of hex digits
    # str should be an even number of chars followed by an LF
    if (len(str) ==1) | (len(str) % 2 == 0):
        return None

    # Convert two characters at a time to their decimal equivalent
    result = []
    for i in range(0, len(str) - 1, 2):
        result.append(int(str[i:i+2], 16))
    return result
