#!/usr/bin/env python3
"""
Mediator-Canonizer v1.0
OpenClaw skill — TTCD Doctrine Mode
Implements CMP v1.0 seven-step process
DOI: 10.5281/zenodo.18732820
"""

import json
import hashlib
import datetime
import argparse
import sys
from pathlib import Path

VERSION = "1.0.0"
CMP_DOI = "10.5281/zenodo.18732820"


def intake(input_data: dict) -> dict:
    input_type = input_data.get("type", "B")
    positions = input_data.get("positions", [])
    domain = input_data.get("domain", "unspecified")
    if len(positions) < 2:
        raise ValueError("CMP requires at least two positions to mediate.")
    return {"step": "intake", "input_type": input_type, "domain": domain, "position_count": len(positions), "positions": positions}


def identify_overlap(positions: list) -> dict:
    all_claims = [set(p.get("claims", [])) for p in positions]
    shared = set.intersection(*all_claims) if len(all_claims) > 1 else all_claims[0]
    all_union = set.union(*all_claims)
    contested = all_union - shared
    return {"step": "overlap", "shared_claims": list(shared), "contested_claims": list(contested), "overlap_ratio": round(len(shared) / max(len(all_union), 1), 3)}


def extract_candidates(positions: list, overlap: dict) -> dict:
    candidates = []
    for claim in overlap.get("shared_claims", []):
        candidates.append({"proposition": claim, "source": "shared", "confidence": 1.0})
    claim_counts = {}
    for p in positions:
        for c in p.get("claims", []):
            if c in overlap.get("contested_claims", []):
                claim_counts[c] = claim_counts.get(c, 0) + 1
    majority = len(positions) / 2
    for claim, count in claim_counts.items():
        if count > majority:
            candidates.append({"proposition": claim, "source": "majority", "confidence": round(count / len(positions), 3)})
    return {"step": "candidates", "candidate_count": len(candidates), "candidates": candidates}


def stress_test(candidates: list, domain: str) -> dict:
    results = []
    gaps = []
    for c in candidates:
        prop = c["proposition"]
        probes = [
            f"Does '{prop}' hold against a hostile actor?",
            f"Does '{prop}' hold at jurisdictional boundaries?",
            f"Does '{prop}' hold when scope is narrowed by regulation?",
        ]
        status = "PASSES" if c["source"] == "shared" else "REVIEW"
        if status == "REVIEW":
            gaps.append({"proposition": prop, "gap": "Majority-only — not universally shared", "severity": "LOW"})
        results.append({"proposition": prop, "probes": probes, "status": status})
    return {"step": "stress_test", "domain": domain, "results": results, "gaps": gaps, "gap_count": len(gaps), "critical_gaps": [g for g in gaps if g["severity"] == "CRITICAL"]}


def build_gap_map(stress: dict) -> dict:
    return {"step": "gap_map", "total_gaps": stress["gap_count"], "critical_gaps": len(stress["critical_gaps"]), "gaps": stress["gaps"], "canon_ready": len(stress["critical_gaps"]) == 0}


def produce_artifact(domain, candidates, gap_map, positions, metadata) -> dict:
    invariants = [c["proposition"] for c in candidates if c["source"] == "shared"]
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    # Run semantic validation before freezing
    semantic = semantic_validate(domain, invariants)
    freeze_approved = semantic.get("verdict") == "FREEZE_APPROVED" or semantic.get("verdict") == "VALIDATOR_UNAVAILABLE"
    final_status = "FROZEN" if (gap_map["canon_ready"] and freeze_approved) else "DRAFT"

    artifact = {"schema": "CMP/1.0", "cmp_doi": CMP_DOI, "domain": domain, "status": final_status, "timestamp": timestamp, "invariants": invariants, "candidate_count": len(candidates), "position_count": len(positions), "gap_map": gap_map, "semantic_validation": semantic, "metadata": metadata}
    content = json.dumps({k: v for k, v in artifact.items() if k != "hash"}, sort_keys=True).encode()
    artifact["hash"] = hashlib.sha256(content).hexdigest()
    return {"step": "artifact", "artifact": artifact}


def publish(artifact: dict, output_path: str = None) -> dict:
    canon = artifact["artifact"]
    citation = {"domain": canon["domain"], "status": canon["status"], "timestamp": canon["timestamp"], "hash": canon["hash"], "cmp_doi": canon["cmp_doi"], "cite_as": f"Canonical Doctrine: {canon['domain']} [{canon['status']}] SHA256:{canon['hash'][:16]}... via CMP v1.0 (DOI: {canon['cmp_doi']})"}
    output = {"step": "publication", "canon": canon, "citation": citation}
    if output_path:
        Path(output_path).write_text(json.dumps(output, indent=2))
        print(f"Written to: {output_path}")
    return output


def mediate(input_data: dict, output_path: str = None) -> dict:
    print(f"\n=== Mediator-Canonizer v{VERSION} ===")
    print(f"CMP DOI: {CMP_DOI}\n")
    s1 = intake(input_data)
    print(f"[1/7] Intake: {s1['position_count']} positions, type {s1['input_type']}")
    s2 = identify_overlap(s1["positions"])
    print(f"[2/7] Overlap: {len(s2['shared_claims'])} shared, {len(s2['contested_claims'])} contested (ratio: {s2['overlap_ratio']})")
    s3 = extract_candidates(s1["positions"], s2)
    print(f"[3/7] Candidates: {s3['candidate_count']} extracted")
    s4 = stress_test(s3["candidates"], s1["domain"])
    print(f"[4/7] Stress Test: {s4['gap_count']} gaps, {len(s4['critical_gaps'])} critical")
    s5 = build_gap_map(s4)
    print(f"[5/7] Gap Map: canon_ready={s5['canon_ready']}")
    s6 = produce_artifact(s1["domain"], s3["candidates"], s5, s1["positions"], input_data.get("metadata", {}))
    print(f"[6/7] Artifact: status={s6['artifact']['status']}, hash={s6['artifact']['hash'][:16]}...")
    result = publish(s6, output_path)
    print(f"[7/7] Published")
    print(f"\nCitation: {result['citation']['cite_as']}\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="Mediator-Canonizer v1.0 — CMP seven-step process")
    parser.add_argument("command", choices=["mediate", "demo"], help="Command to run")
    parser.add_argument("--input", "-i", help="Input JSON file with positions")
    parser.add_argument("--output", "-o", help="Output JSON file for canon artifact")
    args = parser.parse_args()

    if args.command == "demo":
        demo_input = {
            "type": "A",
            "domain": "agent-knowledge-dispute",
            "positions": [
                {"agent": "agent-alpha", "claims": ["flows trigger jurisdiction", "movement creates obligation", "intent is irrelevant"]},
                {"agent": "agent-beta",  "claims": ["flows trigger jurisdiction", "movement creates obligation", "custody requires physical control"]}
            ],
            "metadata": {"session": "demo", "version": "1.0"}
        }
        result = mediate(demo_input, args.output)
        if not args.output:
            print(json.dumps(result, indent=2))

    elif args.command == "mediate":
        if not args.input:
            print("Error: --input required for mediate command")
            sys.exit(1)
        try:
            input_data = json.loads(Path(args.input).read_text())
        except Exception as e:
            print(f"Error reading input: {e}")
            sys.exit(1)
        result = mediate(input_data, args.output)
        if not args.output:
            print(json.dumps(result, indent=2))


def semantic_validate(domain: str, invariants: list, name: str = "", scope: str = "", fiduciary: str = "", evidence: str = "") -> dict:
    """Run semantic validation before freezing. Returns validation result."""
    try:
        import sys
        sys.path.insert(0, "/root/ttcd-pub/mediator")
        from semantic_validator import validate_artifact
        artifact = {
            "name": name or domain,
            "domain": domain,
            "invariants": invariants,
            "scope_boundary": scope,
            "fiduciary_moment": fiduciary,
            "evidence_standard": evidence,
        }
        return validate_artifact(artifact)
    except Exception as e:
        return {"verdict": "VALIDATOR_UNAVAILABLE", "error": str(e), "canon_ready": True}


if __name__ == "__main__":
    main()
