from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from code_1 import get_farmer_advice, get_malayalam_speech, speak_malayalam

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Farmer Advisory System API",
        "status": "running",
        "endpoints": [
            "POST /advisory - Get farming advice",
            "POST /speech - Get advice via speech",
            "GET /audio - Download audio response",
            "GET /demo - Test endpoint"
        ]
    })


@app.route("/advisory", methods=["POST"])
def advisory():
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
        else:
            query = request.form.get("query")

        if not query:
            return jsonify({"error": "Missing query parameter"}), 400

        # Get farmer advice
        result = get_farmer_advice(query)

        # Generate audio
        speak_malayalam(result['response'])

        return jsonify({
            "query": query,
            "response": result['response'],
            "intent": result['intent'],
            "timestamp": result['timestamp'],
            "audio_url": "/audio"
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/audio", methods=["GET"])
def get_audio():
    try:
        audio_path = "malayalam_audio.mp3"
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype="audio/mpeg", as_attachment=True, download_name="advisory.mp3")
        return jsonify({"error": "Audio not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Audio error: {str(e)}"}), 500


@app.route("/speech", methods=["POST"])
def advisory_speech():
    try:
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

    except Exception as e:
        return jsonify({"error": f"Speech processing error: {str(e)}"}), 500


@app.route("/demo", methods=["GET"])
def demo():
    return jsonify({"message": "Hello, world!", "status": "API is working"})


if __name__ == "__main__":
    print("🌾 Starting Farmer Advisory System API...")
    print("🚀 Server starting on http://127.0.0.1:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)