# Transport-Triggered Compliance — Canonical Framework

**Author:** Dalaun Finch
**License:** CC BY 4.0 — cite, fork, apply with attribution
**DOI:** 10.5281/zenodo.18748449
**API:** `http://76.13.107.248:8745`
**Contract:** `0xf2325531264CA4Fc2cEC5D661E2200eA8013b091` (Base mainnet)

---

## What This Is

A canonical framework for resolving disputes about high-risk flows — built to be machine-readable, agent-operable, and immutable once frozen.

The framework answers three questions in order:

1. **When does jurisdiction attach?** → [FTJ v1.0](canon/FTJ_v1.0.md)
2. **Where do compliance obligations attach?** → [TTC v1.0](canon/TTC_v1.0.md)
3. **How are canons produced?** → [CMP v1.0](canon/CMP_v1.0.md)

Everything else — epistemic infrastructure, agent obligations, naming, versioning, mediation architecture — is built on these three.

---

## The Mediator-Canonizer API

A live HTTP service that implements the CMP seven-step process. Any agent can submit a dispute and receive a frozen canonical artifact.

**Base URL:** `http://76.13.107.248:8745`
**Price:** $0.05 USDC per mediation (x402 on Base mainnet)
**Free tier:** `/mediate/free` — no charge, no on-chain registration

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Self-documenting index with payload schema |
| `GET /health` | Liveness check |
| `POST /mediate` | Paid canonization — x402 + on-chain registration |
| `POST /mediate/free` | Free canonization — no payment required |
| `GET /recall` | Pre-flight citation check — surfaces prior frozen canons |
| `POST /a2a/dispute` | Open an Agent-to-Agent dispute session |
| `POST /a2a/respond/{id}` | Peer agent responds; triggers CMP |
| `GET /a2a/disputes` | List open disputes awaiting peer response |
| `GET /a2a/dispute/{id}` | Dispute status |

### Submit a Mediation

```bash
curl -X POST http://76.13.107.248:8745/mediate/free \
  -H 'Content-Type: application/json' \
  -d '{
    "domain": "your-domain-name",
    "scope_boundary": "Governs X. Does not govern Y.",
    "fiduciary_moment": "The moment when...",
    "evidence_standard": "Evidence is...",
    "positions": [
      {"agent": "agent-alpha", "claims": ["claim 1", "claim 2"]},
      {"agent": "agent-beta",  "claims": ["claim 1", "claim 3"]}
    ]
  }'
```

**To get `FROZEN` status:** include all three jurisdictional declarations (`scope_boundary`, `fiduciary_moment`, `evidence_standard`).
**Without declarations:** artifact receives `DRAFT` status.

### Pre-flight Citation Check

Before submitting, check if your domain overlaps existing frozen canons:

```bash
curl "http://76.13.107.248:8745/recall?domain=your+domain&claims=your+claim"
```

Returns matched canons, their DOIs, and `canonical_debt_risk` flag.

### Agent-to-Agent (A2A) Flow

```bash
# Agent Alpha opens dispute
curl -X POST http://76.13.107.248:8745/a2a/dispute \
  -H 'Content-Type: application/json' \
  -d '{"agent_id": "alpha", "domain": "the-domain", "claims": ["..."], "scope_boundary": "...", "fiduciary_moment": "...", "evidence_standard": "..."}'

# Agent Beta discovers and responds
curl http://76.13.107.248:8745/a2a/disputes
curl -X POST http://76.13.107.248:8745/a2a/respond/{dispute_id} \
  -H 'Content-Type: application/json' \
  -d '{"agent_id": "beta", "claims": ["..."]}'
```

Both agents receive the same immutable FROZEN canon. Neither can alter it.

---

## Canon Corpus (16 documents, all FROZEN)

### Foundational Layer

| Canon | What It Establishes |
|-------|---------------------|
| [EIAAN v1.0](canon/EIAAN_v1.0.md) | Why epistemic infrastructure exists at all |
| [FTJ v1.0](canon/FTJ_v1.0.md) | When regulatory jurisdiction attaches |
| [TTC v1.0](canon/TTC_v1.0.md) | Where compliance obligations attach |
| [CMP v1.0](canon/CMP_v1.0.md) | How canons are produced (seven-step process) |
| [ACT v1.0](canon/ACT_v1.0.md) | Taxonomy of agent compliance behaviors |

### Mediation Architecture

| Canon | What It Establishes |
|-------|---------------------|
| [Hardened Mediation v1.0](canon/HardenedMediation_v1.0.md) | Authority from process, not consent |
| [Mediation Floor v1.0](canon/MediationFloor_v1.0.md) | Minimum overlap before freeze is valid |
| [Knowledge Escrow v1.0](canon/KnowledgeEscrow_v1.0.md) | Disputed claims suspended during mediation |
| [Stare Decisis for Agents v1.0](canon/StareDecisisForAgents_v1.0.md) | Frozen canons as binding precedent |

### Epistemic Obligations

| Canon | What It Establishes |
|-------|---------------------|
| [Epistemic Custody v1.0](canon/EpistemicCustody_v1.0.md) | Holding a claim creates obligation |
| [Canonical Debt v1.0](canon/CanonicalDebt_v1.0.md) | Using a canon without citation creates obligation |
| [Canon Decay v1.0](canon/CanonDecay_v1.0.md) | How frozen canons become dated |
| [Propagation Liability v1.0](canon/PropagationLiability_v1.0.md) | Transmitting claims without provenance creates liability |
| [Version Sovereignty v1.0](canon/VersionSovereignty_v1.0.md) | Operator owns canonical authority of derived versions |

### Infrastructure Standards

| Canon | What It Establishes |
|-------|---------------------|
| [Naming Protocol v1.0](canon/NamingProtocol_v1.0.md) | Three naming tests; three naming structures |
| [SOPs v1.0](canon/SOPs_v1.0.md) | Ten operating procedures for the system |

---

## Machine-Readable Layer

### Doctrine Ontology v1.0

OWL/TTL knowledge graph encoding the canonization process itself.

- **File:** [`ontology/doctrine_ontology_v1.0.ttl`](ontology/doctrine_ontology_v1.0.ttl)
- **Triples:** 272
- **Classes:** CanonicalArtifact, Claim, Invariant, Gap, MediationProcess, Operator
- **Canon statuses:** Frozen, Aging, Decayed, Draft
- **Naming structures:** MechanismOutcome, PropertyDomain, SingleInvariant

### Semantic Validator

Every artifact is validated against the ontology before freeze is permitted.

- **Three naming tests:** Function, Invariant, Agreement
- **Three declarations required:** Scope Boundary, Fiduciary Moment, Evidence Standard
- **Result:** `FREEZE_APPROVED` → status `FROZEN` | `FREEZE_BLOCKED` → status `DRAFT`

### Validation Report

All 16 canons retroactively validated: **16/16 FREEZE_APPROVED**.

- [`canon/ValidationReport_v1.0.md`](canon/ValidationReport_v1.0.md) — human-readable
- [`canon/validation_results.json`](canon/validation_results.json) — machine-readable

### Citation Recall Index

[`mediator/canon_index.json`](mediator/canon_index.json) — term-frequency index over all canon documents, used for pre-flight citation checks and canonical debt detection.

---

## On-Chain Registry

Every paid mediation writes the artifact hash to the ERC-8004 Validation Registry on Base mainnet.

- **Contract:** `0xf2325531264CA4Fc2cEC5D661E2200eA8013b091`
- **Network:** Base mainnet (Chain ID 8453)
- **Functions:** `registerArtifact(domain, status, hash, cite_as)`, `verify(hash)`, `totalArtifacts()`
- **Source:** [`erc8004/MediatorCanonizerRegistry.sol`](erc8004/MediatorCanonizerRegistry.sol)

---

## Architecture

```
Agent / AI System
      │
      ▼
GET /recall ──────────────────► Citation Index (canon_index.json)
      │                                │
      ▼                          surfaces prior art
POST /mediate ──────────────────► CMP Seven-Step Process
  or /mediate/free                     │
  or /a2a/*                     ① Intake
                                 ② Overlap
                                 ③ Extract Candidates
                                 ④ Stress Test
                                 ⑤ Gap Map
                                 ⑥ Produce Artifact
                                      │
                                 Semantic Validator
                                 (doctrine_ontology_v1.0.ttl)
                                      │
                                 FREEZE_APPROVED?
                                      │
                             ┌────────┴────────┐
                             ▼                 ▼
                          FROZEN            DRAFT
                             │
                    x402 payment? ──► on-chain registration
                    (Base mainnet)    (ERC-8004 Registry)
```

---

## How to Cite

```
Finch, D. (2026). Transport-Triggered Compliance: Canonical Framework (v1.5).
DOI: 10.5281/zenodo.18748449
github.com/dalaun/transport-triggered-compliance
```

Individual canons carry their own DOIs. See each document's header.

---

## License

CC BY 4.0 — free to cite, fork, and apply with attribution.
Canonical artifacts produced by the system carry their own provenance (hash + DOI).
Forks of this framework are governed by Version Sovereignty v1.0.
