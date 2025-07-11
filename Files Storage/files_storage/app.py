import hashlib
import hmac
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode

from flask import Flask, request, flash, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.update(
    # Upload PATH MUST exist in the FS and be writable
    UPLOAD_PATH=os.environ.get('APP_UPLOAD_PATH', '/tmp/uploads'),
    SECRET_KEY=os.environ.get('APP_SECRET_KEY', 'changeme').encode('ascii'),
    MAX_CONTENT_LENGTH=os.environ.get('APP_MAX_CONTENT_LENGTH', 2 * 1024 * 1024)
)


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(a, b))

def timestamp_now():
    return int(datetime.now().timestamp())

def timestamp_in(seconds=0, minutes=0, hours=0):
    new_time = datetime.now() + timedelta(seconds=seconds, minutes=minutes, hours=hours)
    return int(new_time.timestamp())

def allowed_file(filename):
    return filename.endswith('.txt') or ('.' not in filename)


@app.route('/')
def index():
    return redirect(url_for('upload'))


@app.route('/resource/<hash_id>')
def resource(hash_id):

    if not 'exp' in request.args or not 'S' in request.args:
        return 'Missing Expiry and/or Signature!'

    expire = request.args.get('exp')
    sign = request.args.get('S')

    if int(expire) < timestamp_now():
        return 'EXPIRED'

    digest = hmac.new(app.config['SECRET_KEY'], f'{hash_id}:{expire}'.encode('ascii'), hashlib.sha512).hexdigest()
    if sign != digest:
        return 'INVALID HMAC SIGNATURE'

    resource_files = []
    for path in os.listdir(os.path.join(app.config['UPLOAD_PATH'], hash_id)):
        query_string = urlencode({'exp': expire, 'S': digest})
        resource_files.append((f'{hash_id}/{path}?{query_string}', path))

    return render_template('resource.html', resource=resource_files, hash_id=hash_id)


@app.route('/resource/<hash_id>/<filename>')
def resource_file(hash_id, filename):

    if not 'exp' in request.args or not 'S' in request.args:
        return 'Missing Expiry and/or Signature!'

    expire = request.args.get('exp')
    sign = request.args.get('S')

    if int(expire) < timestamp_now():
        return 'EXPIRED'

    digest = hmac.new(app.config['SECRET_KEY'], f'{hash_id}:{expire}'.encode('ascii'), hashlib.sha512).hexdigest()
    if sign != digest:
        return 'INVALID HMAC SIGNATURE'

    with open(os.path.join(app.config['UPLOAD_PATH'], hash_id, filename), 'r', encoding='utf-8', errors='replace') as f:
        return render_template('resource_content.html', hash_id=hash_id, filename=filename, content=f.read())


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_post():
    resource_hash = bytes(32)

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    for file in request.files.getlist('file'):
        if not allowed_file(file.filename):
            flash('Illegal file extension, only .txt allowed')
            return redirect(request.url)

        file_hash = hashlib.sha256()
        chunk = file.stream.read(4*1024)
        while chunk:
            file_hash.update(chunk)
            chunk = file.stream.read(4*1024)
        # reset stream so it's read from the beginning when saving
        file.stream.seek(0)
        resource_hash = xor(resource_hash, file_hash.digest())

    if not os.path.exists(os.path.join(app.config['UPLOAD_PATH'], resource_hash.hex())):
        os.mkdir(os.path.join(app.config['UPLOAD_PATH'], resource_hash.hex()))

        for file in request.files.getlist('file'):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_PATH'], resource_hash.hex(), filename))

    expire = timestamp_in(minutes=10)
    digest = hmac.new(app.config['SECRET_KEY'], f'{resource_hash.hex()}:{expire}'.encode('ascii'), hashlib.sha512).hexdigest()

    url = f'{request.scheme}://{request.host}/resource/{resource_hash.hex()}'
    query_string = urlencode({'exp': expire, 'S': digest})
    download_link = f"{url}?{query_string}"

    return render_template('upload_success.html', download_link=download_link)


if __name__ == '__main__':
    app.run()
