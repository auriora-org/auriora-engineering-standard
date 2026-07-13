# Changelog

All notable changes to the AURIORA Engineering Standard (AES) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). AES releases use semantic versioning as required by [AES-VER-001](./docs/05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts): `MAJOR` for incompatible normative change, `MINOR` for backward-compatible normative addition, `PATCH` for clarification or defect correction. Entries record normative changes with their requirement identifiers; editorial changes are either omitted or explicitly marked as editorial, per [AES-GOV-011](./docs/08-decisions-and-governance.md#aes-gov-011-standard-change-record).

## [1.0.0] - 2026-07-13

First release of the AURIORA Engineering Standard.

### Added

- `STANDARD.md`: scope, requirement language (MUST/SHOULD/MAY scaled by applicability and maturity), the three-level maturity model (Experimental, Active Development, Released), conformance, the primary architecture diagram and reuse decision tree, and the foundation governance rules `AES-GOV-001`–`AES-GOV-003`.
- Nine canonical chapters: Principles, Terminology, Architecture (Platform, Module, Controller, Unit design), Naming and Identity (family identifiers, product numbers, revisions, serials, AOIDs, document IDs), Interfaces and Versioning, EEPROM Metadata, Maturity and Release, Decisions and Governance, Review Checklists.
- Fixed historical decisions `AES-HIST-001`–`AES-HIST-006` preserving platform-first architecture, Controller/Module separation, replaceable Units, interface contracts, documentation-as-product and stable family identity.
- Architectural Decision Records (`ADR-001`–`ADR-003`) and Engineering Decision Records (`EDR-001`–`EDR-002`).
- Document index and worked Module lifecycle example.
- Two review checklists (general engineering and release); domain-specific checklists delegated to the companion guides.
- CC BY-SA 4.0 license and contributing policy.
- Companion standards and guides linked from the handbook: [AURIORA Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) (`AHDG`), [AURIORA Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) (`AFSG`), [AURIORA Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) (`ASSG`) and [AURIORA Documentation Standard](https://github.com/auriora-org/auriora-documentation-standard) (`ADS`).
