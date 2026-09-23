# Document Index

**Document ID:** AES-REG-DOC
**Status:** Normative
**Depends On:** [Naming and Identity](./04-naming-and-identity.md)

This index records the AES documents and reserved companion document IDs, and hosts the AOID assignment list. Document IDs are stable identifiers ([AES-DOCID-001](./04-naming-and-identity.md#aes-docid-001-document-identifiers-for-standards)): once a document ID has appeared in a released artifact or record it is not reused for a different document family.

## Current AES Documents

| Document ID | Title | Source Path |
|---|---|---|
| `AES-INDEX` | AURIORA Engineering Standard | `STANDARD.md` |
| `AES-PHIL` | Principles | `docs/01-principles.md` |
| `AES-TERM` | Terminology | `docs/02-terminology.md` |
| `AES-ARCH` | Architecture | `docs/03-architecture.md` |
| `AES-NAME` | Naming and Identity | `docs/04-naming-and-identity.md` |
| `AES-IF` | Interfaces and Versioning | `docs/05-interfaces-and-versioning.md` |
| `AES-EEPROM` | EEPROM Metadata | `docs/06-eeprom-metadata.md` |
| `AES-REL` | Maturity and Release | `docs/07-maturity-and-release.md` |
| `AES-GOV` | Decisions and Governance | `docs/08-decisions-and-governance.md` |
| `AES-CHECK` | Review Checklists | `docs/09-review-checklists.md` |
| `AES-REG-DOC` | Document Index | `docs/document-index.md` |
| `AES-EXAMPLE-MODULE-LIFECYCLE` | Worked Example: Module Lifecycle (informative) | `examples/worked-example-module-lifecycle.md` |
| `AES-EXAMPLE-UIF-SELECTION` | Worked Example: Choosing a Unit Interface Profile (informative) | `examples/worked-example-unit-interface-profile-selection.md` |
| `AES-EXAMPLE-AEL` | Worked Example: Multimodal AEL Experiment (informative) | `examples/worked-example-multimodal-ael-experiment.md` |
| `AES-EXAMPLE-AUTONOMOUS` | Worked Example: Unattended Field Deployment (informative) | `examples/worked-example-unattended-field-deployment.md` |

## Interface Specifications

Concrete, independently versioned Unit Interface Profiles (see [AES-IF-008](./05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)):

| Profile | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA UIF-I2C-6` | 0.1 | Draft | `docs/interfaces/uif-i2c-6.md` |
| `AURIORA UIF-MI2C-8` | 0.1 | Draft | `docs/interfaces/uif-mi2c-8.md` |
| `AURIORA UIF-MSPI-14` | 0.1 | Draft | `docs/interfaces/uif-mspi-14.md` |

The AURIORA Event Link (see [AES-AEL-001](./05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface)):

| Interface | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA AEL` | 0.2 | Draft | `docs/interfaces/ael.md` |

The Module Port and the Module Power Interface (see [AES-MOD-005](./03-architecture.md#aes-mod-005-external-interfaces-and-power-separation), [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md)):

| Interface | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA Module Port` | 0.1 | Draft | `docs/interfaces/module-port.md` |
| `AURIORA Module Power Interface` | 0.1 | Draft | `docs/interfaces/module-power.md` |

No **MCI transport binding** specification exists yet. The Module Control Interface ([AES-MCI-001](./05-interfaces-and-versioning.md#aes-mci-001-transport-independence)) is defined transport-independently; its bindings — a direct local transport and the Module Control Link (`MCL`) — are recorded as open items in [EDR-007](./edr/EDR-007-module-control-interface-and-module-hub.md) and will be listed here when specified; `MCL`'s connector and half-duplex single-pair model are already fixed by the Module Port specification ([EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md)). The direct local transport binding is also the host-facing interface of a Module Hub ([AES-HUB-003](./03-architecture.md#aes-hub-003-host-facing-interface-and-traffic-separation), [EDR-010](./edr/EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md)).

## Retired Identifiers

Identifiers that appeared in a released AES version and were withdrawn. They are reserved and are not reused for a different meaning ([AES-DOCID-001](./04-naming-and-identity.md#aes-docid-001-document-identifiers-for-standards)).

| Identifier | Was | Retired in | Replacement |
|---|---|---|---|
| `AES-SYNC-001` – `AES-SYNC-004` | Module Synchronization Interface requirements (Interfaces and Versioning §4, AES 0.6.0–0.7.1) | 0.8.0 | `AES-AEL-001` – `AES-AEL-005` ([EDR-008](./edr/EDR-008-auriora-event-link.md)) |
| `AES-EXAMPLE-SYNC` | Worked Example: Module Synchronization (informative) | 0.8.0 | `AES-EXAMPLE-AEL` |
| `AURIORA SYNC` (`docs/interfaces/sync.md`) | Module Synchronization Interface specification, 0.1 Draft | 0.8.0 | `AURIORA AEL` (`docs/interfaces/ael.md`); the file remains as a superseded notice |

## Companion Document IDs (reserved)

| Document ID | Title | Repository |
|---|---|---|
| `AHDG` | AURIORA Hardware Design Guide | [auriora-hardware-design-guide](https://github.com/auriora-org/auriora-hardware-design-guide) |
| `AFSG` | AURIORA Firmware Style Guide | [auriora-firmware-style-guide](https://github.com/auriora-org/auriora-firmware-style-guide) |
| `ASSG` | AURIORA Software Style Guide | [auriora-software-style-guide](https://github.com/auriora-org/auriora-software-style-guide) |
| `ADS` | AURIORA Documentation Standard | [auriora-documentation-standard](https://github.com/auriora-org/auriora-documentation-standard) |

## Family Identifier Register

Every Product Family identifier is entered here before it appears in any artifact ([AES-NAME-001](./04-naming-and-identity.md#aes-name-001-family-identifier-stability)): `A`, two mnemonic letters, and the role letter `M` or `U`; infrastructure families are registered individually. An identifier once entered is never reused, whether current, renamed or retired.

| Identifier | Family | Role | Status | Derivation / note |
|---|---|---|---|---|
| `APEM` | AURIORA Plant Electrophysiology Module | Module | Allocated | `PE` + `M`; product APEM-01 |
| `APBM` | AURIORA Photobiology Module | Module | Allocated | `PB` + `M` |
| `AASM` | AURIORA Acoustic Stimulus Module | Module | Allocated | `AS` + `M`; renames `AAM` ([EDR-014](./edr/EDR-014-four-letter-family-identifiers-and-register.md)); AES text migrated; hardware marking, firmware and companion guides migrate before Release |
| `AENU` | AURIORA Environmental Sensor Unit | Unit | Allocated | `EN` + `U`; renames `AEU` ([EDR-014](./edr/EDR-014-four-letter-family-identifiers-and-register.md)); AES text and provisional AOID migrated; schematic, firmware and companion guides migrate before Release |
| `ASPU` | AURIORA Spectral Unit | Unit | Reserved | `SP` + `U` |
| `ASOU` | AURIORA Soil Unit | Unit | Reserved | `SO` + `U` |
| `AWNU` | AURIORA Wind Unit | Unit | Reserved | `WN` + `U` |
| `ACTU` | AURIORA Communication and Timing Unit | Unit | Reserved | `CT` + `U` |
| `AGEU` | AURIORA Geophysical Unit | Unit | Reserved | `GE` + `U` |
| `AHUB` | AURIORA Hub | Infrastructure | Allocated | registered individually; size variants are products (AHUB-01, AHUB-02, …), never encoded in the identifier |
| `AAM` | — | — | Retired 2026-09-23 | renamed to `AASM`; never reused |
| `AEU` | — | — | Retired 2026-09-23 | renamed to `AENU`; never reused |
| `ASU` | — | — | Retired 2026-09-23 | collided (Spectral / Soil); never reused |
| `AAC` | AURIORA Audio Controller | Controller | Retired 2026-09-23 | family discontinued; never reused |
| `AMH` | — | — | Retired 2026-09-23 | superseded by `AHUB` before any use; never reused |

## AOID Assignments

Released artifacts that participate in machine-readable identity need an AOID ([AES-ID-006](./04-naming-and-identity.md#aes-id-006-aoid-assignment)); assignments are listed here to prevent collisions. Pre-Release entries may appear provisionally so identifiers cited in draft specs are reserved.

| AOID | Artifact | Maturity |
|---|---|---|
| `AOID:PUB:UNIT:ENV:AENU:001` | AURIORA Environmental Sensor Unit (AENU-01); Managed Unit, first realization of the `UIF-MI2C-8` profile ([EDR-005](./edr/EDR-005-low-bandwidth-managed-unit-interface.md)); re-registered from `AEU` ([EDR-014](./edr/EDR-014-four-letter-family-identifiers-and-register.md)) | Pre-Release (provisional) |
| `AOID:PUB:HUB:GEN:AHUB:001` | AURIORA Hub (AHUB-01); `MCL` concentrator, AEL router, host-facing interface, cascading ([EDR-013](./edr/EDR-013-mcl-cascading-and-path-addressing.md)) | Pre-Release (provisional) |
