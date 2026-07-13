# 08 Decisions and Governance

**Document ID:** AES-GOV
**Status:** Normative
**Depends On:** [Terminology](./02-terminology.md), [Interfaces and Versioning](./05-interfaces-and-versioning.md)
**Supersedes:** AES-HIST (Historical Architectural Decisions), AES-EDR (Engineering Decision Records), AES-GOVERNANCE (Governance)

## 1. Purpose

This chapter defines when a decision needs a formal record, how those records are kept, and how governance works for a one- or two-person maintainer team.

## 2. Fixed Historical Decisions

These decisions are the foundation of the Platform. They SHALL be preserved unless superseded by a formal Engineering Decision Record.

| ID | Decision |
|---|---|
| AES-HIST-001 | **Platform before product.** AURIORA engineering treats the Platform as the durable architecture and individual Modules as Platform participants. |
| AES-HIST-002 | **Controllers remain separate from Modules**, even when physically integrated. The Module is the product contract; the Controller is a replaceable implementation center. ([EDR-001](./edr/EDR-001-controller-module-separation.md)) |
| AES-HIST-003 | **Units are replaceable building blocks.** A Unit that cannot be identified, bounded and replaced safely is a subassembly, not a Unit. |
| AES-HIST-004 | **Interfaces are contracts** — versioned architectural commitments, not implementation details. |
| AES-HIST-005 | **Documentation is part of the product** for Released artifacts: a release without sufficient documentation is incomplete. |
| AES-HIST-006 | **Product Families have stable architectural identifiers**, with Family / Product / Revision / Instance identity kept separate. ([EDR-002](./edr/EDR-002-runtime-unit-identity.md) records the related identity decision.) |

## 3. When a Decision Needs a Record

Most decisions need no record beyond the work itself. The ladder:

| Decision kind | Where it is recorded |
|---|---|
| Routine engineering judgment: component selection, local implementation choices, directory layout, refactoring, easily reversible decisions | Nowhere formal. The commit, schematic annotation, issue or PR is enough. |
| Non-obvious project decisions worth remembering: topology choices, rejected alternatives, measurement-driven choices | A short note in `docs/design-notes.md` (or the README for small projects). |
| Project decisions that are expensive to reverse or will be questioned repeatedly: MCU/platform selection for a product, protocol design, storage formats, license choice | An ADR in the project repository (`docs/adr/NNNN-title.md`, per the [Documentation Standard](https://github.com/auriora-org/auriora-documentation-standard)) — recommended, not mandatory. |
| Platform-wide decisions | An EDR — mandatory, see below. |

### AES-EDR-001: EDR Trigger

**Requirement:** An Engineering Decision Record SHALL be created for decisions that are platform-wide: introducing or changing canonical roles or frozen vocabulary, AOID taxonomy values, breaking changes to Released Host or Unit Interfaces, EEPROM schema major versions, Product Family supersession or identifier migration after Release, and changes to AES release or publication policy. These are the decisions that are difficult or expensive to reverse, compatibility-affecting, safety-critical, or shared across repositories and product families.

**Rationale:** These decisions outlive the person who made them and affect artifacts beyond the local repository. Everything not on this list needs, at most, a design note.

### AES-EDR-002: Decision Record Structure and Immutability

**Requirement:** EDRs SHALL include Status, Context, Alternatives Considered, Decision, Rationale and Consequences. An accepted EDR SHALL NOT be rewritten; changes supersede it with a new EDR linking back.

**Rationale:** A record without alternatives is a conclusion, not a decision; history that can be edited is not history.

EDR template:

```markdown
# EDR-NNN: Decision Title

## Status
Proposed / Accepted / Superseded by EDR-NNN / Deprecated

## Context
What Platform problem or risk forced the decision?

## Alternatives Considered
The realistic options, including the chosen one, with their essential trade-offs.

## Decision
The decision, in one or two sentences.

## Rationale
Why this fits AURIORA better than the alternatives.

## Consequences
Costs, risks and obligations this creates.
```

Existing ADRs and EDRs (see the [index in STANDARD.md](../STANDARD.md#9-adr-and-edr-index)) remain valid historical records and SHALL be preserved.

## 4. Governance for a Small Team

Governance names real responsibilities — Platform architecture, family ownership, interface ownership, release ownership, documentation ownership — but AURIORA currently has one or two developers, so those responsibilities are not separate roles held by separate people.

### AES-GOV-010: Maintainer Governance

**Requirement:** The maintainer MAY hold all governance responsibilities. Decisions with Platform-wide reach — family creation, terminology changes, interface changes, compatibility breaks — are governed by their applicable requirements ([AES-TERM-003](./02-terminology.md#aes-term-003-frozen-core-vocabulary), [AES-NAME-001](./04-naming-and-identity.md#aes-name-001-family-identifier-stability), [AES-IF-005](./05-interfaces-and-versioning.md#aes-if-005-backward-compatibility-within-a-major-version), [AES-EDR-001](#aes-edr-001-edr-trigger)) rather than by approval meetings. When the same person authors and reviews a compatibility break or public release, the record SHOULD note it was a self-review, and independent review SHOULD be sought where a qualified reviewer is available.

**Rationale:** Governance that assumes an organization larger than the real team gets silently ignored, which is worse than explicit tailoring. What must survive is the evidence of *what* was decided, not a fiction about *who* approved it.

### AES-GOV-011: Standard Change Record

**Requirement:** The AES repository SHALL maintain a curated `CHANGELOG.md`. Every released AES version SHALL have a changelog entry listing its normative changes (requirement additions, modifications, removals, terminology changes) with requirement identifiers, and SHALL be tagged in version control.

**Rationale:** Conformance claims reference an AES version; without a curated record of normative deltas, adopting a newer version cannot be assessed. This applies equally to the companion standards.
