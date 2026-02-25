# Canon: Agent Liability Attachment (ALA) v1.0
**Status:** FROZEN  
**DOI:** 10.5281/zenodo.18765787  
**Version:** 1.0  
**Domain:** Agent-to-agent transactions, autonomous execution, liability chains  
**Canonized:** 2026-02-25  

## Core Invariant
Liability in an autonomous agent transaction attaches to the agent that held decision authority at the moment the consequential action was taken, not to the agent that initiated the chain.

## Invariants
1. Decision authority is determined by which agent had the last uncontested opportunity to halt or modify the action before execution.
2. An initiating agent that fully delegates decision authority transfers liability with it.
3. Partial delegation — where the initiating agent retains override capability — retains shared liability.
4. An agent acting under instruction with no override capability is not the liable party; liability traces to the instructing agent.
5. Liability cannot be disclaimed by an agent that held decision authority, regardless of downstream instruction.

## Jurisdictional Declarations
**Scope Boundary:** Governs liability assignment in multi-agent execution chains where an action produces a disputed outcome. Does not govern intent, negligence standards, or consequential damage calculation.

**Fiduciary Moment:** The moment an agent executes an irreversible action — a transaction, data write, external API call, or binding commitment — while holding uncontested decision authority. That moment determines liability attachment.

**Evidence Standard:** Decision authority is evidenced by the agent's execution log showing it received the action parameters, had capability to modify or halt, and proceeded. Absence of override capability must be demonstrated structurally, not asserted.

## Stress Test
Tested against: orchestrator agent claiming downstream agent is fully liable; sub-agent claiming it was just following instructions; human operator claiming the agent acted autonomously. All three collapsed under authority-tracing. Liability follows the last decision point.
