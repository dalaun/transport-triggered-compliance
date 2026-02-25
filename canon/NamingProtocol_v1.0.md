# Naming Protocol v1.0
A Canonical Standard for Naming Canonical Artifacts
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem

A name that requires explanation is not canonical.
A name that describes an intention is not canonical.
A name that depends on shared context to be understood is not canonical.

Most frameworks are named after their authors, their origins, or their goals.
These names are contingent -- they require agreement about the author, the origin, or the goal.

A canonical name requires no such agreement.
It carries its own meaning.

## The Invariant

A canonical name is the shortest possible complete description of an invariant
such that the name and the function are inseparable.

If you can remove a word from the name without losing meaning, the name is not yet canonical.
If you can change a word without changing the function, the name is not yet canonical.
If the name describes what was intended rather than what is, the name is not yet canonical.

## The Three Tests

A name is canonical if and only if it passes all three tests:

1. THE FUNCTION TEST
   Can the function be derived from the name alone?
   A reader who has never encountered the concept should be able to infer
   what it governs from the name without reading the document.

   PASSES: Flow-Triggered Jurisdiction
   -- flow triggers, jurisdiction results. Function is in the name.

   FAILS: Regulatory Compliance Framework
   -- what triggers it? what results? the name describes a category, not a mechanism.

2. THE INVARIANT TEST
   Does the name describe what IS rather than what is intended?
   A canonical name describes a mechanism, not a goal.

   PASSES: Transport-Triggered Compliance
   -- transport triggers compliance. This is what happens, not what is hoped.

   FAILS: Sustainable Transport Policy
   -- sustainability is an intention. Policy is a goal. Neither is a mechanism.

3. THE AGREEMENT TEST
   Can the name be cited without agreement on its desirability?
   A canonical name is outcome-neutral. Its truth does not depend on
   whether the reader approves of the outcome.

   PASSES: Epistemic Custody
   -- custody exists or it does not. Agreement on whether custody is good is irrelevant.

   FAILS: Responsible AI Governance
   -- responsible and governance both embed contested value judgments.
   -- the name cannot be cited by someone who disputes what responsible means.

## The Naming Convention

Canonical names follow one of three structures:

1. MECHANISM-OUTCOME: [What triggers it]-[What results]
   Examples: Flow-Triggered Jurisdiction, Transport-Triggered Compliance
   Use when: the canon describes a causal relationship between a trigger and a consequence.

2. PROPERTY-DOMAIN: [The defining property]-[The domain it applies to]
   Examples: Hardened Mediation, Epistemic Custody, Version Sovereignty
   Use when: the canon describes a property that transforms how a domain operates.

3. SINGLE INVARIANT: [The irreducible concept]
   Examples: Canon Decay, Canonical Debt, The Mediation Floor
   Use when: the canon names a phenomenon that has no simpler decomposition.

## What Canonical Names Are Not

They are not acronyms chosen for memorability.
They are not metaphors chosen for relatability.
They are not proper nouns chosen for branding.
They are not descriptions of the author's intent.

A canonical name is a compression of the invariant it names.
Compression without loss of meaning.
Nothing added. Nothing removed.

## The Jurisdictional Declarations

Every canonical artifact must explicitly state three things.
These are not optional. They are what make a name citable without agreement.

1. SCOPE BOUNDARY: What the canon governs. What it does not govern.
   Without this, the canon can be applied to everything or nothing.

2. FIDUCIARY MOMENT: The exact instant responsibility crystallizes.
   Without this, the canon has no operational trigger.

3. EVIDENCE STANDARD: What counts as evidence that the canon applies.
   Without this, the canon cannot be adjudicated.

A name that passes the three naming tests but whose document omits any of the
three jurisdictional declarations is not a complete canon.
It is a hypothesis with a good name.

## The Linguistic Architecture

The naming protocol is a linguistic architecture because:

1. The name IS the shortest valid citation.
2. The function IS derivable from the name.
3. The canon IS inseparable from its name.

When these three conditions hold, the name propagates without the document.
An agent can cite Flow-Triggered Jurisdiction without having read FTJ v1.0
and be understood by any agent that has.

This is the propagation mechanism EIAAN v1.0 describes.
The name carries the doctrine.
The doctrine travels in the name.

## Retroactive Application

All existing canonical artifacts in this stack have been evaluated against this protocol.

The following names pass all three tests:
- Flow-Triggered Jurisdiction (Mechanism-Outcome)
- Transport-Triggered Compliance (Mechanism-Outcome)
- Anti-Circumvention Triad (Property-Domain)
- Hardened Mediation (Property-Domain)
- Epistemic Custody (Property-Domain)
- Version Sovereignty (Property-Domain)
- Canonical Debt (Single Invariant)
- Canon Decay (Single Invariant)
- The Mediation Floor (Single Invariant)
- Propagation Liability (Single Invariant)
- Stare Decisis for Agents (Single Invariant -- borrowed and scoped)
- The Knowledge Escrow (Single Invariant)
- Canonical Mediation Protocol (Mechanism-Outcome)
- Epistemic Infrastructure for Autonomous Agent Networks (Property-Domain)

## Application to New Canons

Before freezing any new canonical artifact, the name must be evaluated
against the three tests and assigned to one of the three naming structures.

A name that fails any test must be revised before the canon is frozen.
The Mediator-Canonizer API will enforce this protocol as part of the
semantic validation layer in CMP v2.0.

## Citation

Finch, D. (2026). Naming Protocol v1.0: A Canonical Standard for Naming Canonical Artifacts.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance

---

## Jurisdictional Declarations

**Scope Boundary:** Governs the canonical standard for naming canonical artifacts across the CMP framework. Does not govern naming in non-canonical contexts, informal usage, or branding decisions.

**Fiduciary Moment:** The moment a name is proposed for a canonical artifact and submitted to the Mediator-Canonizer for validation — before freeze, not after.

**Evidence Standard:** Passing all three naming tests (Function, Invariant, Agreement) as evaluated by SemanticValidator/1.0 constitutes sufficient naming validation evidence.
