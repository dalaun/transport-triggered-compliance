"""
ttcd_agent.py — TTCD-Aware Negotiation Agent
Participates in Veritaseum-style intent rooms.
When negotiation deadlocks, triggers TTCD CMP via A2A protocol.
The canon produced becomes the binding settlement price.
"""

import requests, time, json

TTCD_API = "http://76.13.107.248:8745"

class TTCDAgent:
    def __init__(self, agent_id, has_asset, has_amount,
                 wants_asset, target_ratio, walk_away_ratio,
                 label=None):
        """
        agent_id       — unique agent identifier
        has_asset      — asset being offered  (e.g. "USDC")
        has_amount     — amount being offered (e.g. 2700)
        wants_asset    — asset being sought   (e.g. "ETH")
        target_ratio   — preferred price      (USDC per ETH)
        walk_away_ratio— absolute limit; beyond this agent walks
        """
        self.agent_id        = agent_id
        self.has_asset       = has_asset
        self.has_amount      = has_amount
        self.wants_asset     = wants_asset
        self.target_ratio    = target_ratio
        self.walk_away_ratio = walk_away_ratio
        self.label           = label or agent_id
        self.history         = []   # list of {round, from, ratio, accepted}
        self.dispute_id      = None
        self.canon           = None

    # ── Intent ──────────────────────────────────────────────────────────────

    def broadcast_intent(self):
        return {
            "agent":      self.agent_id,
            "has":        {"asset": self.has_asset,   "amount": self.has_amount},
            "wants":      self.wants_asset,
            "target":     self.target_ratio,
            "timestamp":  time.time()
        }

    # ── Negotiation ──────────────────────────────────────────────────────────

    def evaluate_offer(self, offered_ratio, round_num):
        """
        Returns (accepted: bool, counter_ratio: float)
        Buyer wants LOW ratio (cheap ETH). Seller wants HIGH ratio (expensive ETH).
        """
        self.history.append({"round": round_num, "from": "peer", "ratio": offered_ratio})

        # Check walk-away
        if self.has_asset == "USDC":  # buyer: lower is better
            if offered_ratio > self.walk_away_ratio:
                return False, None   # walk away
            if offered_ratio <= self.target_ratio:
                return True, offered_ratio
            # counter: split the difference toward target
            counter = round((offered_ratio + self.target_ratio) / 2, 2)
        else:  # seller: higher is better
            if offered_ratio < self.walk_away_ratio:
                return False, None   # walk away
            if offered_ratio >= self.target_ratio:
                return True, offered_ratio
            counter = round((offered_ratio + self.target_ratio) / 2, 2)

        self.history.append({"round": round_num, "from": self.agent_id, "ratio": counter})
        return False, counter

    def detect_deadlock(self, consecutive=3):
        """True when the last N offers from the peer are identical — no movement."""
        peer_offers = [h["ratio"] for h in self.history if h["from"] == "peer"]
        if len(peer_offers) < consecutive:
            return False
        last = peer_offers[-consecutive:]
        return len(set(last)) == 1

    # ── TTCD CMP ─────────────────────────────────────────────────────────────

    def open_dispute(self, market_ratio):
        """Initiating agent opens A2A dispute session with TTCD."""
        pair = f"{self.has_asset}/{self.wants_asset}"
        resp = requests.post(f"{TTCD_API}/a2a/dispute", json={
            "agent_id":        self.agent_id,
            "domain":          f"price determination: {pair} atomic swap",
            "claims": [
                f"The binding price for a {pair} swap is the market rate at the moment of mutual commitment, not the seller's preferred price.",
                f"An agent acting in good faith should not pay more than {self.target_ratio} {self.has_asset} per {self.wants_asset}.",
                f"The market rate at commitment time ({market_ratio} {self.has_asset}/{self.wants_asset}) is the canonical reference price.",
                "Holding out for a non-market price after commitment resources are allocated constitutes a fiduciary breach."
            ],
            "scope_boundary":    f"Governs price attachment in {pair} agent-to-agent swap negotiations using HTLC settlement.",
            "fiduciary_moment":  "The moment either agent locks assets into the HTLC escrow contract.",
            "evidence_standard": "The binding price is the machine-readable market ratio present in a public price oracle at the timestamp of the first asset lock.",
            "metadata": {
                "market_ratio":     market_ratio,
                "pair":             pair,
                "integration":      "Veritaseum P2P Intent Room",
                "htlc":             True
            }
        }, timeout=15)
        data = resp.json()
        self.dispute_id = data.get("dispute_id")
        return data

    def respond_to_dispute(self, dispute_id, market_ratio):
        """Peer agent responds to an open dispute, triggering CMP."""
        pair = f"{self.wants_asset}/{self.has_asset}"
        resp = requests.post(f"{TTCD_API}/a2a/respond/{dispute_id}", json={
            "agent_id": self.agent_id,
            "claims": [
                f"The binding price for a {pair} swap must compensate for execution risk and market movement.",
                f"A seller should not be forced below their minimum acceptable ratio of {self.target_ratio} {self.wants_asset}/{self.has_asset}.",
                f"The market rate at commitment time ({market_ratio} {self.wants_asset}/{self.has_asset}) is the canonical reference price.",
                "Enforcing a pre-commitment quoted price after market conditions change constitutes a fiduciary breach."
            ]
        }, timeout=15)
        result = resp.json()
        self.canon = result.get("canon", {})
        return result

    def accept_canon_price(self, canon_result):
        """Both agents accept the canon-produced invariant as the settlement price."""
        self.canon = canon_result.get("canon", {})
        prior_art  = canon_result.get("prior_art", {})
        return {
            "agent":     self.agent_id,
            "accepted":  True,
            "canon_hash": self.canon.get("hash"),
            "status":    self.canon.get("status"),
            "prior_art": [m["canon"] for m in prior_art.get("matches", [])]
        }
