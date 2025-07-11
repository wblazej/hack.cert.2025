from flask import Flask, render_template, request, make_response, abort, send_file, redirect
from random import choice
from string import ascii_lowercase
from pathlib import Path
from dns import rdatatype
import dns.resolver
from hashlib import sha256
from pydantic import BaseModel
from datetime import datetime
from urllib.parse import urlparse
from requests import get
import logging
import os


logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
DATA_STORAGE = Path("/storage")
FLAG = os.environ["FLAG"]

# 1mb should be plenty
MAX_FILE_SIZE = 1_000_000


class UserFile(BaseModel):
    filename: str
    size: int
    create: datetime


def resolve_domain(domain: str) -> str | None:
    if not domain:
        return None

    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]
    try:
        answer = resolver.resolve(domain, rdtype=rdatatype.A)
    except Exception:
        return None

    return str(answer[0])


def get_user_session() -> tuple[str, bool]:
    session = request.cookies.get('session')
    if not session:
        session = "".join(choice(ascii_lowercase) for _ in range (16))
        return session, True
    else:
        return session, False


def get_user_files(session: str) -> list[UserFile]:
    session_dir = sha256(session.encode()).hexdigest()
    user_dir = DATA_STORAGE / session_dir
    user_dir.mkdir(exist_ok=True)
    user_files = []

    for f in user_dir.iterdir():
        if not f.is_file():
            continue

        stat = f.stat()
        user_files.append(UserFile(
            filename=f.name,
            size=stat.st_size,
            create=stat.st_ctime
        ))
    return user_files


def get_user_file(filename: str) -> Path:
    session, set_cookie = get_user_session()
    if set_cookie:
        abort(400, "no session")

    session_dir = sha256(session.encode()).hexdigest()
    user_dir = DATA_STORAGE / session_dir

    if not user_dir.exists():
        abort(400, "no user")

    try:
        # why is this so complicated?
        file_path = user_dir / (user_dir.joinpath(filename).resolve().relative_to(user_dir.resolve()))
    except ValueError:
        abort(400)

    return file_path


@app.route("/")
def index():
    session, set_cookie = get_user_session()

    user_files = get_user_files(session=session)

    response = make_response(render_template("index.html", user_files=user_files))
    if set_cookie:
        response.set_cookie('session', session)
    return response


@app.route("/archive", methods=['POST'])
def archive_url():
    ALLOWED_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg"
    ]

    content_url = request.form["url"]

    parsed = urlparse(url=content_url)
    if not parsed:
        abort(400, "bad URL")

    if not any(content_url.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        abort(400, "bad extension")

    if parsed.scheme not in ("http", "https"):
        abort(400, "bad schema")

    resolved = resolve_domain(parsed.hostname)

    if not resolved:
        abort(400, "bad host")

    logging.info("resolved: %s", resolved)

    if resolved == "127.0.0.1":
        abort(400, "bad ip")

    headers = {
        "User-Agent": "content-archiver"
    }

    filename = parsed.path.split("/")[-1] or "image.png"
    output = get_user_file(filename=filename)

    logging.info("Downloading %s", content_url)

    try:
        r = get(url=content_url, headers=headers, stream=True, allow_redirects=False)
    except Exception:
        abort(400, "bad request")

    if r.status_code != 200:
        abort(400, "bad status")

    response_size = 0
    with output.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
            response_size += len(chunk)

            if response_size > MAX_FILE_SIZE:
                break

    logging.info("Saved %s bytes to %s", response_size, output)
    return redirect("/")


@app.route("/image/<filename>")
def get_archived_image(filename: str):
    f = get_user_file(filename=filename)

    if not f.is_file():
        abort(404, "no file")

    return send_file(f)


@app.route("/source")
def get_source():
    return send_file(__file__)


@app.route("/flag")
def get_flag():
    remote_ip = request.environ.get('HTTP_X_REAL_IP')

    if remote_ip and remote_ip != "127.0.0.1":
        abort(401)

    return make_response(FLAG)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=23612)
