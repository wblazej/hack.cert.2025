import json
import requests
from flask import Flask, request, abort

app = Flask(__name__)


@app.route('/run', methods=['POST'])
def run():
    payload = json.loads(request.data)
    if 'cmd' in payload:
        command = payload['cmd']
        if command != 'id':
            abort(403)
        else:
            payload = f'{{"content":{request.data.decode()}}}'
            print(payload)
            r = requests.post("http://runner/api/run", headers={"Content-Type": "application/json"}, data=payload)
            return r.content
    else:
        abort(404)


@app.get("/")
def index():
    return "You can't connect to this API with your browser. Check the source code."


if __name__ == "__main__":
    app.run(port=5001)
