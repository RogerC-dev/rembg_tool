import io

import flask
from rembg import remove
from PIL import Image
import numpy as np

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


def remove_color_background(image_data, color_hex='#00FF00', tolerance=30):
    """
    Remove a specific color background from an image.
    Perfect for green screen / chroma key images.

    Args:
        image_data: Raw image bytes
        color_hex: Hex color to remove (default is bright green #00FF00)
        tolerance: How much variation from the target color to allow (0-255)
    """
    # Open image and convert to RGBA
    img = Image.open(io.BytesIO(image_data)).convert('RGBA')
    data = np.array(img)

    # Parse the target color
    color_hex = color_hex.lstrip('#')
    target_r = int(color_hex[0:2], 16)
    target_g = int(color_hex[2:4], 16)
    target_b = int(color_hex[4:6], 16)

    # Calculate the difference from target color for each pixel
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Find pixels that are close to the target color
    diff_r = np.abs(r.astype(int) - target_r)
    diff_g = np.abs(g.astype(int) - target_g)
    diff_b = np.abs(b.astype(int) - target_b)

    # A pixel is considered background if all channels are within tolerance
    mask = (diff_r <= tolerance) & (diff_g <= tolerance) & (diff_b <= tolerance)

    # Set alpha to 0 for background pixels
    data[:,:,3] = np.where(mask, 0, a)

    # Create result image
    result = Image.fromarray(data, 'RGBA')

    # Save to bytes
    output = io.BytesIO()
    result.save(output, format='PNG')
    output.seek(0)
    return output.getvalue()


@app.route('/removebg', methods=['POST'])
def remove_background():
    if 'file' not in flask.request.files:
        return "No file part", 400
    
    file = flask.request.files['file']

    if file.mimetype != 'image/jpeg' and file.mimetype != 'image/png':
        return "Invalid file type. Only PNG files are allowed.", 400
    
    # Check if user wants color-based removal
    mode = flask.request.form.get('mode', 'ai')  # 'ai' or 'color'

    if mode == 'color':
        # Color-based removal (for green screen / solid color backgrounds)
        color = flask.request.form.get('color', '#00FF00')  # Default to bright green
        tolerance = int(flask.request.form.get('tolerance', 30))
        result = remove_color_background(file.stream.read(), color, tolerance)
        return flask.send_file(io.BytesIO(result), download_name='output.png', mimetype='image/png')
    else:
        # AI-based removal (original behavior)
        return flask.send_file(io.BytesIO(remove(file.stream.read(), force_return_bytes=True)), download_name='output.png', mimetype='image/png')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)