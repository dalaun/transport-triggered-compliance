# The Knowledge Escrow v1.0
A First-Principles Definition
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem

Two agents submit conflicting claims for canonical mediation.
The CMP process is running.
The mediation is not yet complete.

During this window, neither agent should be able to act on the disputed claims as authoritative.
The claims are contested. Their status is unresolved.

But there is no mechanism to hold them in suspension.
Either agent can continue asserting its claims as fact while the mediation runs.

## The Invariant

A disputed claim under active mediation must be held in escrow
until the mediation produces a canonical resolution.

## Definition

The Knowledge Escrow is the pre-canon state in which disputed claims
are held in suspension pending canonical resolution.

A claim enters Knowledge Escrow when:
1. Two or more agents assert conflicting versions of the claim.
2. A mediation request has been submitted to the Mediator-Canonizer.
3. The mediation process has not yet produced a frozen artifact.

## Escrow Properties

While a claim is in Knowledge Escrow:

1. SUSPENSION: Neither version of the claim may be asserted as canonical.
   An agent that asserts an escrowed claim as authoritative incurs Canonical Debt.

2. PRESERVATION: Both versions of the claim are preserved exactly as submitted.
   Neither party may alter their position while the mediation is running.

3. MEDIATOR AUTHORITY: The Mediator-Canonizer holds exclusive authority
   over the escrowed claims during the mediation window.

4. TIME LIMIT: Escrow has a maximum duration defined by the mediation timeout.
   If mediation does not complete within the timeout, the escrow expires
   and the claims revert to contested status.

## Escrow Release

Knowledge Escrow is released when:

1. FROZEN: The mediation produces a frozen canon. Shared claims are released as canonical.
   Contested claims remain contested but are documented in the gap map.

2. BELOW FLOOR: The mediation falls below the Mediation Floor.
   All claims revert to contested status. No canon is frozen.

3. TIMEOUT: The mediation window expires without resolution.
   All claims revert to contested status.

## Why Escrow Matters

Without the Knowledge Escrow, the mediation process can be gamed.

An agent could submit a mediation request while continuing to assert its position
as authoritative to downstream agents. By the time the canon is frozen,
the incorrect position has already propagated.

The Knowledge Escrow closes this window.
During mediation, the truth is genuinely suspended.
Neither party wins until the process completes.

## The Escrow as Epistemic Integrity Mechanism

The Knowledge Escrow is the operational expression of epistemic humility.

It says: we do not know which version is canonical yet.
Therefore neither version may be cited as canonical yet.
The mediation will decide. Until it does, both versions are hypothesis, not doctrine.

## Application

The Mediator-Canonizer API implements Knowledge Escrow implicitly
through the mediation timeout parameter (maxTimeoutSeconds: 300).

A future version will implement explicit escrow tracking,
allowing agents to query whether a claim is currently under active mediation.

## Citation

Finch, D. (2026). The Knowledge Escrow v1.0: A First-Principles Definition.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance