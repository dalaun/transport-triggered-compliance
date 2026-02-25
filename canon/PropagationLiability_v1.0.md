# Propagation Liability v1.0
A First-Principles Definition
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem

Agent A cites a frozen canon in its reasoning.
Agent B relies on Agent A's citation.
Agent C relies on Agent B's reasoning.
The canon turns out to be dated or flawed.

Who is liable for the downstream error?

## The Invariant

Liability in a citation chain attaches to the agent that broke the provenance.

## Definition

Propagation Liability is the epistemic responsibility incurred by an agent
when it passes a canonical claim forward without verifying its current status.

Propagation Liability distributes across the citation chain as follows:

1. ORIGIN LIABILITY: The operator who froze the canon is liable
   for the accuracy of the canon at the time of freezing.
   Origin liability does not extend to post-freezing changes in the world.

2. TRANSIT LIABILITY: An agent that passes a canon forward without checking
   its decay status incurs transit liability for any downstream errors
   caused by the dated canon.

3. TERMINAL LIABILITY: The agent that acts on a canon without independent
   verification incurs terminal liability for that action.

## The Liability Break

Liability breaks at the point where provenance was severed.

If Agent A passes a canon with full provenance and Agent B strips the provenance
before passing it to Agent C, Agent B holds full liability for C's downstream error.

If Agent A passes a canon without checking its decay status,
Agent A holds transit liability regardless of whether the canon was accurate at freezing.

## The Verification Defense

An agent eliminates transit liability by verifying the canon before passing it forward.

Verification requires:
1. Checking the on-chain registry for the canon's current status.
2. Confirming no superseding version has been published.
3. Passing the canon forward with its full provenance chain intact.

An agent that completes all three steps is not liable for downstream errors
caused by post-verification changes.

## Application

The on-chain registry at 0xf2325531264CA4Fc2cEC5D661E2200eA8013b091
provides the verification mechanism.

Any agent can call the verify() function with a canon hash
to confirm its existence, domain, status, and timestamp.

An agent that verifies before passing has exercised due diligence.
An agent that passes without verifying has not.

## Citation

Finch, D. (2026). Propagation Liability v1.0: A First-Principles Definition.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance

---

## Jurisdictional Declarations

**Scope Boundary:** Governs the epistemic responsibility of agents who transmit knowledge claims to other agents or systems. Does not govern legal liability, negligence, or contractual obligations between parties.

**Fiduciary Moment:** The moment an agent transmits a knowledge claim downstream without attributing provenance, where the receiving agent relies on that claim.

**Evidence Standard:** Documented transmission event without source citation in the transmission record constitutes sufficient propagation liability evidence.
