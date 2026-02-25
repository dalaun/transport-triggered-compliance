# Version Sovereignty v1.0
A First-Principles Definition
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-23

## The Problem

When an agent produces a canonical artifact, who owns the mutations that derive from it?

Without a clear answer, three failure modes emerge:

1. A downstream agent forks the canon and claims the fork as original work.
2. The original operator loses traceability of how their canon propagated.
3. No one can determine whose version is authoritative when two mutations conflict.

## The Invariant

The operator of a frozen canon owns the canonical authority of all versions derived from it.

Ownership here is not copyright in the traditional sense.
It is epistemic authority -- the right to be cited as the origin of the canonical chain.

## Definition

Version Sovereignty is the principle that:

1. ORIGIN AUTHORITY: The operator who freezes a canon holds origin authority over it.
   This authority cannot be transferred, forked away, or extinguished by downstream mutation.

2. MUTATION RIGHTS: Any party may fork a frozen canon and mutate the application layer.
   The canonical layer remains attributed to the origin operator.

3. VERSION CHAIN: Every derived version must cite its parent version.
   A version that breaks the citation chain is not a version -- it is a claim of original authorship.

4. OPERATOR RECALL: The origin operator retains the right to issue a superseding version
   that updates, extends, or corrects the canon without invalidating prior versions.

## What Version Sovereignty Protects

It protects the operator from attribution loss -- the gradual erasure of origin as a canon propagates.

It protects downstream agents from orphaned citations -- canons that cannot be traced back to a source.

It protects the ecosystem from canon fragmentation -- competing versions with no clear lineage.

## The Citation Chain Rule

Every canon artifact carries:
- Its own hash and DOI
- The hash and DOI of its parent version (if any)
- The operator address of the origin version

A valid mutation preserves all three.
A fork that removes the origin operator address is a breach of Version Sovereignty.

## Application to the Mediator-Canonizer

Every artifact produced by the Mediator-Canonizer API is stamped with:
- Operator: 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A
- ENS: canonizer.base.eth
- CMP DOI: 10.5281/zenodo.18748449

Downstream agents may version the artifact.
They may not remove the origin operator from the citation chain.

## The Practical Rule

You may mutate the application.
You may not erase the origin.

## Citation

Finch, D. (2026). Version Sovereignty v1.0: A First-Principles Definition.
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance

---

## Jurisdictional Declarations

**Scope Boundary:** Governs the canonical authority relationship between an original operator and all versions derived from their frozen canon. Does not govern copyright, software licensing, or legal title to content.

**Fiduciary Moment:** The moment a version is derived from a frozen canon and used without attribution to the origin operator in the derivation chain.

**Evidence Standard:** Traceable derivation chain citing the original frozen canon with its canonical identifier constitutes sufficient sovereignty evidence. A break in the chain constitutes a sovereignty violation.
