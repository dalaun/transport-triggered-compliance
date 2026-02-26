"""
challenge_endpoints.py
Canon Challenge protocol — appended to api.py

POST /canon/challenge          — submit a challenge to a frozen canon
GET  /canon/challenge/<id>     — challenge status and result
GET  /canon/challenges         — list all challenges (history + outcomes)
"""

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
