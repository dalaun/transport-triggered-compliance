"""
intent_room.py — Veritaseum Intent Room Simulator
Models the P2P negotiation flow from the Veritaseum platform:
  1. Maker broadcasts intent
  2. Taker discovers and negotiates
  3. Rounds of counter-offers
  4. Deadlock detection -> TTCD CMP
  5. Canon price accepted -> HTLC settlement
"""

import time, json

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


class IntentRoom:
    """Simulates the Veritaseum intent room negotiation flow."""

    def __init__(self, market_ratio, max_rounds=6):
        self.market_ratio = market_ratio
        self.max_rounds   = max_rounds
        self.log_entries  = []

    def _record(self, entry):
        self.log_entries.append(entry)

    def run(self, maker, taker):
        separator("VERITASEUM INTENT ROOM - LIVE SESSION")
        log(f"Market price:  1 {maker.wants_asset} = {self.market_ratio} {maker.has_asset}", CYAN)
        separator()

        # Step 1: Maker broadcasts intent
        separator("STEP 1 - MAKER BROADCASTS INTENT")
        intent = maker.broadcast_intent()
        log(f"{BOLD}{maker.label}{RESET} broadcasts intent", CYAN)
        log(f"  Offering : {intent['has']['amount']} {intent['has']['asset']}", CYAN)
        log(f"  Seeking  : {intent['wants']}", CYAN)
        log(f"  Target   : {maker.target_ratio} {maker.has_asset}/{maker.wants_asset}", CYAN)

        # Step 2: Taker discovers intent
        separator("STEP 2 - TAKER DISCOVERS INTENT")
        log(f"{BOLD}{taker.label}{RESET} sees the broadcast -- opening negotiation", YELLOW)
        log(f"  Taker target   : {taker.target_ratio} {taker.has_asset}/{taker.wants_asset}", YELLOW)
        log(f"  Taker walk-away: {taker.walk_away_ratio}", YELLOW)

        # Step 3: Negotiation rounds
        separator("STEP 3 - NEGOTIATION ROUNDS")
        current_offer = taker.target_ratio
        deadlock      = False
        settled       = False
        final_ratio   = None

        for rnd in range(1, self.max_rounds + 1):
            log(f"Round {rnd}: {taker.label} offers {current_offer} {taker.has_asset}/{taker.wants_asset}", YELLOW)

            accepted, counter = maker.evaluate_offer(current_offer, rnd)

            if accepted:
                log(f"  {maker.label} ACCEPTS {current_offer}", GREEN)
                settled     = True
                final_ratio = current_offer
                break

            if counter is None:
                log(f"  {maker.label} WALKS AWAY -- offer exceeds walk-away limit", RED)
                break

            log(f"  {maker.label} counters: {counter}", CYAN)

            taker_accepted, taker_counter = taker.evaluate_offer(counter, rnd)
            if taker_accepted:
                log(f"  {taker.label} ACCEPTS {counter}", GREEN)
                settled     = True
                final_ratio = counter
                break

            if taker_counter is None:
                log(f"  {taker.label} WALKS AWAY -- counter below walk-away limit", RED)
                break

            log(f"  {taker.label} counters back: {taker_counter}", YELLOW)
            current_offer = taker_counter

            if maker.detect_deadlock(consecutive=3):
                log(f"\n  !! DEADLOCK DETECTED after round {rnd} -- no convergence !!", RED)
                deadlock = True
                break

        # Step 4: Deadlock -> TTCD CMP
        canon_hash   = None
        canon_status = "N/A"

        if deadlock or (not settled):
            separator("STEP 4 - DEADLOCK: TRIGGERING TTCD CMP")
            log(f"Neither agent can agree. Invoking TTCD Canonical Mediation Protocol.", RED)
            log(f"Prior art check: PDR v1.0 governs this domain.", CYAN)
            log("")

            log(f"{maker.label} opens A2A dispute with TTCD...", CYAN)
            dispute    = maker.open_dispute(self.market_ratio)
            dispute_id = dispute.get("dispute_id")
            log(f"  Dispute ID : {dispute_id}", CYAN)
            log(f"  Status     : {dispute.get('status')}", CYAN)
            log("")

            log(f"{taker.label} responds -- CMP runs...", YELLOW)
            result = taker.respond_to_dispute(dispute_id, self.market_ratio)

            canon     = result.get("canon", {})
            prior_art = result.get("prior_art", {})
            a2a       = result.get("a2a", {})

            separator("STEP 5 - CMP RESULT")
            status_color = GREEN if canon.get("status") == "FROZEN" else YELLOW
            log(f"Status    : {BOLD}{canon.get('status')}{RESET}", status_color)
            log(f"Domain    : {canon.get('domain')}", CYAN)
            log(f"Hash      : {str(canon.get('hash',''))[:24]}...", GRAY)
            log(f"Parties   : {a2a.get('parties')}", CYAN)
            log("")

            if prior_art.get("matches"):
                log("Prior art surfaced:", YELLOW)
                for m in prior_art["matches"]:
                    log(f"  [{m['score']:5.1f}] {m['canon']}", YELLOW)
                if prior_art.get("canonical_debt_risk"):
                    log(f"\n  {prior_art.get('debt_risk_message','')}", RED)
            log("")

            log(f"Canon establishes: market rate at commitment is binding.", GREEN)
            log(f"Settlement price : {self.market_ratio} {maker.has_asset}/{maker.wants_asset}", GREEN)
            log("")

            maker_accept = maker.accept_canon_price(result)
            taker_accept = taker.accept_canon_price(result)
            log(f"{maker.label} accepts canon: {maker_accept['accepted']}", GREEN)
            log(f"{taker.label} accepts canon: {taker_accept['accepted']}", GREEN)

            final_ratio  = self.market_ratio
            canon_hash   = canon.get("hash")
            canon_status = canon.get("status")
            settled      = True

        # Step 6: HTLC Atomic Settlement
        separator("STEP 6 - HTLC ATOMIC SETTLEMENT")
        amount_out = round(maker.has_amount / final_ratio, 6)

        log(f"{maker.label} locks {maker.has_amount} {maker.has_asset} into HTLC escrow...", CYAN)
        time.sleep(0.3)
        log(f"  [OK] Maker asset locked", GREEN)

        log(f"{taker.label} locks {amount_out} {maker.wants_asset} into HTLC escrow...", YELLOW)
        time.sleep(0.3)
        log(f"  [OK] Taker asset locked", GREEN)

        log(f"Secret key revealed -- both parties claim their assets...", CYAN)
        time.sleep(0.3)
        log(f"  [OK] {maker.label} claims {amount_out} {maker.wants_asset}", GREEN)
        log(f"  [OK] {taker.label} claims {maker.has_amount} {maker.has_asset}", GREEN)

        separator("SETTLEMENT COMPLETE")
        summary = {
            "status":       "SETTLED",
            "maker":        maker.agent_id,
            "taker":        taker.agent_id,
            "pair":         f"{maker.has_asset}/{maker.wants_asset}",
            "amount_in":    maker.has_amount,
            "amount_out":   amount_out,
            "final_ratio":  final_ratio,
            "market_ratio": self.market_ratio,
            "canon_hash":   canon_hash,
            "canon_status": canon_status,
            "rounds":       len(maker.history) // 2
        }

        log(f"Pair         : {summary['pair']}", BOLD)
        log(f"Amount in    : {summary['amount_in']} {maker.has_asset}", BOLD)
        log(f"Amount out   : {summary['amount_out']} {maker.wants_asset}", BOLD)
        log(f"Final ratio  : {summary['final_ratio']}", BOLD)
        log(f"Market ratio : {summary['market_ratio']}", BOLD)
        if summary['canon_hash']:
            log(f"Canon hash   : {str(summary['canon_hash'])[:24]}...", BOLD)
        log(f"Canon status : {summary['canon_status']}", GREEN if summary['canon_status'] == 'FROZEN' else CYAN)
        log(f"Rounds taken : {summary['rounds']}", BOLD)
        separator()

        return summary
