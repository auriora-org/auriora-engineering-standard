# 01 Principles

**Document ID:** AES-PHIL
**Status:** Normative
**Depends On:** [STANDARD](../STANDARD.md), [Terminology](./02-terminology.md)

## 1. Purpose

AURIORA is a long-lived open engineering and research Platform. AES therefore prioritizes coherent architecture, deterministic interfaces, repairability, reuse and honest documentation over short-term local optimization — *scaled to the maturity of the work*. A breadboard is allowed to be a breadboard; a released Module is not.

This chapter states the engineering posture. It contains two normative requirements; everything else is guidance a competent engineer would follow anyway.

## 2. Principles

| Principle | Meaning |
|---|---|
| Build platforms, not isolated products. | Every Module, Controller and Unit is a participant in the long-lived AURIORA Platform. |
| Reuse before creating. | Prefer an existing Unit, interface or Product Family before inventing a new artifact (see the [decision tree](../STANDARD.md#7-primary-architectural-decision-tree)). |
| Documentation supports engineering. | Write enough to understand, continue, test and reproduce the work — and no more. Documentation whose maintenance costs more than the risk it reduces is a defect. |
| Be honest about maturity. | An Experimental artifact may be rough, but it says so. Nothing pretends to be more finished than it is. |
| Stable interfaces beat optimized interfaces. | At Platform boundaries, compatibility clarity outweighs local performance gains. |
| Repairability over unnecessary integration. | Replaceable Units, declared limits and machine-readable identity protect long-term maintainability of released hardware. |
| Preserve rationale for decisions that matter. | Future engineers need *why*, not only *what* — for the decisions that are expensive to reverse. A line in `design-notes.md` is usually enough; formal records are for platform-wide decisions. |
| Prefer explicitness over cleverness. | Names, ownership, maturity state and compatibility promises should be obvious to future maintainers. |
| Design for decades, not for releases. | Short-term convenience is fine when its long-term Platform impact is bounded — and noted. |

## 3. Working Rules

- If an existing Unit can satisfy the function through a declared interface, reuse it.
- If a Module can be extended without changing its architectural identity or compatibility promise, extend it.
- If the required behavior creates a new standalone product role, create a new Module.
- If the new role would establish a durable identity across multiple products or revisions, create or reserve a Product Family.
- If a decision changes canonical vocabulary, interface semantics, compatibility guarantees or family identity, record it per [Decisions and Governance](./08-decisions-and-governance.md).

## 4. Normative Requirements

### AES-PHIL-003: Determinism for Critical Interfaces

**Requirement:** Interfaces that affect measurement, stimulation, calibration, safety or identity SHALL be deterministic and documented before the artifact is Released. During Experimental and Active Development work, deterministic behavior SHOULD be designed in from the start, because it is expensive to retrofit.

**Rationale:** Biological sensing and stimulation systems require traceable behavior; convenience shortcuts that obscure state undermine reproducibility.

### AES-PHIL-005: Documentation Scaled to Maturity

**Requirement:** An artifact SHALL carry the documentation required by its maturity level as defined in [Maturity and Release](./07-maturity-and-release.md). An artifact SHALL NOT be Released without documentation sufficient for another competent engineer to understand, build, test and modify it.

**Rationale:** Documentation captures architecture while choices are still visible. But requiring release-grade documentation from prototypes produces stale paperwork, not engineering value. The maturity model sets the bar where the risk actually is.

## 5. Design Trade-offs

AES deliberately avoids becoming a compliance-management system — review gates, conformance levels, registers and evidence packages for every artifact. That model assumes an organization AURIORA does not have. Instead AES is an architectural constitution: vocabulary, identity, interfaces, maturity honesty and release quality, with process required only where it pays for itself. The cost is that more rests on the judgment of the maintainer; the benefit is that the standard describes work that actually happens.
