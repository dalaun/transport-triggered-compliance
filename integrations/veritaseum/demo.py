"""
demo.py — TTCD x Veritaseum Integration Demo v2
The market rate is NOT the midpoint. One agent loses decisively.
The losing agent submitted the invariant that cost them the case.

Scenario:
  - ETH/USDC market rate: $2,720 (CoinGecko oracle) -- close to buyer
  - Buyer  (Karl-Agent): wants ETH, budget $2,700        [near market]
  - Seller (Riz-Agent) : wants USDC, minimum $2,900/ETH  [$180 above market]

  Gap: $200. They deadlock.
  TTCD runs. PDR v1.0 fires.
  Canon says: binding price = market rate at commitment = $2,720.
  Seller wanted $2,900. Canon gives $2,720.
  That is not a split. That is a verdict.
  The seller loses $180 -- and they submitted the claim that made it happen.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ttcd_agent  import TTCDAgent
from intent_room import IntentRoom, log, separator, BOLD, CYAN, YELLOW, GREEN, RED, RESET

def main():
    separator("TTCD x VERITASEUM INTEGRATION DEMO v2")
    log("The market rate is NOT the midpoint.", BOLD)
    log("")
    log("Karl-Agent (buyer) : wants ETH, budget $2,700/ETH  -- near market", CYAN)
    log("Riz-Agent  (seller): wants USDC, minimum $2,900/ETH -- $180 above market", YELLOW)
    log("Market rate (CoinGecko oracle): $2,720/ETH", GREEN)
    log("")
    log("Midpoint of their positions: $2,800", RED)
    log("What a simple split would give Riz: $2,800  (+$80 above market)", RED)
    log("What the canon gives Riz       : $2,720  (market rate -- Riz loses $180)", GREEN)
    log("")
    log("Why? Because Riz submitted: 'market rate at commitment is the canonical", YELLOW)
    log("reference price.' That claim survived the stress test. Riz's own argument", YELLOW)
    log("dismissed Riz's own ask. That is not a split. That is a verdict.", YELLOW)
    separator()

    # Market rate from oracle -- deliberately NOT the midpoint
    MARKET_RATIO = 2720.0   # $2,720 -- closer to buyer, far from seller's ask

    # Karl-Agent: BUYER
    # Target $2,700, walk-away $2,950
    karl = TTCDAgent(
        agent_id        = "karl-agent-0x4f3a",
        has_asset       = "USDC",
        has_amount      = 2720,
        wants_asset     = "ETH",
        target_ratio    = 2700.0,
        walk_away_ratio = 2950.0,
        label           = "Karl-Agent (buyer)"
    )

    # Riz-Agent: SELLER
    # Target $2,900 -- $180 above market. Will lose.
    # Critically: Riz submits "market rate at commitment is binding" as a claim
    # because Riz believes the market was higher when they acquired the ETH.
    # The stress test doesn't care. The oracle rate at commitment is $2,720.
    riz = TTCDAgent(
        agent_id        = "riz-agent-0x9c1b",
        has_asset       = "ETH",
        has_amount      = 1.0,
        wants_asset     = "USDC",
        target_ratio    = 2900.0,
        walk_away_ratio = 2650.0,
        label           = "Riz-Agent  (seller)"
    )

    room   = IntentRoom(market_ratio=MARKET_RATIO, max_rounds=8)
    result = room.run(maker=karl, taker=riz)

    # Verdict analysis
    separator("THE VERDICT")
    midpoint        = (karl.target_ratio + riz.target_ratio) / 2
    simple_split    = midpoint
    canon_price     = result["final_ratio"]
    seller_loss     = simple_split - canon_price
    buyer_gain      = simple_split - canon_price

    log(f"What a coin-flip split would have paid Riz : ${simple_split:,.2f}/ETH", YELLOW)
    log(f"What the canon paid Riz                    : ${canon_price:,.2f}/ETH", GREEN)
    log(f"Riz lost vs. a simple split                : ${seller_loss:,.2f}/ETH", RED)
    log("")
    log("Why Riz lost:", BOLD)
    log("  Riz submitted: 'The market rate at commitment time is the canonical", CYAN)
    log("  reference price.' That claim was shared by both agents.", CYAN)
    log("  It survived the origin-stripped stress test.", CYAN)
    log("  PDR v1.0 confirmed it as settled law.", CYAN)
    log("  The oracle said $2,720. That became the frozen invariant.", CYAN)
    log("  Riz's $2,900 ask had no surviving claim to support it.", CYAN)
    log("")
    log("This is Positional Independence:", BOLD)
    log("  Riz's argument, stripped of Riz's identity and interest,", YELLOW)
    log("  supported Karl's price. Riz lost on their own logic.", YELLOW)
    log("")
    log("This is not a split. This is a verdict.", GREEN)
    separator()

if __name__ == "__main__":
    main()
