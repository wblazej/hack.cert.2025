import struct
from z3 import *

# Create 16 32-bit variables for the 64-byte flag (16 * 4 = 64 bytes)
flag_vars = [BitVec(f'flag_{i}', 32) for i in range(16)]

# Map variables to the stack layout (based on the decompiled code)
# The stack grows downward, so higher addresses come first
uStack_818 = flag_vars[0]   # First 4 bytes
uStack_814 = flag_vars[1]   # Next 4 bytes
uStack_810 = flag_vars[2]
uStack_80c = flag_vars[3]
uStack_808 = flag_vars[4]
uStack_804 = flag_vars[5]
uStack_800 = flag_vars[6]
uStack_7fc = flag_vars[7]
uStack_7f8 = flag_vars[8]
uStack_7f4 = flag_vars[9]
uStack_7f0 = flag_vars[10]
uStack_7ec = flag_vars[11]
uStack_7e8 = flag_vars[12]
uStack_7e4 = flag_vars[13]
uStack_7e0 = flag_vars[14]
uStack_7dc = flag_vars[15]   # Last 4 bytes

solver = Solver()

# Add constraints based on the decompiled code
# CONCAT44(high, low) combines two 32-bit values: (high << 32) | low

# Constraint 1: (CONCAT44(uStack_814,uStack_818) ^ CONCAT44(uStack_80c,uStack_810)) == 0x56465f0f1f4e0a
val1 = Concat(uStack_814, uStack_818)
val2 = Concat(uStack_80c, uStack_810)
solver.add(val1 ^ val2 == 0x56465f0f1f4e0a)

# Constraint 2: CONCAT44(uStack_804,uStack_808) - CONCAT44(uStack_7fc,uStack_800) == 0x44edf4edfb46ba00
val3 = Concat(uStack_804, uStack_808)
val4 = Concat(uStack_7fc, uStack_800)
solver.add(val3 - val4 == 0x44edf4edfb46ba00)

# Constraint 3: CONCAT44(uStack_7ec,uStack_7f0) + CONCAT44(uStack_7f4,uStack_7f8) == -0x6035271f31222c29
val5 = Concat(uStack_7ec, uStack_7f0)
val6 = Concat(uStack_7f4, uStack_7f8)
solver.add(val5 + val6 == (-0x6035271f31222c29) & 0xffffffffffffffff)

# Constraint 4: (CONCAT44(uStack_7e4,uStack_7e8) ^ CONCAT44(uStack_7dc,uStack_7e0)) == 0xd73433748040f0c
val7 = Concat(uStack_7e4, uStack_7e8)
val8 = Concat(uStack_7dc, uStack_7e0)
solver.add(val7 ^ val8 == 0xd73433748040f0c)

# Constraint 5: CONCAT44(uStack_808,uStack_80c) + CONCAT44(uStack_810,uStack_814) == -0x2e1fa52123575761
val9 = Concat(uStack_808, uStack_80c)
val10 = Concat(uStack_810, uStack_814)
solver.add(val9 + val10 == (-0x2e1fa52123575761) & 0xffffffffffffffff)

# Constraint 6: CONCAT44(uStack_800,uStack_804) - CONCAT44(uStack_7f8,uStack_7fc) == 0x4b70dfd44edf4ee
val11 = Concat(uStack_800, uStack_804)
val12 = Concat(uStack_7f8, uStack_7fc)
solver.add(val11 - val12 == 0x4b70dfd44edf4ee)

# Constraint 7: CONCAT44(uStack_7e8,uStack_7ec) + CONCAT44(uStack_7f0,uStack_7f4) == -0x6931233160352720
val13 = Concat(uStack_7e8, uStack_7ec)
val14 = Concat(uStack_7f0, uStack_7f4)
solver.add(val13 + val14 == (-0x6931233160352720) & 0xffffffffffffffff)

# Constraint 8: (uStack_818 ^ uStack_7e4) == 0x135e0d0c
solver.add(uStack_818 ^ uStack_7e4 == 0x135e0d0c)

# Constraint 9: (uStack_7e0 ^ uStack_7dc) == 0x183d4c3b
solver.add(uStack_7e0 ^ uStack_7dc == 0x183d4c3b)

# Constraint 10: (uStack_804 ^ uStack_800) == 0x184f1b0c
solver.add(uStack_804 ^ uStack_800 == 0x184f1b0c)

# Constraint 11: (uStack_7ec ^ uStack_7e8) == 0x5f020b07
solver.add(uStack_7ec ^ uStack_7e8 == 0x5f020b07)

# Add constraint for the flag format "ecsc25{" at the beginning
# "ecsc25{" = 0x7b35327363736365 (as 64-bit little-endian)
# But we need to check the exact byte order

# Let's force the first 7 bytes to be "ecsc25{"
ecsc25_bytes = b"ecsc25{"
for i in range(7):
    byte_idx = i // 4  # Which 32-bit word
    byte_pos = i % 4   # Position within the word
    expected_byte = ecsc25_bytes[i]
    
    # Extract the specific byte from the word
    actual_byte = (flag_vars[byte_idx] >> (byte_pos * 8)) & 0xff
    solver.add(actual_byte == expected_byte)

# Add constraint for closing brace "}" at the end (position 63)
closing_brace_word = 63 // 4  # Word 15
closing_brace_pos = 63 % 4    # Position 3
actual_closing_byte = (flag_vars[closing_brace_word] >> (closing_brace_pos * 8)) & 0xff
solver.add(actual_closing_byte == ord('}'))

# Add constraints for printable ASCII characters for the rest
for var_idx, var in enumerate(flag_vars):
    for byte_pos in range(4):
        global_byte_idx = var_idx * 4 + byte_pos
        if global_byte_idx < 7 or global_byte_idx == 63:
            continue  # Skip bytes we've already constrained
        
        byte_val = (var >> (byte_pos * 8)) & 0xff
        solver.add(And(byte_val >= 32, byte_val <= 126))  # Printable ASCII

if solver.check() == sat:
    model = solver.model()
    flag_bytes = []
    
    for var in flag_vars:
        val = model[var].as_long()
        # Convert 32-bit value to 4 bytes (little-endian)
        bytes_chunk = struct.pack('<I', val)
        flag_bytes.extend(bytes_chunk)
    
    flag = ''.join(chr(b) for b in flag_bytes)
    print(flag)

