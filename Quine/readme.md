# Quine

I decompiled the binary with ghidra and rewrote the VM code to python (*with a small help of LLM*). Then used `z3-solver` to get the flag. The output was not in a flag format, but I guessed that I need to add `ecsc25{}` and it was correct. Final solution:
```py
from z3 import *


OP_SHR = 0
OP_SETB = 1
OP_SETC = 2
OP_XORB = 3
OP_LITB = 4
OP_LITC = 5
OP_LOOP = 6
OP_EMIT = 7

z = Solver()
reg_a0 = BitVec('reg_a0', 64)
ra = reg_a0
rb = BitVecVal(0, 64)
rc = BitVecVal(0, 64)


def get(val):
    if 0 <= val <= 4:
        return BitVecVal(val, 64)
    elif val == 5:
        return ra
    elif val == 6:
        return rb
    elif val == 7:
        return rc


bytecode = [2, 5, 4, 2, 3, 7, 0, 3, 5, 3, 3, 7, 2, 5, 3, 7, 7, 6, 6, 0]
p = [(bytecode[i], bytecode[i+1]) for i in range(0, len(bytecode), 2)]

i = 0
_max = 20

for t in range(_max):
    for pc, (op, arg) in enumerate(p):
        if op == OP_SHR:
            ra = LShR(ra, get(arg))
        elif op == OP_SETB:
            rb = get(arg) & 7
        elif op == OP_SETC:
            rc = get(arg) & 7
        elif op == OP_XORB:
            rb = rb ^ get(arg)
        elif op == OP_LITB:
            rb = BitVecVal(2, 64)
        elif op == OP_LITC:
            rc = BitVecVal(6, 64)
        elif op == OP_EMIT:
            v = get(arg)
            expected = bytecode[i]
            z.add(v == expected)
            i += 1
        elif op == OP_LOOP:
            if t < _max - 1:
                z.add(ra != 0)
            else:
                z.add(ra == 0)
            break

if z.check() == sat:
    model = z.model()
    v = model[reg_a0].as_long()

    mask = 0x48C8CE7C0A532EC7
    key = v ^ mask
    print(key.to_bytes(8, 'big').decode('ascii'))
# AoC24d17
```