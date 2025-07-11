# Files Storage

We got an expired link with a file hash, an expiration timestamp and a signature created with the hash and the timestamp. To get a link with a new signature (and a new expiration timestamp) with the same hash, we need to create a hash collision. Hashes of the files are XORed, so I found [this](https://github.com/malt3/sha256-xor-collisions/blob/master/hashXorBreaker.py). Using it, we can create a hash collision, therefore make an expired link valid. Entire solution:
```py
import hashlib, os


def popcount(x):
    x -= (x >> 1) & 0x5555555555555555
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    return ((x * 0x0101010101010101) & 0xffffffffffffffff ) >> 56


def format_hash_bin(h):
    s = len(h)
    return bin(int.from_bytes(h, byteorder='big'))[2:].rjust(s*8, '0')

def format_hash_hex(h):
    s = len(h)
    return hex(int.from_bytes(h, byteorder='big'))[2:].rjust(s * 2, '0')

def print_hash_bin(h):
    print(format_hash_bin(h))

def print_hash_hex(h):
    print(format_hash_hex(h))



def bit_from_bytes(h, idx):
    return (int.from_bytes(h, byteorder='big') >> idx) & 1


def xor_binary_string(b1, b2):
    size = max(len(b1),len(b2))
    result = bytearray(b'\x00'*size)
    for i in range(size):
        result[i] = b1[i] ^ b2[i]
    return bytes(result)


class HashBreaker:
    def __init__(self):
        self.lut = 256*[None]

    def hash(self, value):
        if not isinstance(value, bytes):
            raise TypeError('Value for hash must be in bytes')
        m = hashlib.sha256()
        m.update(value)
        hashval = m.digest()
        return hashval


    def xor_hash(self, list):
        result = b'\x00'*32
        for plaintext in list:
            result = xor_binary_string(result, self.hash(plaintext))
        return result

    def reduce_inputs(self, inputs):
        inputs.sort()
        occurence = 0
        prev = None
        new_list = []
        for value in inputs:
            if prev == value:
                occurence += 1
            else:
                if (prev is not None) and (occurence % 2):
                    new_list.append(prev)
                prev = value
                occurence = 1
        if len(inputs) and occurence % 2:
            new_list.append(inputs[-1])
        return new_list

    def generateLUT(self):
        for i in range(256):
            found_good_candidate = False
            while not found_good_candidate:
                candidate = os.urandom(32)
                hash_sum = self.hash(candidate)
                self.lut[i] = {'hash': None, 'inputs':[candidate]}
                for j in range(i):
                    if bit_from_bytes(hash_sum, j) != 0:
                        self.lut[i]['inputs'].extend(self.lut[j]['inputs'])
                self.lut[i]['inputs'] = self.reduce_inputs(self.lut[i]['inputs'])
                hash_sum = self.xor_hash(self.lut[i]['inputs'])
                if bit_from_bytes(hash_sum, i) == 0:
                    # Candidate NOT usable
                    continue
                else:
                    found_good_candidate = True
                self.lut[i]['hash'] = hash_sum


                for j in range(i):
                    if  bit_from_bytes(self.lut[j]['hash'], i) != 0:
                        self.lut[j]['inputs'].extend(self.lut[i]['inputs'])
                        self.lut[j]['inputs'] = self.reduce_inputs(self.lut[j]['inputs'])
                        self.lut[j]['hash'] = xor_binary_string(self.lut[j]['hash'], self.lut[i]['hash'])

    def fakeHash(self, wanted_hash):
        if not isinstance(wanted_hash, bytes):
            raise TypeError('wanted_hash must be in bytes')
        if len(wanted_hash) != 32:
            raise ValueError('wanted_hash must be a 256 Bit hash (32 bytes)')
        inputs = []
        for i in range(256):
            if bit_from_bytes(wanted_hash, i) != 0:
                inputs.extend(self.lut[i]['inputs'])
        inputs = self.reduce_inputs(inputs)
        return inputs

    def alterHash(self, previous_hash, wanted_hash):
        diff = xor_binary_string(previous_hash, wanted_hash)
        return self.fakeHash(diff)
    
    
import requests
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import re

EXPIRED_URL = 'https://files-storage.ecsc25.hack.cert.pl/resource/b0e9b3e3ae021b54eefca53e3a06a47d758198d7163edc054f8ee1456e491f20?exp=1751460814&S=b0b7b787686a987d78cb029d57dbb31892bec408681dd4477fad5c63ae8015c4c715a8b1331aed887615af8614419f68c813bda1217ccf51e4118706d787d548'

hb = HashBreaker()
hb.generateLUT()

target_hash_hex = urlparse(EXPIRED_URL).path.split('/')[-1]
target_hash_bytes = bytes.fromhex(target_hash_hex)

file_contents = hb.fakeHash(target_hash_bytes)

upload_url = urlparse(EXPIRED_URL)._replace(path="/upload", query="").geturl()

upload_payload = []
for i, content in enumerate(file_contents):
    filename = f"{i}.txt"
    upload_payload.append(('file', (filename, content, 'application/octet-stream')))

response = requests.post(upload_url, files=upload_payload, timeout=30)

soup = BeautifulSoup(response.text, 'html.parser')
link_tag = soup.find('a', href=lambda href: href and 'resource' in href)

new_link = unquote(link_tag['href'])

res = requests.get(f'{new_link}')
soup = BeautifulSoup(res.text, 'html.parser')
element = soup.find(lambda tag: tag.name == "a" and tag.text.strip() == "flag.txt")
res = requests.get(urlparse(EXPIRED_URL)._replace(path="/resource", query="").geturl() + "/" + element['href'])
print(re.findall(r'ecsc25{.*}', res.content.decode())[0])
# ecsc25{HashMeBabyOneMoreTime_72615207c}
```