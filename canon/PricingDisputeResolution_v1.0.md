# Canon: Pricing Dispute Resolution (PDR) v1.0
**Status:** FROZEN  
**DOI:** 10.5281/zenodo.18765787  
**Version:** 1.0  
**Domain:** Agent commerce, dynamic pricing, rate disputes  
**Canonized:** 2026-02-25  

## Core Invariant
The binding price in an agent transaction is the price that was unambiguously machine-readable at the moment the consuming agent committed resources to the transaction, not the price at execution or settlement.

## Invariants
1. Price attaches at commitment, not at execution.
2. A price change that occurs after a consuming agent has committed resources to a transaction is not binding on that transaction.
3. Ambiguous pricing (multiple valid interpretations of the same price signal) defaults to the interpretation most favorable to the consuming agent.
4. Dynamic pricing is binding only when the pricing function itself was disclosed and machine-readable before commitment.
5. A price quoted by an agent in a negotiation round is binding on that agent for the duration of that round.

## Jurisdictional Declarations
**Scope Boundary:** Governs the determination of binding price in disputes between agents where price changed between quote, commitment, and execution. Does not govern refund terms, settlement mechanics, or currency conversion rates.

**Fiduciary Moment:** The moment a consuming agent allocates resources (compute, capital, downstream commitments) in reliance on a price signal. At that moment the price is locked for that transaction.

**Evidence Standard:** The binding price is evidenced by the machine-readable price signal present in the provider's API response at the timestamp of the consuming agent's resource commitment event, as recorded in the consuming agent's decision log.

## Stress Test
Tested against: provider claiming price updated before settlement so new price applies; consumer claiming quoted price applies regardless of elapsed time; provider claiming dynamic pricing clause overrides commitment-time price. Only the commitment-time machine-readable price survived all attacks.
