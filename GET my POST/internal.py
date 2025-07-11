from flask import Flask

app = Flask(__name__)


@app.route('/flag', methods=['GET'])
def flag():
    return open("flag.txt", 'r').read()


if __name__ == "__main__":
    app.run(port=5001)
