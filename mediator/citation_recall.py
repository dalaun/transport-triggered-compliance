#!/usr/bin/env python3
"""
Citation Recall v1.0
Agent IP memory — surfaces existing frozen canons before new mediations.
Implements: EpistemicCustody, CanonicalDebt, PropagationLiability (all v1.0)

Prevents agents from reworking ground already covered by a frozen canon.
Called automatically in mediate() and exposed as GET /recall endpoint.

DOI: 10.5281/zenodo.18765787
"""

import os, re, json
from collections import defaultdict
from pathlib import Path

CANON_DIR = "/root/ttcd-pub/canon"
INDEX_PATH = "/root/ttcd-pub/mediator/canon_index.json"

# Stop words — too common to be meaningful index terms
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "can",
    "could", "should", "may", "might", "must", "shall", "not", "no", "nor",
    "it", "its", "this", "that", "these", "those", "they", "them", "their",
    "we", "us", "our", "you", "your", "he", "she", "his", "her", "who",
    "what", "when", "where", "which", "how", "if", "than", "then", "so",
    "as", "any", "all", "each", "both", "only", "also", "more", "most",
    "such", "same", "other", "into", "out", "up", "about", "over", "after",
    "under", "between", "through", "during", "before", "without", "within",
    "does", "whether", "either", "neither", "once", "while", "because",
    "there", "here", "very", "just", "still", "even", "well", "now"
}

# Canonical domain terms — weighted higher in scoring
DOMAIN_TERMS = {
    "jurisdiction", "custody", "movement", "flow", "flows", "transport",
    "compliance", "obligation", "mediation", "canon", "canonical", "frozen",
    "invariant", "invariants", "epistemic", "agent", "agents", "claim",
    "claims", "provenance", "citation", "version", "operator", "decay",
    "debt", "liability", "precedent", "escrow", "sovereignty", "hardened",
    "propagation", "stare", "decisis", "naming", "protocol", "ontology"
}

def extract_terms(text: str) -> list:
    """Extract meaningful terms from text, lowercased, de-stopped."""
    words = re.findall(r"[a-z][a-z\-']*[a-z]", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 3]

def parse_canon_for_index(path: str) -> dict:
    """Extract indexable content from a canon markdown file."""
    with open(path) as f:
        text = f.read()

    filename = Path(path).stem  # e.g. FTJ_v1.0

    # Name from first heading
    name = ""
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean and not clean.startswith("Author") and not clean.startswith("Version"):
            name = clean
            break
    name = re.sub(r"\s*\(\w+\)\s*$", "", name).strip()
    name = re.sub(r"\s*A First-Principles.*$", "", name).strip()

    # DOI
    doi_m = re.search(r"DOI:\s*(10\.\S+)", text)
    doi = doi_m.group(1) if doi_m else None

    # Status
    status_m = re.search(r"Status:\s*(\S+)", text)
    status = status_m.group(1).rstrip(",") if status_m else "UNKNOWN"

    # Scope boundary (from our added section)
    scope_m = re.search(r"\*\*Scope Boundary:\*\*\s*(.+)", text)
    scope = scope_m.group(1).strip() if scope_m else ""

    # Core invariant lines (from "## The Invariant" or prominent sentences)
    invariants = []
    inv_sec = re.search(r"##\s+The Invariant\s*\n+([\s\S]*?)(?=\n##|\n---|\Z)", text)
    if inv_sec:
        for line in inv_sec.group(1).splitlines():
            line = line.strip()
            if 10 < len(line) < 150 and not line.startswith("If you"):
                invariants.append(line)
        invariants = invariants[:4]

    # Jurisdictional declarations
    fid_m = re.search(r"\*\*Fiduciary Moment:\*\*\s*(.+)", text)
    fiduciary = fid_m.group(1).strip() if fid_m else ""

    evid_m = re.search(r"\*\*Evidence Standard:\*\*\s*(.+)", text)
    evidence = evid_m.group(1).strip() if evid_m else ""

    # All index terms: name + scope + invariants + fiduciary + evidence + first 400 words of content
    index_text = " ".join([name, scope, fiduciary, evidence] + invariants)
    # Add first 400 words of body (strip markdown)
    body = re.sub(r"#.*\n", " ", text)
    body = re.sub(r"\*\*[^*]+\*\*", " ", body)
    body_words = body.split()[:400]
    index_text += " " + " ".join(body_words)

    terms = extract_terms(index_text)
    # Term frequency dict, domain terms weighted x3
    tf = defaultdict(int)
    for t in terms:
        weight = 3 if t in DOMAIN_TERMS else 1
        tf[t] += weight

    return {
        "file": filename,
        "name": name,
        "status": status,
        "doi": doi,
        "scope": scope,
        "invariants": invariants,
        "fiduciary": fiduciary,
        "evidence": evidence,
        "tf": dict(tf),
    }

def build_index(force: bool = False) -> list:
    """Build or load the citation index."""
    if not force and os.path.exists(INDEX_PATH):
        with open(INDEX_PATH) as f:
            return json.load(f)

    files = sorted([
        f for f in os.listdir(CANON_DIR)
        if f.endswith(".md") and not f.startswith("Validation")
    ])

    index = []
    for fname in files:
        entry = parse_canon_for_index(os.path.join(CANON_DIR, fname))
        index.append(entry)

    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)

    return index

def score_recall(entry: dict, query_terms: list, query_claims: list) -> float:
    """Score a canon entry against query terms and claims."""
    tf = entry["tf"]
    score = 0.0

    # Term overlap with query
    for term in query_terms:
        if term in tf:
            score += tf[term] * 0.1

    # Direct claim string overlap (high weight)
    canon_text = " ".join(entry["invariants"] + [entry["scope"], entry["fiduciary"]]).lower()
    for claim in query_claims:
        claim_terms = extract_terms(claim)
        for ct in claim_terms:
            if ct in canon_text:
                score += 2.0

    return round(score, 2)

def recall(domain: str, claims: list = None, top_n: int = 3) -> dict:
    """
    Surface existing canons relevant to a new mediation.
    Returns matches ranked by relevance score.

    domain: the domain being submitted for mediation
    claims: list of claim strings from agent positions
    top_n: max number of matches to return
    """
    index = build_index()
    claims = claims or []

    query_terms = extract_terms(domain)
    for claim in claims:
        query_terms.extend(extract_terms(claim))

    # Dedupe query terms
    query_terms = list(set(query_terms))

    scored = []
    for entry in index:
        score = score_recall(entry, query_terms, claims)
        if score > 0:
            scored.append({
                "canon": entry["name"],
                "file": entry["file"],
                "status": entry["status"],
                "doi": entry["doi"],
                "score": score,
                "scope": entry["scope"],
                "matched_invariants": [
                    inv for inv in entry["invariants"]
                    if any(t in inv.lower() for t in query_terms)
                ][:2],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:top_n]

    frozen_hits = [r for r in top if r["status"] in ("FROZEN", "frozen")]
    debt_risk = len(frozen_hits) > 0

    return {
        "schema": "CitationRecall/1.0",
        "domain": domain,
        "query_terms": query_terms[:20],
        "matches": top,
        "canonical_debt_risk": debt_risk,
        "debt_risk_message": (
            f"This domain overlaps with {len(frozen_hits)} frozen canon(s). "
            "Cite them in your submission to avoid canonical debt."
        ) if debt_risk else "No overlapping frozen canons detected.",
    }

if __name__ == "__main__":
    import sys

    # Rebuild index
    print("Building citation index...")
    idx = build_index(force=True)
    print(f"Indexed {len(idx)} canons\n")

    # Test recall
    domain = sys.argv[1] if len(sys.argv) > 1 else "regulatory jurisdiction over agent data flows"
    claims = sys.argv[2:] if len(sys.argv) > 2 else [
        "jurisdiction attaches at movement",
        "custody creates obligation",
        "agents must cite canonical sources"
    ]

    result = recall(domain, claims)
    print(f"Domain:  {domain}")
    print(f"Claims:  {claims}")
    print(f"Debt risk: {result['canonical_debt_risk']}")
    print(f"\nTop matches:")
    for m in result["matches"]:
        print(f"  [{m['score']:5.1f}] {m['canon']} ({m['status']}) doi={m['doi']}")
        for inv in m["matched_invariants"]:
            print(f"         -> {inv[:80]}")
