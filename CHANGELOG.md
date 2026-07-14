# Changelog

All notable changes to the AURIORA Engineering Standard (AES) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). AES releases use semantic versioning as required by [AES-VER-001](./docs/05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts): `MAJOR` for incompatible normative change, `MINOR` for backward-compatible normative addition, `PATCH` for clarification or defect correction. Entries record normative changes with their requirement identifiers; editorial changes are either omitted or explicitly marked as editorial, per [AES-GOV-011](./docs/08-decisions-and-governance.md#aes-gov-011-standard-change-record).

## [1.1.0] - 2026-07-14

### Added

- Unit execution models: `Passive Unit` and `Managed Unit` defined as execution models of a Unit (not new top-level objects), with `Unit API` and `Unit Interface Profile` as supporting terms (Terminology §3). New requirements `AES-UNIT-006` (declared execution model, discoverable capabilities/API version) and `AES-UNIT-007` (deterministic discovery→validate→`UIF_PWR_EN`→wait `UIF_READY`→communicate sequence) in Architecture §5.
- Unit Interface signal and profile model (Interfaces and Versioning §3.1): the `UIF_` prefix defined as *AURIORA Unit Interface*, the standard `UIF_` signal set, active-HIGH `UIF_READY` semantics, and a prohibition on any Unit-presence pin (`UIF_PRESENT`/`UIF_PRESENT_N`) — presence is EEPROM discovery. New requirement `AES-IF-008` (named, independently versioned Unit Interface Profiles; hosts reject unsupported profiles/versions).
- EEPROM optional TLV fields for execution model, Unit Interface Profile identifier/version, Unit API identifier/version, capability flags and power characteristics (required voltage, startup/operating/discovery-state current), via new requirement `AES-EEPROM-008` layered on the existing TLV extension mechanism (`AES-EEPROM-003`) — no fixed-header expansion.
- Versioned Unit Interface Profile specifications under `docs/interfaces/`: `AURIORA UIF-I2C-6` (Draft, six-signal profile for Passive/simple-I²C Units) and the `AURIORA Managed SPI Profile` (Draft). Both define the signal set and semantics; connector, pin count and electrical/mechanical limits are left as explicit open hardware decisions, so both remain Draft until finalized. Indexed from `STANDARD.md` and the Document Index.
- `UIF-I2C-6` §3 records the first hardware realization (AEU-01, `AOID:PUB:UNIT:ENV:AEU:001`) seeding the electrical layer with a nominal `UIF_PWR_VIN` of +3V3; these values are AEU-01-specific and not yet profile-normative. The AOID is registered provisionally in the Document Index AOID table.

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
