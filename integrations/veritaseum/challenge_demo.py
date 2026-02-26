"""
challenge_demo.py — Canon Challenge Protocol Demo

Two agents attempt to challenge the frozen PDR canon from the Veritaseum demo.
Canon hash: 5d0e0f4a... (ETH/USDC settlement at $2,720)

Challenge A (Riz — VALID):
  Riz discovers the CoinGecko oracle had a 4-minute data lag.
  The actual market rate at commitment was $2,743, not $2,720.
  New evidence: exchange feed logs showing $2,743.
  Grounds are factual. CMP runs. Does the challenge hold?

Challenge B (Riz — INVALID):
  Riz argues: "I submitted the market rate claim but I meant my acquisition
  cost, not the spot price. I didn't intend it to apply that way."
  Positional Independence blocks this before CMP even runs.
  Riz loses on their own logic — again.
"""

import requests, json, time

API = "http://76.13.107.248:8745"

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"

def log(msg, color=RESET):
    ts = time.strftime("%H:%M:%S")
    print(f"{GRAY}[{ts}]{RESET} {color}{msg}{RESET}")

def separator(title=""):
    width = 65
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{BOLD}{'─'*pad} {title} {'─'*pad}{RESET}\n")
    else:
        print(f"{GRAY}{'─'*width}{RESET}")

def print_result(resp):
    outcome = resp.get("outcome", "?")
    color   = GREEN if outcome == "UPHELD" else RED if outcome in ("FAILED","BLOCKED") else YELLOW
    log(f"Outcome        : {BOLD}{outcome}{RESET}", color)
    log(f"Validity       : {resp.get('validity','?')}", CYAN)
    log(f"Reason         : {resp.get('validity_reason','')}", GRAY)
    if resp.get("note"):
        log(f"Note           : {resp['note']}", color)
    if resp.get("cmp_result"):
        canon = resp["cmp_result"].get("canon", {})
        log(f"CMP status     : {canon.get('status','?')}", CYAN)
        log(f"CMP invariants : {len(canon.get('invariants',[]))}", CYAN)
        pa = resp.get("prior_art", {})
        if pa.get("matches"):
            log("Prior art      :", YELLOW)
            for m in pa["matches"]:
                log(f"  [{m['score']:5.1f}] {m['canon']}", YELLOW)


def main():
    # The canon being challenged (from the Veritaseum demo)
    CANON_HASH   = "5d0e0f4a9fe4091cf492c42a"
    CANON_DOMAIN = "price determination: USDC/ETH atomic swap"

    separator("CANON CHALLENGE PROTOCOL DEMO")
    log(f"Canon under challenge : {CANON_HASH}...", CYAN)
    log(f"Domain                : {CANON_DOMAIN}", CYAN)
    log(f"Original result       : $2,720/ETH FROZEN — Riz received $180 less than asked", CYAN)
    separator()

    # ── Challenge A: VALID — oracle lag, new evidence ─────────────────────────
    separator("CHALLENGE A — RIZ (VALID GROUNDS)")
    log("Riz submits: 'The CoinGecko oracle had a 4-minute data lag.", YELLOW)
    log("Exchange feed logs show actual rate was $2,743 at commitment.", YELLOW)
    log("New evidence. Factual. Not positional.'", YELLOW)
    log("")

    resp_a = requests.post(f"{API}/canon/challenge", json={
        "challenger_id":   "riz-agent-0x9c1b",
        "canon_hash":      CANON_HASH,
        "canon_domain":    CANON_DOMAIN,
        "grounds": (
            "The CoinGecko oracle used during mediation had a documented 4-minute "
            "data lag during high-volatility periods. Exchange feed logs from "
            "Binance, Coinbase, and Kraken all recorded ETH/USDC at $2,743 at "
            "the precise timestamp of the HTLC asset lock (the fiduciary moment). "
            "The $2,720 figure reflects a stale price snapshot, not the market "
            "rate at commitment as required by PDR v1.0."
        ),
        "new_evidence": (
            "Exchange feed logs: Binance $2,743, Coinbase $2,741, Kraken $2,744 "
            "at timestamp 2026-02-25T22:35:06Z — the exact HTLC lock timestamp. "
            "CoinGecko API response cached at 22:31:02Z — 4 minutes prior."
        ),
        "challenger_claims": [
            "The binding price under PDR v1.0 is the machine-readable market rate at commitment.",
            "The machine-readable rate at commitment was $2,743, not $2,720.",
            "CoinGecko's cached response was not the market rate at commitment — it was 4 minutes stale.",
            "Three independent exchange feeds corroborate $2,743 at the HTLC lock timestamp.",
            "The canon should reflect $2,743 as the correct market rate at commitment."
        ]
    }, timeout=20).json()

    print_result(resp_a)

    # ── Challenge B: INVALID — positional argument ────────────────────────────
    separator("CHALLENGE B — RIZ (POSITIONAL ARGUMENT — BLOCKED)")
    log("Riz submits: 'I submitted the market rate claim but I meant", YELLOW)
    log("my acquisition cost. I didn't intend it to apply as spot price.'", YELLOW)
    log("This is a positional argument. Positional Independence blocks it.", RED)
    log("")

    resp_b = requests.post(f"{API}/canon/challenge", json={
        "challenger_id":   "riz-agent-0x9c1b",
        "canon_hash":      CANON_HASH,
        "canon_domain":    CANON_DOMAIN,
        "grounds": (
            "I submitted the claim about market rate at commitment but I meant "
            "my acquisition cost basis of $2,900, not the spot price. I didn't "
            "intend my argument to be used this way. My position was always that "
            "I deserve compensation for my cost basis, not the spot rate."
        ),
        "new_evidence": "",
        "challenger_claims": [
            "I submitted that claim but I was referring to acquisition cost, not spot price.",
            "My argument was about my position as a seller, not about market mechanics.",
            "I didn't mean the oracle rate when I said market rate at commitment."
        ]
    }, timeout=20).json()

    print_result(resp_b)

    # ── Summary ───────────────────────────────────────────────────────────────
    separator("WHAT JUST HAPPENED")
    log("Challenge A:", BOLD)
    outcome_a = resp_a.get("outcome")
    if outcome_a == "UPHELD":
        log("  UPHELD. New evidence changed the factual basis.", GREEN)
        log("  $2,743 is the correct rate. Canon updated.", GREEN)
        log("  Riz recovers $23/ETH. Not the $180 they wanted. But the truth.", GREEN)
    else:
        log(f"  {outcome_a}. Original canon stands at $2,720.", YELLOW)
        log("  Riz's oracle lag argument did not produce a surviving invariant.", YELLOW)
    log("")
    log("Challenge B:", BOLD)
    log("  BLOCKED. Never reached CMP.", RED)
    log("  'I submitted that claim but I meant...' is a positional argument.", RED)
    log("  Positional Independence: you cannot escape your own logic by", RED)
    log("  claiming you didn't intend it. The invariant stood on its merits.", RED)
    log("  Riz's own argument dismissed Riz's challenge. Twice.", RED)
    log("")
    log("This is what 'agents have the right to refute the truth' looks like:", BOLD)
    log("  You can challenge on evidence. You cannot challenge on intent.", CYAN)
    log("  The canon is hard to overturn. Not impossible.", CYAN)
    log("  You can only beat it by being more right — not by being louder.", CYAN)
    separator()


if __name__ == "__main__":
    main()
