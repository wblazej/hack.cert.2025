import os
from Crypto.Cipher import AES

KEY = os.urandom(16)
NONCE = os.urandom(12)

def encrypt_message(message):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
    return cipher.encrypt(message.encode()).hex()

print(encrypt_message("hello world"))
print(encrypt_message("did you ever hear the tragedy of darth plagueis the wise"))
print(encrypt_message(open("flag.txt", "r").read()))
