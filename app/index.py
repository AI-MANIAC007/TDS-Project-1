from flask import Flask, request, jsonify
from rag import answer_question
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
load_dotenv()
CORS(app)

@app.route("/api", methods=["POST"])
def api():
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required."}), 400

    answer, links = answer_question(question)
    return jsonify({"answer": answer, "links": links})

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "TDS Virtual TA API is running!"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
