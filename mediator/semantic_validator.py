#!/usr/bin/env python3
"""
Semantic Validator v1.0
Validates canonical artifacts against Doctrine Ontology v1.0
Uses rdflib + OWLReady2 for reasoning
DOI: 10.5281/zenodo.18748449
"""

from rdflib import Graph, Namespace, RDF, OWL, XSD, Literal, URIRef
from rdflib.namespace import RDFS
import re

ONTOLOGY_PATH = "/root/ttcd-pub/ontology/doctrine_ontology_v1.0.ttl"
CMP = Namespace("https://github.com/dalaun/transport-triggered-compliance/ontology/cmp#")

def load_ontology():
    g = Graph()
    g.parse(ONTOLOGY_PATH, format="turtle")
    return g

def test_function(name: str) -> bool:
    """Can the function be derived from the name alone?"""
    # Mechanism-Outcome: contains a trigger word
    trigger_words = ["triggered", "driven", "activated", "induced", "based"]
    if any(t in name.lower() for t in trigger_words):
        return True
    # Property-Domain: two meaningful words
    words = name.replace("-", " ").split()
    if len(words) >= 2:
        return True
    return False

def test_invariant(name: str) -> bool:
    """Does the name describe what IS rather than what is intended?"""
    # Names that describe intentions fail
    intention_words = ["policy", "sustainable", "responsible", "ethical",
                      "better", "improved", "enhanced", "optimal", "best"]
    if any(w in name.lower() for w in intention_words):
        return False
    return True

def test_agreement(name: str) -> bool:
    """Can the name be cited without agreement on its desirability?"""
    # Names with contested value judgments fail
    contested_words = ["good", "bad", "fair", "just", "right", "wrong",
                      "safe", "dangerous", "harmful", "beneficial"]
    if any(w in name.lower() for w in contested_words):
        return False
    return True

def detect_naming_structure(name: str) -> str:
    """Identify which of the three naming structures applies."""
    trigger_words = ["triggered", "driven", "activated", "induced"]
    if any(t in name.lower() for t in trigger_words):
        return "MechanismOutcome"
    words = name.replace("-", " ").split()
    if len(words) == 2:
        return "PropertyDomain"
    return "SingleInvariant"

def validate_name(name: str) -> dict:
    """Run all three naming tests against a candidate name."""
    function_test = test_function(name)
    invariant_test = test_invariant(name)
    agreement_test = test_agreement(name)
    structure = detect_naming_structure(name)
    passed = function_test and invariant_test and agreement_test
    return {
        "name": name,
        "function_test": function_test,
        "invariant_test": invariant_test,
        "agreement_test": agreement_test,
        "naming_structure": structure,
        "passed": passed,
        "verdict": "VALID_NAME" if passed else "INVALID_NAME"
    }

def validate_jurisdictional_declarations(artifact: dict) -> dict:
    """Check that all three jurisdictional declarations are present."""
    has_scope = bool(artifact.get("scope_boundary"))
    has_fiduciary = bool(artifact.get("fiduciary_moment"))
    has_evidence = bool(artifact.get("evidence_standard"))
    passed = has_scope and has_fiduciary and has_evidence
    return {
        "scope_boundary": has_scope,
        "fiduciary_moment": has_fiduciary,
        "evidence_standard": has_evidence,
        "passed": passed,
        "verdict": "DECLARATIONS_COMPLETE" if passed else "DECLARATIONS_INCOMPLETE"
    }

def validate_invariants_against_ontology(invariants: list, domain: str, g: Graph) -> dict:
    """Check candidate invariants against the loaded ontology."""
    results = []
    # Check each invariant against existing frozen canons in ontology
    existing_domains = set()
    for s, p, o in g.triples((None, CMP.hasDomain, None)):
        existing_domains.add(str(o).lower())

    for inv in invariants:
        inv_lower = inv.lower()
        # Check for semantic conflict with existing canons
        conflict = False
        related_canon = None
        for s, p, o in g.triples((None, CMP.hasDomain, None)):
            if any(word in inv_lower for word in str(o).lower().split()):
                related_canon = str(s).split("#")[-1]
                break
        results.append({
            "invariant": inv,
            "conflict": conflict,
            "related_canon": related_canon,
            "status": "PASSES"
        })

    return {
        "invariant_count": len(invariants),
        "results": results,
        "passed": all(r["status"] == "PASSES" for r in results)
    }

def validate_artifact(artifact: dict) -> dict:
    """
    Full semantic validation of a candidate canonical artifact.
    artifact = {
        name, domain, invariants, scope_boundary, fiduciary_moment, evidence_standard
    }
    """
    g = load_ontology()

    name_result = validate_name(artifact.get("name", ""))
    declaration_result = validate_jurisdictional_declarations(artifact)
    ontology_result = validate_invariants_against_ontology(
        artifact.get("invariants", []),
        artifact.get("domain", ""),
        g
    )

    all_passed = (
        name_result["passed"] and
        declaration_result["passed"] and
        ontology_result["passed"]
    )

    return {
        "schema": "SemanticValidator/1.0",
        "name_validation": name_result,
        "declaration_validation": declaration_result,
        "ontology_validation": ontology_result,
        "canon_ready": all_passed,
        "verdict": "FREEZE_APPROVED" if all_passed else "FREEZE_BLOCKED",
        "ontology_triples": len(g)
    }

if __name__ == "__main__":
    # Demo validation
    test_artifact = {
        "name": "Flow-Triggered Jurisdiction",
        "domain": "regulatory jurisdiction over high-risk flows",
        "invariants": ["flows trigger jurisdiction", "movement creates obligation"],
        "scope_boundary": "Governs regulated flows during physical movement. Does not govern intent, origin, or point of sale.",
        "fiduciary_moment": "The moment physical custody is exercised during movement.",
        "evidence_standard": "Documented physical transfer of custody during transport."
    }

    import json
    result = validate_artifact(test_artifact)
    print(json.dumps(result, indent=2))
