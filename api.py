from flask import Flask, request, jsonify, send_file
import os
from code_1 import get_farmer_advice, get_malayalam_speech, speak_malayalam

app = Flask(__name__)

@app.route("/advisory", methods=["POST"])
def advisory():
    query = request.form.get("query")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    result = get_farmer_advice(query)
    speak_malayalam(result['response'])
    return jsonify({
        "response": result['response'],
        "intent": result['intent'],
        "timestamp": result['timestamp'],
        "audio_url": "/audio"
    })

@app.route("/audio", methods=["GET"])
def get_audio():
    audio_path = "malayalam_audio.mp3"
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg", as_attachment=True, download_name="advisory.mp3")
    return jsonify({"error": "Audio not found"}), 404

@app.route("/speech", methods=["POST"])
def advisory_speech():
    query = get_malayalam_speech()
    if not query:
        return jsonify({"error": "Speech not recognized"}), 400
    result = get_farmer_advice(query)
    speak_malayalam(result['response'])
    return jsonify({
        "query": query,
        "response": result['response'],
        "intent": result['intent'],
        "timestamp": result['timestamp'],
        "audio_url": "/audio"
    })

@app.route("/demo", methods=["GET"])
def demo():
    return "Hello, world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

