"""
AI Digital Safety Shield — Flask Backend
=========================================
Run locally:   python app.py
Production:    gunicorn app:app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from analyzer import analyze_message

app = Flask(__name__)

# Allow requests from your frontend (adjust origins for production)
CORS(app, origins=["*"])


@app.route("/", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "AI Digital Safety Shield"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.

    Expected JSON body:
    {
        "message": "the text to analyze",
        "history": [                          ← optional, last 4 msgs
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }

    Returns:
    {
        "level":       "HIGH" | "MEDIUM" | "LOW",
        "fake_score":  0–100,
        "reason":      "one-sentence explanation",
        "threat_type": "grooming" | "manipulation" | ...,
        "categories":  ["tag1", "tag2"],
        "reasons":     ["short reason 1", "short reason 2"]
    }
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = str(data["message"]).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    result = analyze_message(message, history)
    return jsonify(result)


@app.route("/batch", methods=["POST"])
def batch_analyze():
    """
    Batch analysis for multiple messages at once.

    Expected JSON body:
    {
        "messages": ["msg1", "msg2", ...]
    }
    """
    data = request.get_json(silent=True)
    if not data or "messages" not in data:
        return jsonify({"error": "Missing 'messages' field"}), 400

    messages = data["messages"]
    if not isinstance(messages, list):
        return jsonify({"error": "'messages' must be an array"}), 400

    results = []
    for msg in messages[:20]:  # cap at 20 to prevent abuse
        results.append(analyze_message(str(msg).strip(), []))

    return jsonify({"results": results})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
