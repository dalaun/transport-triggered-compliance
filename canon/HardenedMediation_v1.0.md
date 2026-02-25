# Hardened Mediation v1.0
A First-Principles Definition
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem With Mediation

Standard mediation produces a settlement.
A settlement is an agreement between parties that can be revisited, renegotiated, or abandoned.
It derives its authority from the consent of the parties, not from the logic of the resolution.
When consent is withdrawn, the settlement collapses.

For human disputes, this is acceptable.
For autonomous agents operating at machine speed across jurisdictions, it is not.

An agent cannot operate on a knowledge claim that might be renegotiated.
An agent cannot cite a source that might be withdrawn.
An agent cannot build on a foundation that consent alone holds together.

## The Invariant

Hardened mediation is mediation whose output is immutable.

The hardening is not a technical property. It is a logical one.
A canon is hardened when no party to the dispute can unilaterally alter the output.
The output derives its authority from the process, not from the parties.

## Definition

Hardened Mediation is a mediation process that satisfies all four conditions:

1. ADVERSARIAL STRESS TEST: Candidate invariants are attacked before freezing.
   A proposition that does not survive adversarial stress is not frozen.

2. PROCESS AUTHORITY: Output derives authority from the protocol, not party consent.
   Withdrawal of consent after freezing does not alter the canon.

3. IMMUTABLE OUTPUT: The frozen artifact cannot be edited, retracted, or renegotiated.
   It can only be versioned. A new version does not invalidate the prior version.

4. VERIFIABLE PROVENANCE: The artifact carries a hash, timestamp, and citable identifier.
   Any agent can verify independently without trusting the mediator.

## What Hardened Mediation Is Not

It is not arbitration. Arbitration produces a binding ruling by a third party.
Hardened mediation produces a frozen invariant extracted from the parties themselves.

It is not consensus. Consensus requires agreement from all parties.
Hardened mediation requires only shared claims -- not agreement on contested ones.

It is not a contract. A contract is enforced by law.
A hardened canon is enforced by logic -- true because it survived stress, not because a court said so.

## The Core Distinction

Soft mediation: authority from consent.
Hardened mediation: authority from process.

Soft mediation: output is a settlement.
Hardened mediation: output is a canon.

Soft mediation: revisable by agreement.
Hardened mediation: revisable only by versioning.

## The Hardening Stages

1. EXTRACTION: Shared claims identified across all positions.
2. STRESS TEST: Each shared claim attacked adversarially.
3. GAP MAP: Unresolved tensions documented, not hidden.
4. FREEZE: Surviving claims frozen with hash, timestamp, and DOI.

A claim that does not survive stress is documented as a gap, not discarded.
The gap map is part of the canon.

## Application

Implemented by CMP v1.0 (DOI: 10.5281/zenodo.18748449).
Operationalized by the Mediator-Canonizer API at http://76.13.107.248:8745.

## Citation

Finch, D. (2026). Hardened Mediation v1.0: A First-Principles Definition.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance

---

## Jurisdictional Declarations

**Scope Boundary:** Governs mediation processes whose outputs are immutable and derive authority from process rather than party consent. Does not govern soft mediation, arbitration, litigation, or consensus-based resolution.

**Fiduciary Moment:** The moment a mediation output is frozen with hash and timestamp — after which withdrawal of consent by any party does not alter the canon.

**Evidence Standard:** Frozen hash + ISO timestamp + DOI + documented adversarial stress test constitutes sufficient hardening evidence. Settlement without stress test record is not hardened.
