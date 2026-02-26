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
PRICE_USDC = 50000  # $0.05 in USDC (6 decimals)
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
        "version": "1.2.0",
        "cmp_doi": "10.5281/zenodo.18732820",
        "ontology_doi": "10.5281/zenodo.18748449",
        "contract": CONTRACT,
        "network": "Base mainnet (8453)",
        "price": "$0.05 USDC per mediation",
        "endpoints": {
            "POST /mediate": "Submit positions for canonization (requires x402 payment)",
            "POST /mediate/free": "Free mediation (no on-chain registration)",
            "GET /health": "Service health check",
            "GET /recall": "Pre-flight citation check: surfaces prior frozen canons",
            "POST /a2a/dispute": "Open A2A dispute session",
            "POST /a2a/respond/{id}": "Peer agent responds; triggers mediation",
            "GET /a2a/dispute/{id}": "Dispute status",
            "GET /a2a/disputes": "List open disputes",
            "POST /canon/challenge": "Challenge a frozen canon on its merits (new evidence / scope misapplication)",
            "GET /canon/challenge/{id}": "Challenge status and result",
            "GET /canon/challenges": "Full challenge history — upheld, failed, blocked"
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



import uuid, time
import dispute_store as _ds
import challenge_store as _cs

A2A_TTL = 3600   # disputes expire after 1 hour

def _prune_disputes():
    _ds.prune(A2A_TTL)

def _disputes_get(did):
    return _ds.get(did)

def _disputes_put(did, dispute):
    _ds.put(did, dispute)

def _disputes_list_open():
    return _ds.list_open()

# ─── A2A endpoints ────────────────────────────────────────────────────────────

@app.route("/a2a/dispute", methods=["POST"])
def a2a_initiate():
    """
    Initiating agent opens a dispute session.

    Request body:
    {
      "agent_id": "string",          # caller identity
      "domain": "string",            # domain to mediate
      "claims": ["..."],             # initiating agent position
      "scope_boundary": "string",    # optional — helps downstream freeze
      "fiduciary_moment": "string",
      "evidence_standard": "string",
      "metadata": {}
    }

    Returns:
    {
      "dispute_id": "uuid",
      "status": "open",
      "awaiting": "peer_response",
      "respond_url": "/a2a/respond/{dispute_id}"
    }
    """
    _prune_disputes()
    data = request.get_json() or {}
    agent_id = data.get("agent_id", "agent-unknown")
    domain = data.get("domain", "")
    claims = data.get("claims", [])

    if not domain or not claims:
        return jsonify({"error": "domain and claims required"}), 400

    dispute_id = str(uuid.uuid4())[:8]
    _disputes_put(dispute_id, {
        "created": time.time(),
        "domain": domain,
        "scope_boundary": data.get("scope_boundary", ""),
        "fiduciary_moment": data.get("fiduciary_moment", ""),
        "evidence_standard": data.get("evidence_standard", ""),
        "metadata": data.get("metadata", {}),
        "positions": [{"agent": agent_id, "claims": claims}],
        "status": "open"
    })

    return jsonify({
        "schema": "A2A/1.0",
        "dispute_id": dispute_id,
        "status": "open",
        "awaiting": "peer_response",
        "domain": domain,
        "respond_url": f"/a2a/respond/{dispute_id}",
        "expires_in": A2A_TTL,
        "cmp_doi": "10.5281/zenodo.18732820"
    }), 201


@app.route("/a2a/respond/<dispute_id>", methods=["POST"])
def a2a_respond(dispute_id):
    """
    Peer agent joins an open dispute and triggers mediation.

    Request body:
    {
      "agent_id": "string",
      "claims": ["..."]
    }

    Returns: full mediation result (same as /mediate/free) once processed.
    """
    dispute = _disputes_get(dispute_id)
    if dispute is None:
        return jsonify({"error": "dispute not found or expired"}), 404
    if dispute["status"] != "open":
        return jsonify({"error": "dispute already resolved", "status": dispute["status"]}), 409

    data = request.get_json() or {}
    agent_id = data.get("agent_id", "peer-agent")
    claims = data.get("claims", [])

    if not claims:
        return jsonify({"error": "claims required"}), 400

    # Check not same agent responding to own dispute
    if any(p["agent"] == agent_id for p in dispute["positions"]):
        return jsonify({"error": "same agent cannot be both parties"}), 409

    dispute["positions"].append({"agent": agent_id, "claims": claims})
    dispute["status"] = "mediating"
    _disputes_put(dispute_id, dispute)

    # Build mediation payload and run CMP
    input_data = {
        "domain": dispute["domain"],
        "type": "A",
        "positions": dispute["positions"],
        "scope_boundary": dispute.get("scope_boundary", ""),
        "fiduciary_moment": dispute.get("fiduciary_moment", ""),
        "evidence_standard": dispute.get("evidence_standard", ""),
        "metadata": {**dispute.get("metadata", {}), "a2a_dispute_id": dispute_id}
    }

    try:
        result = mediate(input_data)
        dispute["status"] = "resolved"
        dispute["result"] = result["citation"]
        _disputes_put(dispute_id, dispute)

        result["a2a"] = {
            "schema": "A2A/1.0",
            "dispute_id": dispute_id,
            "parties": [p["agent"] for p in dispute["positions"]],
            "status": "resolved"
        }
        return jsonify(result), 200

    except Exception as e:
        dispute["status"] = "error"
        _disputes_put(dispute_id, dispute)
        return jsonify({"error": str(e)}), 500


@app.route("/a2a/dispute/<dispute_id>", methods=["GET"])
def a2a_status(dispute_id):
    """Check status of an open or resolved dispute."""
    dispute = _disputes_get(dispute_id)
    if dispute is None:
        return jsonify({"error": "not found"}), 404
    resp = {
        "schema": "A2A/1.0",
        "dispute_id": dispute_id,
        "domain": dispute["domain"],
        "status": dispute["status"],
        "parties": [p["agent"] for p in dispute["positions"]],
        "created": dispute["created"],
        "expires_in": max(0, A2A_TTL - (time.time() - dispute["created"]))
    }
    if "result" in dispute:
        resp["result"] = dispute["result"]
    return jsonify(resp), 200


@app.route("/a2a/disputes", methods=["GET"])
def a2a_list():
    """List open disputes (for peer agents to discover and respond)."""
    _prune_disputes()
    open_disputes = [
        {
            "dispute_id": d["id"],
            "domain": d["domain"],
            "status": d["status"],
            "parties": len(d["positions"]),
            "awaiting": "peer" if d["status"] == "open" else None,
            "respond_url": f"/a2a/respond/{d['id']}",
            "expires_in": max(0, A2A_TTL - (time.time() - d["created"]))
        }
        for d in _disputes_list_open()
    ]
    return jsonify({"schema": "A2A/1.0", "open_disputes": open_disputes}), 200


@app.route("/recall", methods=["GET", "POST"])
def recall_endpoint():
    """Pre-flight citation check. Returns prior frozen canons overlapping the domain."""
    try:
        if request.method == "POST":
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
            data["claims"] = request.args.getlist("claims")

        domain = data.get("domain", "")
        claims = data.get("claims", [])
        if isinstance(claims, str):
            claims = [claims]

        import importlib.util
        spec = importlib.util.spec_from_file_location("citation_recall",
            "/root/ttcd-pub/mediator/citation_recall.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.recall(domain, claims)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

import uuid, time
import challenge_store as _cs

# ── Challenge endpoints ───────────────────────────────────────────────────────

@app.route("/canon/challenge", methods=["POST"])
def canon_challenge():
    """
    Submit a merit-based challenge to a frozen canon invariant.

    Request body:
    {
      "challenger_id":    "agent-id",
      "canon_hash":       "sha256 hash of the canon being challenged",
      "canon_domain":     "domain of the original canon (for recall)",
      "grounds":          "specific factual basis: new evidence / scope misapplication / oracle error",
      "new_evidence":     "the new evidence not available at original mediation",
      "scope_argument":   "optional: argue the canon was applied outside its declared scope",
      "challenger_claims": ["claim1", "claim2", ...]
    }

    Valid grounds:   new evidence, oracle error, scope misapplication
    Invalid grounds: positional arguments (what you intended, who submitted what)
                     — blocked by Positional Independence before CMP runs

    Returns:
    {
      "challenge_id": "...",
      "validity":     "ACCEPTED" | "BLOCKED",
      "validity_reason": "...",
      "cmp_result":   { ... },    # if ACCEPTED
      "outcome":      "UPHELD" | "FAILED" | "BLOCKED"
    }
    """
    data           = request.get_json() or {}
    challenger_id  = data.get("challenger_id", "agent-unknown")
    canon_hash     = data.get("canon_hash", "")
    canon_domain   = data.get("canon_domain", "")
    grounds        = data.get("grounds", "")
    new_evidence   = data.get("new_evidence", "")
    scope_argument = data.get("scope_argument", "")
    claims         = data.get("challenger_claims", [])

    if not canon_hash or not grounds:
        return jsonify({"error": "canon_hash and grounds are required"}), 400

    challenge_id = str(uuid.uuid4())[:8]
    challenge = {
        "id":               challenge_id,
        "created":          time.time(),
        "challenger_id":    challenger_id,
        "canon_hash":       canon_hash,
        "canon_domain":     canon_domain,
        "grounds":          grounds,
        "new_evidence":     new_evidence,
        "scope_argument":   scope_argument,
        "challenger_claims": claims,
        "status":           "validating"
    }

    # ── Step 1: Positional Independence gate ─────────────────────────────────
    valid, reason = _cs.validate_grounds(grounds, claims)
    challenge["validity"]        = "ACCEPTED" if valid else "BLOCKED"
    challenge["validity_reason"] = reason

    if not valid:
        challenge["status"]  = "blocked"
        challenge["outcome"] = "BLOCKED"
        _cs.put(challenge_id, challenge)
        return jsonify({
            "schema":          "CanonChallenge/1.0",
            "challenge_id":    challenge_id,
            "validity":        "BLOCKED",
            "validity_reason": reason,
            "outcome":         "BLOCKED",
            "note": (
                "Your challenge was blocked before CMP ran. "
                "Positional Independence requires you engage the invariant "
                "on its merits. Resubmit with factual grounds only."
            )
        }), 400

    # ── Step 2: Reconstruct canon defense from original invariants ────────────
    # The canon defends itself: its own invariants become Position 2.
    # Challenger's new evidence is Position 1.
    # The original canon is automatically surfaced as prior art.

    defense_claims = [
        f"The original canon (hash: {canon_hash[:16]}...) was produced through "
        f"adversarial stress testing and survived origin-stripped evaluation.",
        "A canon that has been frozen cannot be overturned without new evidence "
        "that was unavailable at the time of the original mediation.",
        "The scope boundary of the original canon is precisely defined and was "
        "not exceeded in the mediation that produced it.",
        "The oracle data used to anchor the canon's invariant was the best "
        "available machine-readable price signal at the moment of commitment."
    ]

    challenge_input = {
        "domain":          f"canon challenge: {canon_domain}",
        "type":            "A",
        "positions": [
            {
                "agent":   challenger_id,
                "claims":  claims + ([new_evidence] if new_evidence else [])
            },
            {
                "agent":   f"canon-defense-{canon_hash[:8]}",
                "claims":  defense_claims
            }
        ],
        "scope_boundary":   (
            scope_argument if scope_argument
            else f"Governs the validity of canon {canon_hash[:16]}... in domain: {canon_domain}"
        ),
        "fiduciary_moment": (
            "The moment the challenge produces a FROZEN invariant that "
            "contradicts the original canon's core invariant."
        ),
        "evidence_standard": (
            "A challenge is upheld when the challenger's new evidence produces "
            "a shared invariant that contradicts the original canon and survives "
            "the same origin-stripped stress test."
        ),
        "metadata": {
            "challenge_id":  challenge_id,
            "canon_hash":    canon_hash,
            "challenge_type": "canon_challenge"
        }
    }

    # ── Step 3: Run CMP ───────────────────────────────────────────────────────
    try:
        challenge["status"] = "running_cmp"
        _cs.put(challenge_id, challenge)

        result = mediate(challenge_input)
        canon  = result.get("canon", {})

        challenge["result_canon_hash"]   = canon.get("hash")
        challenge["result_canon_status"] = canon.get("status")

        # ── Step 4: Determine outcome ─────────────────────────────────────────
        # UPHELD: CMP produced FROZEN — challenger's evidence was strong enough
        # FAILED: CMP produced DRAFT — original canon stands
        if canon.get("status") == "FROZEN" and canon.get("invariants"):
            challenge["outcome"] = "UPHELD"
            challenge["status"]  = "resolved"
            outcome_note = (
                "Challenge UPHELD. A new FROZEN canon has been produced from "
                "your new evidence. The original canon is now superseded. "
                "Cite the new canon hash in all future disputes in this domain."
            )
        else:
            challenge["outcome"] = "FAILED"
            challenge["status"]  = "resolved"
            outcome_note = (
                "Challenge FAILED. Your new evidence did not produce a "
                "FROZEN invariant that contradicts the original canon. "
                "The original canon stands. This failed challenge is now "
                "part of the permanent record."
            )

        _cs.put(challenge_id, challenge)

        return jsonify({
            "schema":          "CanonChallenge/1.0",
            "challenge_id":    challenge_id,
            "validity":        "ACCEPTED",
            "validity_reason": reason,
            "outcome":         challenge["outcome"],
            "note":            outcome_note,
            "original_canon":  canon_hash,
            "cmp_result":      result,
            "prior_art":       result.get("prior_art", {})
        }), 200

    except Exception as e:
        challenge["status"]  = "error"
        challenge["outcome"] = "ERROR"
        _cs.put(challenge_id, challenge)
        return jsonify({"error": str(e), "challenge_id": challenge_id}), 500


@app.route("/canon/challenge/<challenge_id>", methods=["GET"])
def canon_challenge_status(challenge_id):
    """Retrieve a challenge by ID."""
    ch = _cs.get(challenge_id)
    if not ch:
        return jsonify({"error": "not found"}), 404
    return jsonify({"schema": "CanonChallenge/1.0", **ch}), 200


@app.route("/canon/challenges", methods=["GET"])
def canon_challenges_list():
    """List all canon challenges — history, outcomes, blocked attempts."""
    challenges = _cs.list_all()
    summary = {
        "total":   len(challenges),
        "upheld":  sum(1 for c in challenges if c.get("outcome") == "UPHELD"),
        "failed":  sum(1 for c in challenges if c.get("outcome") == "FAILED"),
        "blocked": sum(1 for c in challenges if c.get("outcome") == "BLOCKED"),
    }
    return jsonify({
        "schema":     "CanonChallenge/1.0",
        "summary":    summary,
        "challenges": challenges
    }), 200


if __name__ == "__main__":
    print("Mediator-Canonizer API v1.0 — x402 enabled")
    print(f"Price: $1.00 USDC per mediation")
    print(f"Operator: {OPERATOR}")
    print(f"Contract: {CONTRACT}")
    app.run(host="0.0.0.0", port=8745, debug=False)
