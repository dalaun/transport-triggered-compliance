"""
prov_writer.py — PROV-O provenance records for frozen TTCD canons.

When canonizer.py produces a FROZEN canon, write_canon_provenance() is called.
It writes a PROV-O Turtle file to /root/ttcd-pub/provenance/<hash>.ttl.

Each record captures:
  - The canon as prov:Entity
  - The CMP run as prov:Activity
  - The agents as prov:Agent
  - Temporal bounds of the mediation
  - Challenge derivation (when a canon supersedes another)

Files are served via GET /prov/<hash> and can be bulk-loaded into GraphDB.
"""

import os, time
from datetime import datetime, timezone

PROV_DIR = os.path.join(os.path.dirname(__file__), "..", "provenance")
PROV_NS  = "https://ttcd.io/provenance/"
TTCD_NS  = "https://ttcd.io/ontology#"
PROV     = "http://www.w3.org/ns/prov#"
XSD      = "http://www.w3.org/2001/XMLSchema#"


def _iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_canon_provenance(canon_hash, domain, status, agents,
                           started_at, ended_at,
                           supersedes_hash=None, metadata=None):
    """
    Write a PROV-O Turtle file for a canon produced by CMP.
    Only writes for FROZEN canons — DRAFT canons leave no provenance record.

    Returns the file path written, or None if skipped.
    """
    if status != "FROZEN":
        return None

    os.makedirs(PROV_DIR, exist_ok=True)

    canon_uri    = f"{PROV_NS}canon/{canon_hash}"
    activity_uri = f"{PROV_NS}cmp/{canon_hash}"
    started_iso  = _iso(started_at)
    ended_iso    = _iso(ended_at)
    domain_safe  = domain.replace('"', '\\"')

    # Agent blocks
    agent_blocks = []
    attr_lines   = []
    assoc_lines  = []
    for agent_id in agents:
        safe_id   = agent_id.replace("/", "_").replace(":", "_")
        agent_uri = f"{PROV_NS}agent/{safe_id}"
        agent_blocks.append(
            f'<{agent_uri}>\n'
            f'    a prov:Agent ;\n'
            f'    rdfs:label "{agent_id}" .\n'
        )
        attr_lines.append(f'    prov:wasAttributedTo <{agent_uri}> ;')
        assoc_lines.append(f'    prov:wasAssociatedWith <{agent_uri}> ;')

    # Supersession (challenge upheld — this canon replaces another)
    supersedes_block = ""
    if supersedes_hash:
        orig_uri = f"{PROV_NS}canon/{supersedes_hash}"
        supersedes_block = (
            f'\n<{orig_uri}>\n'
            f'    a prov:Entity ;\n'
            f'    prov:wasInvalidatedBy <{activity_uri}> .\n'
        )

    # Metadata annotations
    meta_block = ""
    if metadata:
        for k, v in metadata.items():
            safe_k = k.replace("-", "_")
            meta_block += f'    ttcd:{safe_k} "{str(v).replace(chr(34), "")}" ;\n'

    ttl = f"""@prefix prov:  <{PROV}> .
@prefix ttcd:  <{TTCD_NS}> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <{XSD}> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .

# PROV-O record for TTCD canon {canon_hash[:16]}...
# Domain: {domain}
# Generated: {ended_iso}

<{canon_uri}>
    a prov:Entity , ttcd:FrozenCanon ;
    rdfs:label "Canon: {domain_safe}" ;
    prov:wasGeneratedBy <{activity_uri}> ;
    prov:generatedAtTime "{ended_iso}"^^xsd:dateTime ;
{chr(10).join(attr_lines)}
    ttcd:canonHash "{canon_hash}" ;
    ttcd:canonDomain "{domain_safe}" ;
    ttcd:canonStatus "FROZEN" ;
{meta_block}    owl:versionInfo "1.0" .

<{activity_uri}>
    a prov:Activity ;
    rdfs:label "CMP run: {domain_safe}" ;
    prov:startedAtTime "{started_iso}"^^xsd:dateTime ;
    prov:endedAtTime   "{ended_iso}"^^xsd:dateTime ;
    prov:generated <{canon_uri}> ;
{chr(10).join(assoc_lines)}
    ttcd:cmpDoi "10.5281/zenodo.18732820" .

{''.join(agent_blocks)}
{supersedes_block}
"""

    path = os.path.join(PROV_DIR, f"{canon_hash}.ttl")
    with open(path, "w") as f:
        f.write(ttl)

    return path


def get_provenance_ttl(canon_hash):
    """Return TTL string for a canon, or None if no record exists."""
    path = os.path.join(PROV_DIR, f"{canon_hash}.ttl")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


def list_provenance():
    """List all canon hashes with provenance records."""
    if not os.path.exists(PROV_DIR):
        return []
    return [
        f.replace(".ttl", "")
        for f in os.listdir(PROV_DIR)
        if f.endswith(".ttl")
    ]
