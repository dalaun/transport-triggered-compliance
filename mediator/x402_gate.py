"""
x402_gate.py — Reusable x402 payment decorator for Flask endpoints.

Usage:
    from x402_gate import require_payment, PRICE_MEDIATE, PRICE_RESPOND, PRICE_CHALLENGE

    @app.route("/mediate", methods=["POST"])
    @require_payment(PRICE_MEDIATE, "Canonical mediation via CMP v1.0")
    def mediate_route():
        ...
        return jsonify(result), 200

The decorator:
  1. Checks X-PAYMENT header — returns 402 with requirements if absent
  2. Verifies payment via x402 facilitator
  3. Runs the handler
  4. Settles payment on success (200)
  5. Injects payment receipt into response body
"""

import base64, functools
from flask import request, jsonify
from x402.server import x402ResourceServerSync
from x402.http import HTTPFacilitatorClientSync
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402 import PaymentRequirements

# ── Price tiers (USDC, 6 decimals) ───────────────────────────────────────────
PRICE_MEDIATE   =  50000   # $0.05  — run CMP
PRICE_RESPOND   =  50000   # $0.05  — peer response triggers CMP
PRICE_CHALLENGE = 100000   # $0.10  — challenging a frozen canon costs more

# ── Network config ────────────────────────────────────────────────────────────
OPERATOR  = "0xeb65c54ee09AAc48612Dc77e6d106005547dF67A"
USDC_BASE = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
NETWORK   = "eip155:8453"
HOST      = "http://76.13.107.248:8745"
CMP_DOI   = "10.5281/zenodo.18732820"

# ── x402 server (shared instance) ─────────────────────────────────────────────
_facilitator = HTTPFacilitatorClientSync({"url": "https://x402.org/facilitator"})
x402_server  = x402ResourceServerSync(_facilitator)
x402_server.register(NETWORK, ExactEvmServerScheme())
x402_server.initialize()


def _build_requirements(price_usdc, description):
    """Build payment requirements dict for the current request path."""
    return {
        "scheme":             "exact",
        "network":            NETWORK,
        "maxAmountRequired":  str(price_usdc),
        "resource":           f"{HOST}{request.path}",
        "description":        description,
        "mimeType":           "application/json",
        "payTo":              OPERATOR,
        "maxTimeoutSeconds":  300,
        "asset":              USDC_BASE,
        "outputSchema":       None,
        "extra":              {"cmp_doi": CMP_DOI}
    }


def require_payment(price_usdc, description):
    """
    Decorator that gates a Flask endpoint behind x402 payment.
    Applies to endpoints that return (jsonify(...), status_code).
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            payment_header = request.headers.get("X-PAYMENT")
            reqs = _build_requirements(price_usdc, description)

            # ── No payment header — return 402 with requirements ──────────────
            if not payment_header:
                return jsonify({
                    "error":       "Payment required",
                    "x402Version": 1,
                    "accepts":     [reqs]
                }), 402

            # ── Verify payment ────────────────────────────────────────────────
            try:
                from x402 import PaymentPayload
                payload  = PaymentPayload.model_validate_json(
                    base64.b64decode(payment_header).decode()
                )
                reqs_obj = PaymentRequirements(**reqs)
                verify   = x402_server.verify_payment(payload, reqs_obj)

                if not verify.is_valid:
                    return jsonify({
                        "error":  "Invalid payment",
                        "detail": str(verify)
                    }), 402

                # ── Run handler ───────────────────────────────────────────────
                rv = f(*args, **kwargs)
                response, status = rv if isinstance(rv, tuple) else (rv, 200)

                # ── Settle and inject receipt on success ──────────────────────
                if status == 200:
                    settle = x402_server.settle_payment(payload, reqs_obj)
                    data   = response.get_json()
                    data["payment"] = {
                        "settled":     settle.success,
                        "network":     NETWORK,
                        "amount_usdc": price_usdc / 1_000_000
                    }
                    return jsonify(data), 200

                return response, status

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return wrapper
    return decorator
