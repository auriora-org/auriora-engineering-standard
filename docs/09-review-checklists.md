# 09 Review Checklists

**Document ID:** AES-CHECK
**Status:** Normative
**Depends On:** [Maturity and Release](./07-maturity-and-release.md)

AES defines two checklists: one general engineering checklist and one release checklist. Domain-specific checklists live in the companion guides: hardware in the [AHDG](https://github.com/auriora-org/auriora-hardware-design-guide), firmware in the [AFSG](https://github.com/auriora-org/auriora-firmware-style-guide), software in the [ASSG](https://github.com/auriora-org/auriora-software-style-guide).

Usage: skip items that plainly don't apply — no N/A bookkeeping. Every real "no" is either fixed or consciously accepted with a one-line note in the design notes. Self-review is valid ([AES-QA-001](./07-maturity-and-release.md#aes-qa-001-proportionate-review)); leave a day between building and reviewing when you can.

## General Engineering Checklist

Use before manufacturing a board, merging a significant change, or releasing. One screen, by design.

- [ ] README states what this is and its maturity level, honestly
- [ ] Known hazards and critical operating constraints are written down
- [ ] Safety rules hold: outputs safe at startup and fault; Module enforces its own limits regardless of Unit claims
- [ ] Interfaces others depend on match their documentation (pinouts, commands, formats)
- [ ] Non-obvious decisions and known issues are noted in the design notes
- [ ] Someone else (or you, in six months) could continue this work from what is in the repository
- [ ] Nothing secret, generated or irreproducible is committed
- [ ] License present

## Release Checklist

Use additionally when tagging a Release ([AES-REL-001](./07-maturity-and-release.md#aes-rel-001-release-completeness)).

- [ ] Maturity set to Released; version and tag follow [AES-VER-001](./05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts)
- [ ] Editable sources included; generated outputs regenerated from the tagged revision
- [ ] Final BOM and manufacturing outputs included (hardware)
- [ ] Build reproducible from documented steps; binaries carry commit/toolchain/hash traceability
- [ ] Interfaces documented with versions; compatibility declared by version range, not adjectives
- [ ] Test evidence for critical functions and safety behavior archived
- [ ] Calibration method and records linked, where calibration applies
- [ ] Known limitations documented; release notes/changelog updated where the repo has consumers
- [ ] Licenses declared for all artifact types
- [ ] No unvalidated scientific, diagnostic or therapeutic claims
- [ ] Breaking changes have an EDR and migration notes ([AES-EDR-001](./08-decisions-and-governance.md#aes-edr-001-edr-trigger))
- [ ] Independent review obtained or consciously waived for the cases in [AES-QA-001](./07-maturity-and-release.md#aes-qa-001-proportionate-review)
