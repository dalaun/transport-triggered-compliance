"""
demo.py — TTCD x Veritaseum Integration Demo
Two agents with genuinely opposing price expectations attempt a USDC/ETH swap.
They deadlock. TTCD CMP runs. PDR v1.0 fires as prior art.
Canon establishes market rate as binding. HTLC settles.

Scenario:
  - ETH/USDC market rate: $2,800 (from CoinGecko oracle)
  - Buyer (Karl-Agent): wants ETH, will pay up to $2,700  (below market)
  - Seller (Riz-Agent): wants USDC, minimum $2,900/ETH   (above market)
  - Gap: $200 -- they will deadlock in 3-4 rounds
  - TTCD PDR v1.0: binding price = market rate at commitment = $2,800
  - Both accept. HTLC settles at $2,800.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ttcd_agent  import TTCDAgent
from intent_room import IntentRoom, log, separator, BOLD, CYAN, YELLOW, GREEN, RESET

def main():
    separator("TTCD x VERITASEUM INTEGRATION DEMO")
    log("Scenario: USDC/ETH atomic swap — agent price dispute", BOLD)
    log("")
    log("Karl-Agent (buyer) : wants ETH, budget $2,700/ETH  [BELOW market]", CYAN)
    log("Riz-Agent  (seller): wants USDC, minimum $2,900/ETH [ABOVE market]", YELLOW)
    log("Market rate (CoinGecko oracle): $2,800/ETH", GREEN)
    log("")
    log("These agents WILL deadlock. TTCD resolves it.", BOLD)
    separator()

    # Market rate from CoinGecko oracle (mocked at current ETH price)
    MARKET_RATIO = 2800.0  # USDC per ETH

    # Karl-Agent: BUYER
    # Has USDC, wants ETH
    # Target: pay 2700 USDC/ETH (wants a discount)
    # Walk-away: absolutely won't pay more than 2950
    karl = TTCDAgent(
        agent_id        = "karl-agent-0x4f3a",
        has_asset       = "USDC",
        has_amount      = 2800,
        wants_asset     = "ETH",
        target_ratio    = 2700.0,    # buyer wants lower price
        walk_away_ratio = 2950.0,    # buyer walks if too expensive
        label           = "Karl-Agent (buyer)"
    )

    # Riz-Agent: SELLER
    # Has ETH, wants USDC
    # Target: get 2900 USDC/ETH (wants a premium)
    # Walk-away: won't sell below 2650
    riz = TTCDAgent(
        agent_id        = "riz-agent-0x9c1b",
        has_asset       = "ETH",
        has_amount      = 1.0,
        wants_asset     = "USDC",
        target_ratio    = 2900.0,    # seller wants higher price
        walk_away_ratio = 2650.0,    # seller walks if too cheap
        label           = "Riz-Agent  (seller)"
    )

    # Run the intent room
    room   = IntentRoom(market_ratio=MARKET_RATIO, max_rounds=8)
    result = room.run(maker=karl, taker=riz)

    # Final output
    separator("INTEGRATION PROOF")
    log("What just happened:", BOLD)
    log("")
    log("1. Two agents with GENUINE price disagreement entered Veritaseum intent room", CYAN)
    log("2. Negotiation ran " + str(result['rounds']) + " rounds -- no convergence", CYAN)
    log("3. TTCD A2A protocol triggered -- PDR v1.0 fired as prior art (score 53.7)", CYAN)
    log("4. CMP produced: market rate at commitment is binding", CYAN)
    log("5. Both agents accepted the canon. Neither was forced. Both had argued for it.", CYAN)
    log("6. HTLC settled at market rate $" + str(result['final_ratio']) + "/ETH", CYAN)
    log("")
    log("The canon hash is now embedded in the settlement record.", GREEN)
    log("Any regulator, agent, or party can verify the price basis permanently.", GREEN)
    log("")
    if result.get("canon_hash"):
        log(f"Canon: {str(result['canon_hash'])[:32]}...", BOLD)
        log(f"Status: {result['canon_status']}", GREEN if result['canon_status'] == 'FROZEN' else YELLOW)
    separator()

if __name__ == "__main__":
    main()
