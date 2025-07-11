# Warmup: Crypto

The same keystream is used for all the ciphertexts. Knowing the plaintext we can recover the keystream and decrypt the flag:
```py
from binascii import unhexlify

known = unhexlify('b59743485c1542092a545cbe34623b5ed349c241d9ea6aac70915229e777931467b5ac191e68baff0f824f8e2ca3f9af6a107b24196fcc4d')
flag = unhexlify('b49d540b174f4c4a3d5b49b87b27335ac007c504dfb867ae6599503fff27940b6ab0a30f4767fffb4e8c4e9d64a7f3a27219696a130c')
plain = 'did you ever hear the tragedy of darth plagueis the wise'

keystream = [a ^ b for a, b in zip(known, plain.encode())]

dec = bytes([a ^ b for a, b in zip(keystream, flag)])
print(dec.decode().strip())
# ecsc25{crypto-means-cryptography-and-get-off-my-lawn}
```
