# 07 Maturity and Release

**Document ID:** AES-REL
**Status:** Normative
**Depends On:** [STANDARD](../STANDARD.md), [Interfaces and Versioning](./05-interfaces-and-versioning.md)
**Supersedes:** AES-MTC (Manufacturing, Testing and Calibration), AES-RLQ (Release, Lifecycle, Quality Assurance and Open Hardware), AES-WORKFLOW (Repository and Workflow Standard), AES-CONF (Conformance Standard)

## 1. Purpose

This chapter defines the three maturity levels in detail: what documentation, review and evidence each level expects, and what a Released artifact must provide.

Guiding rule: create enough documentation to understand, continue, test and reproduce the work — never documentation whose maintenance costs more than the risk it reduces.

## 2. Maturity Levels

### AES-LIFE-001: Maturity Declaration

**Requirement:** Every AURIORA repository SHALL state its maturity level (Experimental, Active Development, Released, Deprecated or Retired) in its README, honestly.

**Rationale:** This is the single cheapest piece of process in AES and the one everything else scales from. A reader must be able to tell an idea from a shipped product.

### 2.1 Experimental

For feasibility studies, test boards, breadboards, temporary firmware, internal tools, one-off experiments and early prototypes.

**Expected (the whole list):**

- source files
- a short README (or equivalent project note): what this is, its purpose and status
- important pinouts or interfaces, where applicable
- known hazards and critical operating constraints
- a license
- brief notes for non-obvious decisions, when useful

**Explicitly not required:** CHANGELOG, ADRs/EDRs, conformance declarations, manufacturing packages, review evidence, registers, document IDs, release notes, CI, unit-test coverage targets, separate architecture/design/testing/interface documents.

Experimental work may be incomplete, rough or temporary. The only hard obligations that always apply are the safety rules ([AES-MOD-004](./03-architecture.md#aes-mod-004-safety-policy-ownership), [AES-CTRL-002](./03-architecture.md#aes-ctrl-002-deterministic-startup), [AES-IF-007](./05-interfaces-and-versioning.md#aes-if-007-safe-default-state), [AES-UNIT-004](./03-architecture.md#aes-unit-004-declared-limits)) and honest status.

### 2.2 Active Development

For real AURIORA Modules and applications under development, prototypes expected to become public, iterating hardware revisions, and maintained firmware and software.

**Expected — only information that actively helps engineering:**

- a useful README
- editable source files
- current interface or connector information
- important design notes, known issues and limitations
- build or programming instructions, where applicable
- BOM for hardware, where applicable
- basic bring-up or test notes
- licensing information

### AES-REL-004: Living Design Notes

**Requirement:** Active Development projects SHALL keep their engineering knowledge in version control, but SHALL NOT be forced to split it into many separate documents. A single living document — `docs/design-notes.md`, a project notebook or equivalent — MAY hold significant decisions, open questions, test observations, revision notes, temporary deviations and future work.

**Rationale:** One honest living document that gets updated beats ten mandated documents that go stale. No formal approval record is needed for routine engineering judgment.

### 2.3 Released

For tagged public releases, hardware intended to be reproducible by others, stable interfaces, manufacturing packages, and firmware or software distributed for external use.

### AES-REL-001: Release Completeness

**Requirement:** A Released artifact SHALL be published as an immutable tag (or equivalent) containing, *where applicable to the artifact*:

- editable sources and reproducible build information
- generated manufacturing outputs and final BOM (hardware)
- firmware/software sources and binaries with build traceability (commit, toolchain, hash)
- documented interfaces and declared compatibility (versions, not adjectives)
- essential test evidence for critical functions
- known limitations
- release notes or changelog where the repository has consumers
- licensing information
- safety information, where hazards exist
- calibration information, where calibration is part of the product
- compatibility information, where external integrations depend on it

Requirements are conditional on the nature of the project: a board without calibration needs no calibration records, a small script needs no architecture document, firmware without an RTOS needs no RTOS documentation, an internal fixture needs no user-facing product documentation, a repository that has never released needs no changelog.

**Rationale:** A public release is a reproducibility promise. Another competent engineer must be able to understand, build, program, test and identify the artifact from the tag alone.

### AES-OH-003: Scientific and Safety Claims

**Requirement:** Public documentation SHALL distinguish engineering capability from validated scientific, diagnostic, therapeutic or safety claims.

**Rationale:** AURIORA supports biological research; engineering documentation must not overclaim validation.

### AES-OH-002: License Declaration

**Requirement:** Every public repository SHALL declare its license(s) explicitly; where hardware, firmware and documentation carry different licenses, each SHALL be stated.

**Rationale:** Ambiguity discourages reuse and contribution.

## 3. Deprecation and Retirement

### AES-LIFE-002: Deprecation Policy

**Requirement:** Deprecating a Released artifact SHALL include reason, replacement path (or explicit no-replacement rationale), affected versions and known risks. Retired artifacts SHALL remain reachable through version control history and tags — never silently deleted.

**Rationale:** Old hardware, calibration records and manufacturing evidence stay relevant long after active support ends.

## 4. Manufacturing, Testing and Calibration

These rules apply to Released artifacts (and to any prototype batch handed to an external manufacturer).

### AES-MFG-001: Manufacturing Package

**Requirement:** Hardware Released for reproduction SHALL have an immutable manufacturing package: source revision, generated manufacturing files, BOM with approved substitutions, assembly notes, programming files and inspection criteria, identified by a package version.

**Rationale:** Production cannot be repeated from loosely collected files. During prototyping, regenerating outputs from a tagged commit is the lightweight equivalent.

### AES-MFG-002: Substitution Control

**Requirement:** For Released hardware, component substitutions SHALL be classified (form-fit-function equivalent / electrically equivalent with review / calibration-impacting / firmware-impacting / prohibited) and calibration- or safety-impacting substitutions SHALL rerun the affected tests. Prototype substitutions need only a BOM or design-note entry.

**Rationale:** Uncontrolled substitution silently changes performance.

### AES-MFG-003: Production Programming Records

**Requirement:** Production programming of Released artifacts SHALL record firmware version and hash, programmed identity (AOID/serial), and EEPROM CRC verification.

**Rationale:** Traceability links physical artifacts to release and calibration evidence.

### AES-TEST-001: Release Test Evidence

**Requirement:** A Released Module, Controller or Unit SHALL have test evidence covering its critical functions and safety behavior, including negative tests where failure is dangerous (invalid metadata, missing Unit, power fault, communication timeout — as applicable). Test results for a release SHALL be archived with version and date. A requirement-by-requirement traceability matrix is NOT required.

**Rationale:** "Tested and works" is not evidence; a full compliance matrix is more paperwork than a small team's risk justifies. Test what can hurt, record what you tested.

### AES-CAL-001: Calibration Applicability

**Requirement:** Designs whose outputs or measurements depend on characterization SHALL declare whether calibration is required, optional or not applicable — before Release, with method and validity conditions documented where required. Calibration records SHALL identify serial, hardware revision, schema version, equipment, conditions, results and date, and systems SHALL define behavior for missing, expired or mismatched calibration (fail visibly, never silently fall back).

**Rationale:** Calibration cannot be retrofitted responsibly after data has been collected; silent use of invalid calibration produces scientifically false results.

## 5. Reviews

Reviews exist to catch real failures, not to produce evidence. The consolidated checklists are in [Review Checklists](./09-review-checklists.md).

### AES-QA-001: Proportionate Review

**Requirement:** Before manufacturing hardware and before any Release, the work SHALL be reviewed against the applicable checklist. When only one developer is available, self-review satisfies this requirement — preferably after a short time separation. Independent review SHOULD be obtained, where a qualified reviewer is available, for: safety-critical designs, mains or hazardous voltage, high-energy batteries, RF compliance, externally released stable interfaces, production manufacturing, and security-sensitive update systems.

**Rationale:** A standard that pretends organizational separation exists gets ignored. Honest self-review with a checklist beats fictional independent review. Not every checklist item needs an explicit N/A mark — skip what plainly does not apply.

There are no mandatory Concept/Architecture/Interface/Implementation/Manufacturing/Release gate sequences and no Architecture Freeze milestone. Their surviving intent: think about architecture and interfaces *before* PCB layout and enclosure tooling make them expensive to change, and stabilize identifiers by Release ([AES-NAME-001](./04-naming-and-identity.md#aes-name-001-family-identifier-stability)).

## 6. Repositories and Workflow

All non-normative guidance:

- Suggested layout for hardware/firmware repositories: `README.md`, `docs/`, `hardware/`, `firmware/`, `mechanical/`, `manufacturing/`, `tests/`, `tools/` — use what applies, omit the rest. Very small projects may keep everything at the root. Just don't hide manufacturing files in `misc/final/new/`.
- Direct commits to the main branch are fine for Experimental work and for a single maintainer. Branches and pull requests are recommended for meaningful Active Development changes — they produce a reviewable record — but no approval board, second reviewer or compliance officer is assumed to exist.
- The maintainer may design, implement, review and document the same change.
- Releases: freeze the source, regenerate all generated outputs from the tagged revision (never hand-edit outputs), run the release checklist, tag, and verify the tag's links resolve.
