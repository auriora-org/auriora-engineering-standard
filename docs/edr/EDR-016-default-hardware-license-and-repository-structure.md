# EDR-016: Default Hardware License and Hardware Repository Structure

## Status

Accepted (2026-10-02)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance).*

**Adds** `AES-OH-004` (default licenses) and **replaces** the suggested repository layout of [Maturity and Release §6](../07-maturity-and-release.md#6-repositories-and-workflow); the board-directory naming sentence joins [Naming and Identity §4](../04-naming-and-identity.md#4-public-names). The detailed structure lives in the Hardware Design Guide.

## Context

The first hardware repository with more than one PCB brought two questions AES had left open. The license question: `AES-OH-002` requires every repository to declare its licenses but names none, so a hardware repository chose CERN-OHL-W-2.0 on its own, and the title block, the PCB marking and any future shared KiCad library had no canonical wording to carry. The structure question: the non-normative layout in Maturity and Release §6 suggested `hardware/`, `manufacturing/` and `tools/`, written before any board existed; it did not say whether one product's several PCBs are one or several EDA projects, where generated outputs live, or how a board directory is named so that it stays unambiguous outside its repository. The review of a generic KiCad project-structure proposal against AES, the Hardware Design Guide and the Documentation Standard produced this record.

## Alternatives Considered

### Hardware license

| Option | Outcome |
|---|---|
| **Per-repository choice, AES stays silent** | Rejected. Reuse between boards — footprints, 3D models, proven circuit blocks, a shared library — would need a license check at every copy, and no canonical title-block or marking wording could exist. |
| **CERN-OHL-S-2.0 (strongly reciprocal)** | Rejected. A third party that builds a Module around an AURIORA interface block would have to open its whole design. That works against the Platform's goal of other people building Modules. |
| **CERN-OHL-P-2.0 (permissive)** | Rejected. Nothing would bring improvements to AURIORA designs back; the guide's "fixes flow back to the shared library" would rest on goodwill alone. |
| **CERN-OHL-W-2.0 (weakly reciprocal) as the Platform default** | **Chosen.** The AURIORA design and its modifications stay open; a larger design that incorporates an AURIORA block stays its author's. A repository may still deviate, with an EDR naming it. |

### Repository layout

| Option | Outcome |
|---|---|
| **Keep `hardware/` and add `boards/` only when a second PCB appears** | Rejected. The second PCB arrives after schematic and layout work has started, when moving the first project costs the most and breaks links. |
| **`boards/` always, one EDA project per independently manufactured PCB** | **Chosen.** One directory level, no reorganization later, each board with its own revision, BOM and outputs. |
| **Rename `tools/` to `tooling/`** | Rejected. Same meaning, churn in every repository. |
| **Commit generated manufacturing outputs in `manufacturing/` or `releases/`** | Rejected. Outputs are regenerated from the tagged source revision and attached to that tag's release; `AES-MFG-001`'s immutable package is the release, not a directory. |
| **Board directory named by role alone (`main/`, `status/`)** | Rejected. Ambiguous in tooling, release packages and CI output. The name carries family identifier, product number and role. |

### Identity in the title block

| Option | Outcome |
|---|---|
| **AOID in the title block** | Rejected as the primary field. The AOID is machine identity, `PUB` only once Released, and belongs in the README table and the object manifest. |
| **Product number `<FAMILY-ID>-<NN>` and board identity `<FAMILY-ID>-<NN>-<ROLE>`** | **Chosen.** Human identity per Naming and Identity §5; no new identifier class for internal boards. |

## Decision

1. **`AES-OH-004` — Default Licenses.** AURIORA hardware design sources are licensed under **CERN-OHL-W-2.0**, AURIORA normative documents under **CC BY-SA 4.0**, unless an EDR records a different license for a named repository. The repository `LICENSE` carries the complete text; every hardware release package carries the license text and the Source Location.
2. **Repository layout** ([Maturity and Release §6](../07-maturity-and-release.md#6-repositories-and-workflow)): `README.md`, `LICENSE`, `boards/` — present even for a single PCB — `docs/`, `mechanical/`, `tools/`; nothing created empty; generated outputs attached to the tagged release.
3. **Board directory name** ([Naming and Identity §4](../04-naming-and-identity.md#4-public-names)): `<family-id>-<nn>-<role>`, lowercase kebab-case, the role present even for a single-board product, the EDA root files carrying the same name; `<FAMILY-ID>-<NN>-<ROLE>` is the board identity in title blocks and markings.
4. **The Hardware Design Guide** carries the rest in a new §17: board projects, product versus revision versus assembly variant, shared boards, project-local libraries and nicknames, naming inside the project, the title-block field table, the ignore policy, documentation and mechanical ownership, licensing practice including a SHOULD for PCB license marking, and the migration rule.

## Rationale

The license is a Platform decision because its value is uniformity: a footprint, a model or a protection front-end moves between two AURIORA boards only when both carry the same license, and one license gives one wording for every title block and every silkscreen. Weak reciprocity is the one variant that serves both halves of the Platform's purpose — the AURIORA designs stay open and improved, and other people can build on them without giving up their own work.

The structure decisions are small individually and all point the same way: decide once at creation what would otherwise be decided under pressure later. `boards/` for a single board costs one directory level; adding it when the second board arrives costs a move of a live project. Outputs in the release rather than the tree keep the source tree a source tree, and the release is already the immutable package AES requires.

## Consequences

- AES gains `AES-OH-004`; Maturity and Release §6's layout and release bullets are rewritten; Naming and Identity §4 gains the board-directory sentence.
- **Released within AES `0.12.0`**, a MINOR release: additive, nothing Released behind it. The two existing license practices — CC BY-SA 4.0 for the standards, CERN-OHL-W-2.0 for the one hardware repository — are unchanged by the rule; it records them.
- The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) `0.9.0` adds §17 and a project setup checklist.
- Existing hardware repositories migrate under the guide's §17.9: when substantial work begins, without moving history for cosmetic reasons.

## Scope and Remaining Open Items

**Settled by this record:** the hardware and documentation default licenses; the hardware repository layout; the board directory naming pattern; outputs attached to releases; the title-block identity fields.

**Open — Platform decisions:**

- **Copyright holder wording.** The CERN-OHL notice form expects a copyright line naming a holder; `AURIORA` is a project, not a legal person. The holder string used in READMEs and notices is decided before the first hardware release.
- **Default license for firmware and software.** Recorded when the first firmware or software repository releases; the current practice on the organization's web and profile repositories is MIT.
- **Shared AURIORA KiCad library.** Whether and where a canonical library of reusable symbols, footprints and circuit blocks is maintained as its own repository; the guide already defines how a board consumes it.

**Open — product decisions, recorded with each repository:** which boards a Product Family's repository holds; the exact silkscreen placement of the license marking; grandfathered structure in existing repositories.

## Affected Requirements / Documents

- [Maturity and Release §2.3](../07-maturity-and-release.md#aes-oh-004-default-licenses) — `AES-OH-004` (new); [§6](../07-maturity-and-release.md#6-repositories-and-workflow) — layout and release bullets.
- [Naming and Identity §4](../04-naming-and-identity.md#4-public-names) — board directory naming.
- `STANDARD.md`, `CHANGELOG.md`.
- Hardware Design Guide §2, §15, §16, §17 (new).

## Future Review Criteria

Revisit if: a hardware repository needs a different license for a documented reason, which is the EDR-named exception rather than a change of default; a shared KiCad library repository is created and needs a license or structure rule of its own; or KiCad's project or library file model changes in a way that makes the guide's §17 mapping inaccurate.
