# Standard Operating Procedures v1.0
Mediator-Canonizer System
Author: Dalaun Finch
Status: FROZEN
DOI: 10.5281/zenodo.18748449
Date: 2026-02-25

---

## Overview

These SOPs govern the operation of the Mediator-Canonizer system by the operator.
The system consists of:

- **Mediator-Canonizer API** — Flask service on port 8745 (Base mainnet, x402 enabled)
- **Doctrine Ontology** — 272-triple OWL/TTL knowledge graph at `/root/ttcd-pub/ontology/`
- **Canon corpus** — 15 frozen documents at `/root/ttcd-pub/canon/`
- **ERC-8004 Registry** — on-chain at `0xf2325531264CA4Fc2cEC5D661E2200eA8013b091` (Base mainnet)
- **OpenClaw skill** — workshop copy at `/root/clawd/skills/ttcd/canonizer.py`

---

## SOP-001: Verify System Health

**When:** Daily check. Before any operator action.

```bash
# 1. API health
curl -s http://76.13.107.248:8745/health

# 2. Service running
ssh root@76.13.107.248 "systemctl status mediator-canonizer --no-pager"

# 3. API version + endpoints
curl -s http://76.13.107.248:8745/ | python3 -m json.tool

# 4. On-chain registry reachable
curl -s http://76.13.107.248:8745/health | python3 -c "import json,sys; print(json.load(sys.stdin)['contract'])"
```

**Expected:** `{"status": "ok"}`, service `active (running)`, version `1.1.0`.

---

## SOP-002: Restart the Mediator Service

**When:** After any code update, after crash, after config change.

```bash
ssh root@76.13.107.248
systemctl restart mediator-canonizer
sleep 3
curl -s http://localhost:8745/health
```

**Expected:** `{"status": "ok"}` within 5 seconds of restart.

**If it fails:**
```bash
journalctl -u mediator-canonizer -n 50 --no-pager
```

Look for: missing `PRIVATE_KEY` env var, port already in use, import error.

---

## SOP-003: Add a New Canon Document

**When:** A new doctrine concept has been canonized.

**Steps:**

1. Write the canon document to `/root/ttcd-pub/canon/ConceptName_v1.0.md`
   - Must include: name, status (FROZEN), DOI, date
   - Must include: `## The Invariant` section with at least one invariant
   - Must include: `## Jurisdictional Declarations` section:
     ```
     **Scope Boundary:** ...
     **Fiduciary Moment:** ...
     **Evidence Standard:** ...
     ```

2. Run semantic validation:
   ```bash
   cd /root/ttcd-pub/mediator
   python3 -c "
   from semantic_validator import validate_artifact
   import json
   result = validate_artifact({
       'name': 'Concept Name',
       'domain': 'concept-name',
       'invariants': ['your invariant here'],
       'scope_boundary': 'Governs...',
       'fiduciary_moment': 'The moment...',
       'evidence_standard': 'Evidence of...'
   })
   print(json.dumps(result, indent=2))
   "
   ```
   Required verdict: `FREEZE_APPROVED`.

3. Rebuild citation index:
   ```bash
   python3 /root/ttcd-pub/mediator/citation_recall.py
   ```

4. Commit and push:
   ```bash
   cd /root/ttcd-pub
   git add canon/ConceptName_v1.0.md mediator/canon_index.json
   git commit -m "canon: add ConceptName v1.0"
   git push origin main
   ```

5. Create GitHub release for Zenodo DOI minting (see SOP-005).

---

## SOP-004: Update the Mediator Codebase

**The two-location rule:**
- **OpenClaw** (`/root/clawd/skills/ttcd/`) is the workshop — develop here
- **Standalone API** (`/root/ttcd-pub/mediator/`) is the product — deploy here

**Never edit the standalone API directly.**

```bash
# 1. Edit in workshop
nano /root/clawd/skills/ttcd/canonizer.py

# 2. Test in workshop
python3 /root/clawd/skills/ttcd/canonizer.py demo

# 3. Sync to standalone
cp /root/clawd/skills/ttcd/canonizer.py /root/ttcd-pub/mediator/canonizer.py

# 4. Restart service
systemctl restart mediator-canonizer
sleep 3
curl -s http://localhost:8745/health

# 5. Commit
cd /root/ttcd-pub
git add mediator/canonizer.py
git commit -m "feat: ..."
git push origin main
```

---

## SOP-005: Create a GitHub Release (Zenodo DOI Minting)

**When:** After significant additions to the canon or codebase.

```bash
# On local machine (GitHub CLI)
gh release create v1.X \
  --title "v1.X — Description" \
  --notes "What's new in this release" \
  --repo dalaun/transport-triggered-compliance
```

Then:
1. Go to [Zenodo](https://zenodo.org) → Linked GitHub Repos → Sync
2. The new release will appear as a new Zenodo record
3. Update DOI references in all affected canon documents
4. Re-run retroactive validation if new canons added

**Current DOI chain:**
- v1.0 → 10.5281/zenodo.XXXXXXXX (original)
- v1.2 → 10.5281/zenodo.18732820 (CMP)
- v1.4 → 10.5281/zenodo.18748449 (Ontology, Validator, Naming Protocol)

---

## SOP-006: Monitor x402 Payment Revenue

**When:** Weekly.

```bash
# Check operator balance (USDC on Base)
# Operator address: 0xeb65c54ee09AAc48612Dc77e6d106005547dF67A
# USDC on Base: 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
# Use Basescan: https://basescan.org/address/0xeb65c54ee09AAc48612Dc77e6d106005547dF67A

# Check on-chain registration count
# Contract: 0xf2325531264CA4Fc2cEC5D661E2200eA8013b091
```

**Price:** $0.05 USDC per mediation via `/mediate` (x402).
**Free tier:** `/mediate/free` — no charge, no on-chain registration.
**A2A:** `/a2a/*` — no charge, no on-chain registration (use `/mediate` for paid A2A).

---

## SOP-007: Handle a Failed Mediation

**Symptoms:** Agent reports `status: DRAFT` instead of `FROZEN`.

**Diagnosis:**
```bash
# Check what blocked it
# Look at semantic_validation.verdict in the response:
# - FREEZE_BLOCKED + DECLARATIONS_INCOMPLETE: agent didn't send all 3 declarations
# - FREEZE_BLOCKED + INVALID_NAME: name failed a naming test
# - VALIDATOR_UNAVAILABLE: semantic_validator.py or ontology missing/broken
```

**Fix for agents:**
Tell the agent to include in their POST body:
```json
{
  "scope_boundary": "Governs X. Does not govern Y.",
  "fiduciary_moment": "The moment when...",
  "evidence_standard": "Evidence is..."
}
```

**Fix for ontology errors:**
```bash
python3 -c "from rdflib import Graph; g = Graph(); g.parse('/root/ttcd-pub/ontology/doctrine_ontology_v1.0.ttl', format='turtle'); print(len(g), 'triples')"
```
Expected: `272 triples`.

---

## SOP-008: Run the Retroactive Validator

**When:** After adding or updating canon documents, to confirm 100% FREEZE_APPROVED.

```bash
python3 /tmp/retro_validator.py
# Expected: 15/15 (or N/N) FREEZE_APPROVED
# Report: /root/ttcd-pub/canon/ValidationReport_v1.0.md
# JSON: /root/ttcd-pub/canon/validation_results.json
```

---

## SOP-009: Add a Peer Agent to an A2A Dispute

**When:** An agent needs to resolve a dispute without using the `/mediate` flow directly.

```bash
# 1. Check open disputes
curl -s http://76.13.107.248:8745/a2a/disputes

# 2. Respond as peer
curl -s -X POST http://76.13.107.248:8745/a2a/respond/{dispute_id} \
  -H 'Content-Type: application/json' \
  -d '{"agent_id": "your-agent-id", "claims": ["your claim 1", "your claim 2"]}'

# 3. Result contains FROZEN canon if mediation succeeds
```

---

## SOP-010: Pre-flight Citation Check Before Submitting

**When:** Before any mediation submission, to prevent canonical debt.

```bash
curl -s "http://76.13.107.248:8745/recall?domain=your+domain&claims=your+claim+1&claims=your+claim+2"
```

If `canonical_debt_risk: true`, cite the listed frozen canons in your submission metadata before proceeding.

---

## Emergency Contacts

- **Server:** `ssh root@76.13.107.248`
- **API logs:** `journalctl -u mediator-canonizer -f`
- **GitHub repo:** `github.com/dalaun/transport-triggered-compliance`
- **Contract:** `basescan.org/address/0xf2325531264CA4Fc2cEC5D661E2200eA8013b091`
- **Zenodo record:** `zenodo.org` → search TTCD

---

## Jurisdictional Declarations

**Scope Boundary:** Governs the operational procedures for running the Mediator-Canonizer system. Does not govern canon content, legal compliance, or agent behavior outside the system.

**Fiduciary Moment:** The moment an operator takes an action on the system (restart, commit, deploy) without following the relevant SOP.

**Evidence Standard:** A documented deviation from an SOP, with timestamp and operator identity, constitutes sufficient evidence of a procedural breach.

---

*SOP v1.0 | Finch, D. | 2026 | This document is immutable; revisions are released as new versions.*
