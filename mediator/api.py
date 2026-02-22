from flask import Flask, request, jsonify
from canonizer import mediate
import os
import sys
sys.path.insert(0, '/root/ttcd-pub/mediator')

app = Flask(__name__)

def try_register_on_chain(result):
    try:
        from chain import register_on_chain
        private_key = os.environ.get('PRIVATE_KEY')
        if not private_key:
            return None
        canon = result['canon']
        citation = result['citation']
        return register_on_chain(
            domain=canon['domain'],
            status=canon['status'],
            hash_hex=canon['hash'],
            cite_as=citation['cite_as'],
            private_key=private_key
        )
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Mediator-Canonizer API",
        "version": "1.0.0",
        "cmp_doi": "10.5281/zenodo.18732820",
        "contract": "0xf2325531264CA4Fc2cEC5D661E2200eA8013b091",
        "network": "Base mainnet (8453)",
        "endpoints": {
            "POST /mediate": "Submit positions for canonization",
            "GET /health": "Service health check"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mediator-canonizer", "contract": "0xf2325531264CA4Fc2cEC5D661E2200eA8013b091"})

@app.route("/mediate", methods=["POST"])
def mediate_route():
    try:
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "Request body must be JSON"}), 400
        if len(input_data.get("positions", [])) < 2:
            return jsonify({"error": "At least two positions required"}), 400
        result = mediate(input_data)
        chain_result = try_register_on_chain(result)
        if chain_result:
            result["chain"] = chain_result
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Mediator-Canonizer API v1.0")
    print("Contract: 0xf2325531264CA4Fc2cEC5D661E2200eA8013b091")
    app.run(host="0.0.0.0", port=8745, debug=False)
