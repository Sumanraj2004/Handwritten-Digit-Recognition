from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
import base64
import cv2

app = Flask(__name__)

# Load Model
model = tf.keras.models.load_model("model/mnist_model.h5")


# -------------------- PREPROCESSING (VERY IMPORTANT) --------------------
def preprocess_image_from_b64(b64string):
    # Decode base64
    img_data = base64.b64decode(b64string.split(",")[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # Invert (MNIST expects white digit on black)
    if np.mean(img) > 127:
        img = 255 - img

    # Threshold to pure black/white
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find bounding box of digit
    coords = cv2.findNonZero(img)
    if coords is None:
        return np.zeros((1, 28, 28), np.float32)

    x, y, w, h = cv2.boundingRect(coords)
    digit = img[y:y+h, x:x+w]

    # Resize while keeping aspect ratio (MNIST method)
    h, w = digit.shape
    if h > w:
        new_h = 20
        new_w = int((w / h) * 20)
    else:
        new_w = 20
        new_h = int((h / w) * 20)

    digit = cv2.resize(digit, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Pad to 28×28 and center the digit
    padded = np.zeros((28, 28), dtype=np.uint8)
    x_offset = (28 - new_w) // 2
    y_offset = (28 - new_h) // 2
    padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = digit

    # Normalize
    padded = padded.astype(np.float32) / 255.0
    return padded.reshape(1, 28, 28)


# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    image_data = request.json["image"]
    img = preprocess_image_from_b64(image_data)

    prediction = model.predict(img)
    digit = int(np.argmax(prediction))

    return jsonify({"digit": digit})


if __name__ == "__main__":
    app.run(debug=True)
