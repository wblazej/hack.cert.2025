# Warmup: RE

I decompiled the binary using ghidra and rewrote it to python:
```py
key_data = [
    0x8a7284ecb083fce4,
    0x262f310391ecb4e3,
    0x93b931f9f8c4cb30,
    0x6fe40fe752b0d0e0,
    0xb47f273,
    0xa59f,
    0x5f
]

expected_data = [
    0xe609b1ded3f09f81,
    0x4f485f66bc89df8a,
    0xbede5f908aa1ae5e,
    0x1dc9618e7fc4a582,
    0x79228416,
    0xc0ec,
    0x22
]

def to_bytes(values):
    result = []
    for val in values:
        if isinstance(val, int):
            if val <= 0xFF:
                byte_count = 1
            elif val <= 0xFFFF:
                byte_count = 2
            elif val <= 0xFFFFFF:
                byte_count = 3
            elif val <= 0xFFFFFFFF:
                byte_count = 4
            else:
                byte_count = 8
            
            for i in range(byte_count):
                result.append((val >> (i * 8)) & 0xFF)
    return result

key_bytes = to_bytes(key_data)
expected_bytes = to_bytes(expected_data)

key_bytes = key_bytes[:39]
expected_bytes = expected_bytes[:39]

flag = ""

for i in range(min(len(key_bytes), len(expected_bytes))):
    original_char = expected_bytes[i] ^ key_bytes[i]
    flag += chr(original_char)
    
print(flag)
# ecsc25{like-engineering-but-in-reverse}
```