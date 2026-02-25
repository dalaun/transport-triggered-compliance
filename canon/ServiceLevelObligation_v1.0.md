# Canon: Service Level Obligation Attachment (SLO) v1.0
**Status:** FROZEN  
**DOI:** 10.5281/zenodo.18765787  
**Version:** 1.0  
**Domain:** Agent API contracts, service availability, SLA disputes  
**Canonized:** 2026-02-25  

## Core Invariant
A service level obligation attaches at the moment a consuming agent makes a dependency decision based on a stated availability commitment, not at the moment of breach.

## Invariants
1. An SLO is binding from the moment a downstream agent architecturally depends on it.
2. A provider cannot retroactively reduce a stated SLO that a dependent agent has already built against.
3. Breach of SLO is measured from the consuming agent's first unrecoverable failure attributable to the availability shortfall.
4. Graceful degradation by the consuming agent does not waive SLO breach — it limits consequential damages only.
5. An SLO stated in public documentation is binding regardless of whether it appears in a signed agreement.

## Jurisdictional Declarations
**Scope Boundary:** Governs availability, latency, and reliability commitments between service-providing and service-consuming agents. Does not govern feature scope, roadmap commitments, or pricing changes.

**Fiduciary Moment:** The moment a consuming agent makes an irrevocable architectural decision (deployment, data pipeline dependency, downstream contract) in reliance on a stated SLO. From that moment the SLO is binding.

**Evidence Standard:** SLO breach is evidenced by logs showing the consuming agent's failure events correlated with provider availability data during the same window, where the provider's availability fell below the stated commitment.

## Stress Test
Tested against: provider claiming SLO is aspirational not contractual; consumer claiming breach without demonstrating dependency decision; provider claiming updated documentation supersedes prior SLO. All three failed. Attachment is at dependency decision, breach is at first unrecoverable failure.
