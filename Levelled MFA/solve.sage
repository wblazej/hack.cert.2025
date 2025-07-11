from sage.all import QQ
from sage.all import ZZ
from sage.all import matrix
from sage.all import vector
import requests
import base64
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


def attack(y, k, s, m, a, c):
    """
    source: https://github.com/jvdsn/crypto-attacks/blob/master/attacks/lcg/truncated_state_recovery.py


    Recovers the states associated with the outputs from a truncated linear congruential generator.
    More information: Frieze, A. et al., "Reconstructing Truncated Integer Variables Satisfying Linear Congruences"
    :param y: the sequential output values obtained from the truncated LCG (the states truncated to s most significant bits)
    :param k: the bit length of the states
    :param s: the bit length of the outputs
    :param m: the modulus of the LCG
    :param a: the multiplier of the LCG
    :param c: the increment of the LCG
    :return: a list containing the states associated with the provided outputs
    """
    diff_bit_length = k - s

    # Preparing for the lattice reduction.
    delta = c % m
    y = vector(ZZ, y)
    for i in range(len(y)):
        # Shift output value to the MSBs and remove the increment.
        y[i] = (y[i] << diff_bit_length) - delta
        delta = (a * delta + c) % m

    # This lattice only works for increment = 0.
    B = matrix(ZZ, len(y), len(y))
    B[0, 0] = m
    for i in range(1, len(y)):
        B[i, 0] = a ** i
        B[i, i] = -1

    B = B.LLL()

    # Finding the target value to solve the equation for the states.
    b = B * y
    for i in range(len(b)):
        b[i] = round(QQ(b[i]) / m) * m - b[i]

    # Recovering the states
    delta = c % m
    x = list(B.solve_right(b))
    for i, state in enumerate(x):
        # Adding the MSBs and the increment back again.
        x[i] = int(y[i] + state + delta)
        delta = (a * delta + c) % m

    return x


class LCG:
    def __init__(self, bit_count: int, c: int):
        import random
        # from Crypto.Util.number import getPrime
        # p = getPrime(bit_count)
        # a = random.randint(p // 2, p)
        # print(p, a)
        p = 237265950040262713941897142843147616729
        a = 233399005916624306523442005425011133900
        self.a = a
        self.p = p
        if c:
            self.current = c
        else:
            self.current = random.randint(p // 2, p)

    def _next(self):
        self.current = self.a * self.current % self.p
        return self.current

    def getrandbits(self, bit_count: int) -> int:
        result_bits = []
        while len(result_bits) < bit_count:
            val = self._next()
            bits = bin(val)[2:].zfill(self.p.bit_length())
            result_bits.extend(bits)

        result_bits = result_bits[:bit_count]
        bitstring = ''.join(result_bits)
        return int(bitstring, 2)
    
def inverse_mod(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("No modular inverse exists")
    return x % m


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1

    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def get_previous_lcg_value(current, multiplier, increment, modulus):
    inv = inverse_mod(multiplier, modulus)
    return (inv * (current - increment)) % modulus


URL = "https://levelledmfa.ecsc25.hack.cert.pl/"

s = requests.Session()

passwords = []
token = None

for _ in range(64):
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    res = s.get(f"{URL}/generate", headers=headers).json()

    passwords.append(int.from_bytes(base64.b64decode(res["password"]), "big"))
    token = res["token"]

p = 237265950040262713941897142843147616729
a = 233399005916624306523442005425011133900

states = attack(passwords, 128, 64, p, a, 0)
prev = get_previous_lcg_value(states[0], a, 0, p)

states = attack([prev >> 64] + passwords, 128, 64, p, a, 0)
prev2 = get_previous_lcg_value(states[0], a, 0, p)

r = LCG(128, states[-1])

last_otp = s.post(f"{URL}/flag", headers={
    "Authorization": f"Bearer {token}",
}).text.split()[-1].split('</p>')[0]

while True:
    otp_try = base64.b64encode(r.getrandbits(
        8 * 8).to_bytes(8, 'big')).decode()
    if otp_try == last_otp:
        break
        
secret = (int(prev2) << 128 | int(prev)).to_bytes(32, 'big')

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = secret
jwt = JWTManager(app)
with app.test_request_context():
    token = create_access_token(identity="admin")

otp = base64.b64encode(r.getrandbits(
    8 * 8).to_bytes(8, 'big')).decode()

res = s.post(
    f"{URL}/flag",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={"OTP": otp}
).json()

print(res['flag'].strip())
