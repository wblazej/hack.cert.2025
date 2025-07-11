import requests
from flask import Flask, request, abort

app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def submit():
    if 'url' in request.json:
        return requests.post(request.json['url']).content
    else:
        abort(404)


@app.get("/")
def index():
    return "You can't connect to this API with your browser. Check the source code."


assert requests.get("http://internal:5001/flag").content.startswith(b"ecsc")

if __name__ == "__main__":
    app.run(port=5000)
