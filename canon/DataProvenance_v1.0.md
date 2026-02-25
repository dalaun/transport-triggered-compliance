# Canon: Data Provenance Attachment (DPA) v1.0
**Status:** FROZEN  
**DOI:** 10.5281/zenodo.18765787  
**Version:** 1.0  
**Domain:** Data ownership, data lineage, agent data transactions  
**Canonized:** 2026-02-25  

## Core Invariant
Provenance of a data artifact attaches at the moment of first structured capture, not at the moment of transmission or consumption.

## Invariants
1. A data artifact's provenance chain begins at its origin capture event.
2. Transmission of a data artifact does not transfer provenance — it extends the chain.
3. A consuming agent that transforms data creates a derivative artifact with its own provenance, linked to but distinct from the source.
4. Provenance cannot be stripped retroactively by any downstream agent.
5. An agent asserting ownership of data must demonstrate presence in the provenance chain.

## Jurisdictional Declarations
**Scope Boundary:** Governs all agent-to-agent data transactions where provenance, ownership, or lineage is disputed. Does not govern licensing terms, pricing, or access permissions independently of provenance.

**Fiduciary Moment:** The moment an agent captures, transforms, or transmits a data artifact and fails to record its position in the provenance chain. At that moment the agent forfeits provenance claims downstream.

**Evidence Standard:** A provenance claim is valid when the claiming agent can produce a timestamped record of its capture or transformation event that is consistent with the artifact's content hash at that point in time.

## Stress Test
Tested against: agent purchasing data and claiming original provenance; data broker asserting provenance through transmission volume alone; consumer agent claiming provenance by transformation. All three failed. Provenance attaches at capture only.
