from flask import Flask, request, jsonify
from canonizer import mediate
from x402.server import x402ResourceServerSync
from x402.http import HTTPFacilitatorClientSync
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402 import PaymentRequirements, PaymentRequirementsV1
import os, sys, json, base64
sys.path.insert(0, '/root/ttcd-pub/mediator')

app = Flask(__name__)

OPERATOR = "0xeb65c54ee09AAc48612Dc77e6d106005547dF67A"
CONTRACT = "0xf2325531264CA4Fc2cEC5D661E2200eA8013b091"
USDC_BASE = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
PRICE_USDC = 50000  # $1.00 in USDC (6 decimals)
NETWORK = "eip155:8453"

facilitator = HTTPFacilitatorClientSync({"url": "https://x402.org/facilitator"})
x402_server = x402ResourceServerSync(facilitator)
x402_server.register(NETWORK, ExactEvmServerScheme())
x402_server.initialize()

def get_payment_requirements():
    return {
        "scheme": "exact",
        "network": NETWORK,
        "maxAmountRequired": str(PRICE_USDC),
        "resource": "http://76.13.107.248:8745/mediate",
        "description": "Canonical mediation via CMP v1.0",
        "mimeType": "application/json",
        "payTo": OPERATOR,
        "maxTimeoutSeconds": 300,
        "asset": USDC_BASE,
        "outputSchema": None,
        "extra": {"cmp_doi": "10.5281/zenodo.18732820"}
    }

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
        "version": "1.1.0",
        "cmp_doi": "10.5281/zenodo.18732820",
        "ontology_doi": "10.5281/zenodo.18748449",
        "contract": CONTRACT,
        "network": "Base mainnet (8453)",
        "price": "$0.05 USDC per mediation",
        "endpoints": {
            "POST /mediate": "Submit positions for canonization (requires x402 payment)",
            "POST /mediate/free": "Free mediation (no on-chain registration)",
            "GET /health": "Service health check"
        },
        "payload_schema": {
            "domain": "string: the domain being mediated",
            "positions": "array of {agent, claims[]}, at least 2 required",
            "scope_boundary": "what this canon governs — required for FROZEN status",
            "fiduciary_moment": "the moment canonical obligation attaches — required for FROZEN status",
            "evidence_standard": "what constitutes sufficient evidence — required for FROZEN status",
            "type": "optional: A (agent) or B (human), default B",
            "metadata": "optional metadata object"
        },
        "freeze_requirements": [
            ">=2 positions with shared claims",
            "no critical gaps after stress test",
            "all 3 naming tests pass (Function, Invariant, Agreement)",
            "all 3 jurisdictional declarations non-empty"
        ]
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mediator-canonizer", "contract": CONTRACT})

@app.route("/mediate/free", methods=["POST"])
def mediate_free():
    try:
        input_data = request.get_json()
        if not input_data or len(input_data.get("positions", [])) < 2:
            return jsonify({"error": "At least two positions required"}), 400
        result = mediate(input_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/mediate", methods=["POST"])
def mediate_route():
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        requirements = get_payment_requirements()
        return jsonify({
            "error": "Payment required",
            "x402Version": 1,
            "accepts": [requirements]
        }), 402

    try:
        from x402 import PaymentPayload, PaymentPayloadV1
        payload = PaymentPayload.model_validate_json(
            base64.b64decode(payment_header).decode()
        )
        requirements_obj = PaymentRequirements(**get_payment_requirements())
        verify_result = x402_server.verify_payment(payload, requirements_obj)

        if not verify_result.is_valid:
            return jsonify({"error": "Invalid payment", "detail": str(verify_result)}), 402

        input_data = request.get_json()
        if not input_data or len(input_data.get("positions", [])) < 2:
            return jsonify({"error": "At least two positions required"}), 400

        result = mediate(input_data)
        chain_result = try_register_on_chain(result)
        if chain_result:
            result["chain"] = chain_result

        settle_result = x402_server.settle_payment(payload, requirements_obj)
        result["payment"] = {"settled": settle_result.success, "network": NETWORK}

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Mediator-Canonizer API v1.0 — x402 enabled")
    print(f"Price: $1.00 USDC per mediation")
    print(f"Operator: {OPERATOR}")
    print(f"Contract: {CONTRACT}")
    app.run(host="0.0.0.0", port=8745, debug=False)
