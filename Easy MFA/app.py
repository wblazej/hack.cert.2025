import base64
import random
from flask import Flask, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request, JWTManager


def get_random_string(length):
    return random.getrandbits(length * 8).to_bytes(length, 'big')


def get_mfa():
    return base64.b64encode(get_random_string(8)).decode()


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = get_random_string(32)
jwt = JWTManager(app)

FLAG = open("flag.txt", 'r').read()
random_passwords = [base64.b64encode(get_random_string(8)).decode() for _ in range(384)]


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
