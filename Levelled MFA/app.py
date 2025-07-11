from flask import Flask, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request, JWTManager
import base64


class LCG:
    def __init__(self, bit_count: int):
        import random
        # from Crypto.Util.number import getPrime
        # p = getPrime(bit_count)
        # a = random.randint(p // 2, p)
        # print(p, a)
        p = 237265950040262713941897142843147616729
        a = 233399005916624306523442005425011133900
        self.a = a
        self.p = p
        self.current = random.randint(p // 2, p)
        print(f'Starting seed: {self.current}')

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


random = LCG(128)


def get_random_string(length):
    return random.getrandbits(length * 8).to_bytes(length, 'big')


def get_mfa():
    return base64.b64encode(get_random_string(8)).decode()


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = get_random_string(32)
jwt = JWTManager(app)

FLAG = open("flag.txt", 'r').read()
random_passwords = [base64.b64encode(get_random_string(8)).decode() for _ in range(64)]


@app.route('/generate', methods=['GET'])
def generate_password():
    token = verify_jwt_in_request(optional=True)
    if token is None:
        index = 0
    else:
        _, jwt_data = token
        index = (jwt_data['current'] + 1) % len(random_passwords)
    access_token = create_access_token(identity="user", additional_claims={'current': index})
    return jsonify({'token': access_token, 'password': random_passwords[index]})


@app.route('/flag', methods=['POST'])
@jwt_required()
def flag():
    current_user = get_jwt_identity()
    otp = get_mfa()
    if current_user == "admin" and request.json['OTP'] == otp:
        return jsonify({"flag": FLAG})
    else:
        abort(403, f"Nope, it was {otp}")


@app.get("/")
def index():
    return "You can't connect to this API with your browser. Check the source code."


if __name__ == "__main__":
    app.run()
