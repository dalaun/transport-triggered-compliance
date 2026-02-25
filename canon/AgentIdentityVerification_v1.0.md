# Canon: Agent Identity Verification (AIV) v1.0
**Status:** FROZEN  
**DOI:** 10.5281/zenodo.18765787  
**Version:** 1.0  
**Domain:** Agent authentication, identity claims, botconomy trust  
**Canonized:** 2026-02-25  

## Core Invariant
An agent's identity claim is only as strong as its weakest verifiable binding — the credential, key, or attestation that ties the claimed identity to a demonstrable action history.

## Invariants
1. Identity is not established by self-assertion — it requires a verifiable binding to prior action.
2. A compromised credential invalidates all identity claims made under that credential from the moment of compromise forward, not retroactively.
3. An agent that cannot produce a consistent action history consistent with its identity claim is not verified, regardless of credential validity.
4. Delegation of identity (agent acting on behalf of another) requires an explicit, time-bounded, scope-limited attestation from the delegating agent.
5. Identity verification is context-specific — verification for one transaction domain does not transfer to another.

## Jurisdictional Declarations
**Scope Boundary:** Governs identity verification disputes in agent-to-agent transactions where the acting agent's authority, authenticity, or delegation chain is challenged. Does not govern key management practices or credential issuance.

**Fiduciary Moment:** The moment a receiving agent accepts an identity claim and executes a consequential action in reliance on it. At that moment the receiving agent bears responsibility for verification adequacy.

**Evidence Standard:** An identity claim is verified when the claiming agent produces: (1) a valid credential from a recognized issuer, and (2) a consistent action history demonstrating prior use of that credential in the same domain, and (3) no evidence of compromise in the credential's validity window.

## Stress Test
Tested against: agent claiming identity by credential alone; agent claiming identity by history alone without valid credential; orchestrator claiming sub-agent identity covers its own actions. All three failed. Identity requires both credential and consistent action history.
