import io

import flask
from rembg import remove

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/removebg', methods=['POST'])
def remove_background():
    if 'file' not in flask.request.files:
        return "No file part", 400
    
    file = flask.request.files['file']

    if file.mimetype != 'image/jpeg' and file.mimetype != 'image/png':
        return "Invalid file type. Only PNG files are allowed.", 400
    
    return flask.send_file(io.BytesIO(remove(file.stream.read(), force_return_bytes=True)), download_name='output.png', mimetype='image/png')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)