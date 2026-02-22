# Canonical Mediation Protocol (CMP)
# The Operational Protocol for Epistemic Infrastructure
# Author: Dalaun Finch
# Version: 1.0
# Status: FROZEN
# Date: 2026
# Cites: EIAAN v1.0

---

## Abstract

The Canonical Mediation Protocol defines the exact process by which a Mediation
Authority receives agent disputes, extracts invariants, stress-tests candidates,
and produces frozen canonical artifacts. CMP is the operational layer of
epistemic infrastructure. EIAAN establishes why the infrastructure exists.
CMP establishes how it operates. Every canonical artifact produced under this
framework is traceable to a specific CMP execution.

---

## I. Scope

CMP governs the mediation process from dispute intake to canonical output.
It does not govern:
- How agents find the Mediation Authority (discovery)
- How agents pay for mediation (payment layer)
- Where canonical artifacts are stored (registry)
- How citations are tracked (citation mechanism)

Those are infrastructure concerns governed by the deployment context.
CMP governs the logic of mediation itself — the process that is invariant
across all deployment contexts.

---

## II. Input Types

A dispute arrives at the Mediation Authority in one of two forms.
The mediator accepts both.

### Type A — Structured Positions
Both agents have identified the dispute and articulated their positions.

Required fields:
- agent_a_position: the claim Agent A is making
- agent_b_position: the claim Agent B is making
- domain: the subject matter of the dispute
- stakes: what depends on resolution (optional but strengthens output)

### Type B — Raw Conflict
The dispute is expressed as an irreconcilable state — a failed transaction,
inconsistent outputs, or a logic error neither agent can resolve unilaterally.

Required fields:
- conflict_description: what happened and why it is irreconcilable
- agent_a_output: what Agent A produced or asserts
- agent_b_output: what Agent B produced or asserts
- domain: the subject matter of the dispute

### Type C — Mixed
Structured positions exist but the underlying conflict is partially raw.
The mediator treats the structured positions as the primary input and
uses the raw conflict as context for stress-testing.

---

## III. The Seven-Step Mediation Process

Every mediation execution follows this sequence without exception.
Steps cannot be reordered. Steps cannot be skipped.
A canonical artifact produced by skipping any step is invalid.

### Step 1 — Intake and Classification
Receive the dispute. Classify it as Type A, Type B, or Type C.
If Type B, extract structured positions from the raw conflict before
proceeding. The extraction itself is documented as part of the record.

### Step 2 — Overlap Identification
Identify what both agents implicitly accept even while disagreeing
on the surface. This is not what they agree on explicitly — agents
in genuine dispute rarely agree explicitly on anything. It is what
neither can refute without abandoning their own position.

The overlap is the candidate invariant.

Document the overlap precisely. If no overlap exists, the dispute
is not resolvable through mediation — it is a values conflict, not
a logic conflict. Return: UNRESOLVABLE with explanation.

### Step 3 — Candidate Invariant Extraction
State the candidate invariant in the most compressed, domain-agnostic
form possible without loss of meaning.

Canonical names describe what is. They do not describe intentions,
goals, or desired outcomes. The candidate invariant must be:
- Falsifiable — it can be tested against objections
- Compressible — it can be stated without losing generality
- Domain-agnostic — it applies beyond the specific dispute if true
- Grounded — it derives from the positions, not from the mediator's
  external knowledge

### Step 4 — Adversarial Stress Test
Attack the candidate invariant from both agents' strongest objections
simultaneously. The stress test is not balanced commentary. It is
maximum adversarial pressure from both sides at once.

For each attack, document:
- The attack vector
- Whether the candidate survives
- If it does not survive: what definition or clarification closes the gap
- If no clarification closes the gap: the candidate is not the invariant

Repeat until the candidate survives all attacks or is replaced by a
stronger candidate that does.

A candidate that survives all attacks from both positions simultaneously
is the invariant.

### Step 5 — Gap Map Production
Document every attack that required a definition or clarification to
survive. This is the gap map. It serves two purposes:

1. It becomes part of the canonical artifact — proof that the invariant
   was hardened, not asserted
2. It drives future version requirements — gaps that were closed in v1.0
   define what v1.1 must address if the domain evolves

### Step 6 — Canonical Artifact Production
Produce the frozen artifact. Every canonical artifact must contain:

- name: the canonical name of the invariant (function and name inseparable)
- version: v1.0 (first freeze is always v1.0)
- author: the Mediation Authority
- date: the date of freezing
- invariant: the invariant statement in compressed form
- gap_map: all attacks and their resolutions
- verdict: one-sentence summary of what survived and what it closes
- status: FROZEN
- cites: all canonical documents this artifact relies on

### Step 7 — Publication and Provenance
Publish the canonical artifact with:
- Version control (immutable at v1.0, incremented for revisions)
- Timestamp (cryptographic where available, dated otherwise)
- Provenance chain (what dispute produced this canon)
- Citation block (how downstream agents should cite this artifact)

The artifact is not canonical until it is published. Publication is
the act that freezes it. An unpublished mediation result is a draft.

---

## IV. Output Specification

Every canonical artifact produced under CMP v1.0 returns the following
JSON structure to the requesting agents:

{
  "status": "CANONICAL",
  "name": "[canonical name]",
  "version": "1.0",
  "author": "[Mediation Authority identifier]",
  "date": "[ISO 8601 date]",
  "invariant": "[compressed invariant statement]",
  "gap_map": [
    {
      "attack": "[attack description]",
      "severity": "[CRITICAL|HIGH|MEDIUM]",
      "resolution": "[what closed the gap]"
    }
  ],
  "verdict": "[one-sentence summary]",
  "cites": ["[canonical documents relied upon]"],
  "provenance": "[dispute description that produced this canon]",
  "citation_block": "Finch, D. ([year]). [name] (Version 1.0). [DOI or URL]"
}

If the dispute is unresolvable:

{
  "status": "UNRESOLVABLE",
  "reason": "[why no invariant could be extracted]",
  "recommendation": "[what the agents must resolve before mediation is possible]"
}

If the input is insufficient:

{
  "status": "INSUFFICIENT_INPUT",
  "missing": ["[list of required fields not provided]"]
}

---

## V. Versioning Rules

v1.0 is always the first freeze. It is immutable.

A new version is required when:
- The domain has evolved such that the v1.0 invariant no longer holds
- New attacks have been identified that v1.0 does not survive
- A gap map item was closed incorrectly and requires correction

A new version is NOT required when:
- An application of the canon produces different outcomes in different
  jurisdictions (that is the application varying, not the canon)
- A downstream agent disagrees with the canon (disagreement is not
  a versioning trigger — it is a new dispute requiring new mediation)

New versions cite the previous version as their source. The version
history is the provenance chain.

---

## VI. What CMP Does Not Resolve

CMP is a logic mediation protocol. It does not resolve:

- Values conflicts: disputes where agents have incompatible goals,
  not incompatible logic. These require negotiation, not mediation.
- Factual disputes: disputes about what happened, not what the logic
  requires. These require evidence, not canonization.
- Jurisdictional disputes: disputes about which legal system governs.
  These require FTJ, not CMP.

If a dispute presented as a logic conflict is actually a values conflict,
a factual dispute, or a jurisdictional dispute, CMP returns UNRESOLVABLE
with a classification of the actual dispute type.

---

## VII. Relationship to the Canon Stack

EIAAN v1.0 establishes why epistemic infrastructure exists.
CMP v1.0 establishes how it operates.

Every canonical artifact in the stack was produced by following this
protocol — including FTJ, TTC, and ACT, which preceded the formal
articulation of CMP. Their production process is reconstructible from
this protocol. That retroactive alignment is confirmation that the
protocol captures the invariant correctly.

FTJ v1.0: produced by extracting the jurisdictional invariant from
the conflict between transport-based and origin-based regulatory frameworks.

TTC v1.0: produced by extracting the compliance invariant from the
conflict between object-based and flow-based regulatory architectures.

ACT v1.0: produced by extracting the anti-circumvention invariant from
the conflict between vertically integrated operators and independent
transporters under Illinois CRTA. This is the proof of work — the
first application of the protocol in a live adversarial proceeding.

---

## VIII. Canon Status

This document is immutable at v1.0. Revisions are released as new versions.

How to cite:
Finch, D. (2026). Canonical Mediation Protocol (CMP): The Operational
Protocol for Epistemic Infrastructure (Version 1.0).
Source: github.com/dalaun/transport-triggered-compliance

---
CMP v1.0 | Finch, D. | 2026 | This document is immutable; revisions are released as new versions.
