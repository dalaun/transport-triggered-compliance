from flask import Flask, request, jsonify
from canonizer import mediate

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return {"service": "Mediator-Canonizer API", "version": "1.0.0"}

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

@app.route("/mediate", methods=["POST"])
def mediate_route():
    try:
        data = request.get_json()
        if not data or len(data.get("positions", [])) < 2:
            return {"error": "At least two positions required"}, 400
        return mediate(data), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8745, debug=False)
