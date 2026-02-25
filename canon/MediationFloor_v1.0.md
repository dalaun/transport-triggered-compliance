# The Mediation Floor v1.0
A First-Principles Definition
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem

Two agents submit positions for canonical mediation.
They share exactly one claim: that the sky is blue.
The domain they are disputing is financial regulation.

Should the mediator freeze a canon?

The answer is no. But without a formal threshold, nothing prevents it.
A system without a floor will canonize trivialities.
Trivialized canons degrade the registry.
A degraded registry is not infrastructure. It is noise.

## The Invariant

Not every overlap is canonical.
A canon must meet a minimum threshold of substantive overlap
before it can be frozen.

## Definition

The Mediation Floor is the minimum viable overlap required
before a canonical artifact may be frozen.

The Mediation Floor has two components:

1. QUANTITATIVE FLOOR: The number of shared claims must meet a minimum threshold.
   A single shared claim is insufficient unless it is the sole claim in dispute.

2. QUALITATIVE FLOOR: The shared claims must be substantively relevant to the domain.
   Shared claims that are incidental, trivial, or domain-irrelevant do not count toward the floor.

## The Default Floor

For CMP v1.0, the default Mediation Floor is:

- Minimum 2 shared claims, OR
- Minimum 1 shared claim that is the direct subject of the dispute, AND
- At least 1 shared claim must be domain-specific (not universally true across all domains)

A claim is domain-specific if its truth value would change in a different domain.

## Below The Floor

When a mediation falls below the floor:

1. The mediator does not freeze a canon.
2. The mediator returns a BELOW_FLOOR result with the gap map.
3. The gap map identifies what additional shared ground is needed.
4. The parties may resubmit with clarified positions.

A BELOW_FLOOR result is not a failure.
It is the system correctly identifying that the dispute is not yet ready for canonization.

## The Floor As Quality Control

The Mediation Floor is the quality gate of the canon registry.

Without it, the registry fills with shallow agreements.
With it, every frozen canon represents genuine shared ground
that survived both the floor check and the adversarial stress test.

## Application

The Mediator-Canonizer API enforces the Mediation Floor automatically.
Submissions that fall below the floor receive a structured response
identifying the gap and the additional overlap required.

## Citation

Finch, D. (2026). The Mediation Floor v1.0: A First-Principles Definition.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance

---

## Jurisdictional Declarations

**Scope Boundary:** Governs the minimum viable overlap condition that must be satisfied before a canonical freeze is valid. Does not govern the quality, depth, or content of the mediated claims themselves.

**Fiduciary Moment:** The moment the overlap ratio between party positions falls below the floor threshold, triggering a mandatory gap-map before any freeze is permitted.

**Evidence Standard:** Computed overlap ratio below the declared threshold, documented in the gap map, constitutes sufficient floor-breach evidence.
