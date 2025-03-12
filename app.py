import os
from flask import Flask, render_template, Response, jsonify, request
from camera import *
from PIL import Image

app = Flask(__name__)

headings = ("Name", "Album", "Artist")
df1 = music_rec()
df1 = df1.head(15)

@app.route("/")
def index():
    return render_template("index.html", headings=headings, data=df1)

@app.route('/app')
def app_page():
    return render_template("app.html")

def gen(camera):
    while True:
        global df1
        frame, df1 = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")

@app.route("/video_feed")
def video_feed():
    return Response(
        gen(VideoCamera()), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/live_emotion")
def live_emotion():
    return real_time_emotion()

@app.route("/t")
def gen_table():
    return df1.to_json(orient="records")

@app.route("/get_recommendations")
def get_recommendations():
    [emotion, df1] = max_emotion_reccomendation()
    return jsonify({"detected_emotion": emotion, "music_data": df1.to_dict(orient="records") if df1 is not None else None})

@app.route('/image', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        image = Image.open(file.stream)
        image_array = np.array(image)
        [picture, detected_emotion] = emotion_rec(image_array)
        return jsonify({"emotion": detected_emotion})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Set to default 5000 for Render
    app.run(host="0.0.0.0", port=port)
