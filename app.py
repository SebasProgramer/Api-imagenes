from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Helper function to save image to BytesIO
def save_image_to_bytesio(image):
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

# Route to upload an image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Ensure the filename is safe
    filename = secure_filename(file.filename)
    file_path = os.path.join("images", filename)
    file.save(file_path)

    return jsonify({'message': 'Image uploaded successfully', 'file_path': file_path}), 200

# Route to convert image to black and white
@app.route('/process-image/bw', methods=['POST'])
def convert_to_bw():
    file = request.files.get('image')
    r_weight = float(request.form.get('r_weight', 0.3))
    g_weight = float(request.form.get('g_weight', 0.59))
    b_weight = float(request.form.get('b_weight', 0.11))
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400

    image = Image.open(file.stream)
    bw_image = convert_to_bw_with_rgb(image, r_weight, g_weight, b_weight)
    img_io = save_image_to_bytesio(bw_image)

    return send_file(img_io, mimetype='image/jpeg')

# Route to adjust image contrast
@app.route('/process-image/contrast', methods=['POST'])
def adjust_contrast_route():
    file = request.files.get('image')
    contrast = float(request.form.get('contrast', 1.0))
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400

    image = Image.open(file.stream)
    enhanced_image = adjust_contrast(image, contrast)
    img_io = save_image_to_bytesio(enhanced_image)

    return send_file(img_io, mimetype='image/jpeg')

# Route to convert image to negative
@app.route('/process-image/negative', methods=['POST'])
def convert_to_negative_route():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400

    image = Image.open(file.stream)
    negative = negative_image(image)
    img_io = save_image_to_bytesio(negative)

    return send_file(img_io, mimetype='image/jpeg')

# Function to adjust contrast of an image
def adjust_contrast(image, contrast):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(contrast)

# Function to convert image to negative
def negative_image(image):
    return ImageOps.invert(image.convert("RGB"))

# Function to convert image to black and white using custom weights
def convert_to_bw_with_rgb(image, r_weight, g_weight, b_weight):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    data = np.array(image)
    r, g, b = data[:,:,0], data[:,:,1], data[:,:,2]
    gray = r * r_weight + g * g_weight + b * b_weight
    gray = np.clip(gray, 0, 255)
    data = np.stack((gray,) * 3, axis=-1)
    return Image.fromarray(data.astype(np.uint8))

if __name__ == "__main__":
    app.run(debug=True)
