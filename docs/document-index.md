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
| `AES-EEPROM` | Unit Identity Record (identifier and path historical: the record was an EEPROM until AES 0.14.0) | `docs/06-eeprom-metadata.md` |
| `AES-REL` | Maturity and Release | `docs/07-maturity-and-release.md` |
| `AES-GOV` | Decisions and Governance | `docs/08-decisions-and-governance.md` |
| `AES-CHECK` | Review Checklists | `docs/09-review-checklists.md` |
| `AES-REG-DOC` | Document Index | `docs/document-index.md` |
| `AES-EXAMPLE-MODULE-LIFECYCLE` | Worked Example: Module Lifecycle (informative) | `examples/worked-example-module-lifecycle.md` |
| `AES-EXAMPLE-AEL` | Worked Example: Multimodal AEL Experiment (informative) | `examples/worked-example-multimodal-ael-experiment.md` |
| `AES-EXAMPLE-AUTONOMOUS` | Worked Example: Unattended Field Deployment (informative) | `examples/worked-example-unattended-field-deployment.md` |

## Interface Specifications

The Unit Interface Profile (see [AES-IF-008](./05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles), [EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md)):

| Profile | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA UIF-RS485-4` | 0.1 | Draft | `docs/interfaces/uif-rs485-4.md` |

The withdrawn board-level profiles `UIF-I2C-6`, `UIF-MI2C-8` and `UIF-MSPI-14` are listed under Retired Identifiers; their files remain as notices.

The AURIORA Event Link (see [AES-AEL-001](./05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface)):

| Interface | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA AEL` | 0.2 | Draft | `docs/interfaces/ael.md` |

The Module Port and the Module Power Interface (see [AES-MOD-005](./03-architecture.md#aes-mod-005-external-interfaces-and-power-separation), [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md), [EDR-015](./edr/EDR-015-module-power-interface-limits-and-connector-reservation.md)):

| Interface | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA Module Port` | 0.1 | Draft | `docs/interfaces/module-port.md` |
| `AURIORA Module Power Interface` | 0.2 | Draft | `docs/interfaces/module-power.md` |

No **MCI transport binding** specification exists yet. The Module Control Interface ([AES-MCI-001](./05-interfaces-and-versioning.md#aes-mci-001-transport-independence)) is defined transport-independently; its bindings — a direct local transport and the Module Control Link (`MCL`) — are recorded as open items in [EDR-007](./edr/EDR-007-module-control-interface-and-module-hub.md) and will be listed here when specified; `MCL`'s connector and half-duplex single-pair model are already fixed by the Module Port specification ([EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md)). The direct local transport binding is also the host-facing interface of a Module Hub ([AES-HUB-003](./03-architecture.md#aes-hub-003-host-facing-interface-and-traffic-separation), [EDR-010](./edr/EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md)).

## Retired Identifiers

Identifiers that appeared in a released AES version and were withdrawn. They are reserved and are not reused for a different meaning ([AES-DOCID-001](./04-naming-and-identity.md#aes-docid-001-document-identifiers-for-standards)).

| Identifier | Was | Retired in | Replacement |
|---|---|---|---|
| `AES-SYNC-001` – `AES-SYNC-004` | Module Synchronization Interface requirements (Interfaces and Versioning §4, AES 0.6.0–0.7.1) | 0.8.0 | `AES-AEL-001` – `AES-AEL-005` ([EDR-008](./edr/EDR-008-auriora-event-link.md)) |
| `AES-EXAMPLE-SYNC` | Worked Example: Module Synchronization (informative) | 0.8.0 | `AES-EXAMPLE-AEL` |
| `AURIORA SYNC` (`docs/interfaces/sync.md`) | Module Synchronization Interface specification, 0.1 Draft | 0.8.0 | `AURIORA AEL` (`docs/interfaces/ael.md`); the file remains as a superseded notice |
| `AURIORA UIF-I2C-6` (`docs/interfaces/uif-i2c-6.md`) | Passive Unit Interface Profile, 0.1 Draft (AES 0.2.0–0.13.0) | 0.14.0 | `AURIORA UIF-RS485-4`; the Passive execution model withdrawn with it ([EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md)); the file remains as a withdrawn notice |
| `AURIORA UIF-MI2C-8` (`docs/interfaces/uif-mi2c-8.md`) | Low-bandwidth Managed Unit Interface Profile, 0.1 Draft (AES 0.5.0–0.13.0) | 0.14.0 | `AURIORA UIF-RS485-4` ([EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md)); the file remains as a superseded notice |
| `AURIORA UIF-MSPI-14` (`docs/interfaces/uif-mspi-14.md`) | Managed SPI Unit Interface Profile, 0.1 Draft (AES 0.2.0–0.13.0) | 0.14.0 | None — the high-bandwidth cell stays open ([AES-IF-010](./05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration)); the file remains as a withdrawn notice |
| `AES-EXAMPLE-UIF-SELECTION` | Worked Example: Choosing a Unit Interface Profile (informative) | 0.14.0 | None; the file remains as a withdrawn notice |
| `UIF_PWR_EN`, `UIF_READY`, `UIF_IRQ_N`, `UIF_RESET_N`, `UIF_I2C_*`, `UIF_SPI_*` | Discrete Unit Interface signals | 0.14.0 | The *enable*, *disable*, *ready* and *events pending* link states and the Unit Link `UIF_LINK_P`/`UIF_LINK_N` ([Interfaces and Versioning §3.1](./05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles)) |

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

## External Connector Register

Every external connector form a Platform device may carry is entered here before a design uses it ([AES-MOD-006](./03-architecture.md#aes-mod-006-external-connector-reservation)). *Reserved* forms serve one function only; *controlled* forms serve the listed functions under the listed condition; *unassigned* forms are assigned by EDR before use. Measurement-side connectors of other families are outside the register unless listed.

| Form | Device-side contact | Function | Status | Decided by |
|---|---|---|---|---|
| M8 A-coded 3-position | male / pin-contact, panel | Module Power Interface input (12 V DC) on every Module, Module Hub and other Platform device | Reserved — exclusive | [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md), [EDR-015](./edr/EDR-015-module-power-interface-limits-and-connector-reservation.md) |
| M8 A-coded 3-position | female / socket-contact, panel | Module Power Interface output of a power source; otherwise a measurement-side port (electrode, sensor, actuator) only, with the mis-mating analysis of the specification's Section 8 recorded and the port labeled with its function | Controlled | [EDR-015](./edr/EDR-015-module-power-interface-limits-and-connector-reservation.md) |
| M8 A-coded 3-position | male / pin-contact at both ends of a cable | None — no Platform cable | Prohibited | [EDR-015](./edr/EDR-015-module-power-interface-limits-and-connector-reservation.md) |
| M8 A-coded 8-position | female / socket-contact, panel | Module Port (`MCL`, AEL IN, AEL OUT) on a Module, a Hub's Module Ports and its Hub-to-Hub link ports | Reserved — exclusive | [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md) |
| M8 A-coded 8-position | male / pin-contact, cable | AURIORA Link Cable ends only; never a panel connector | Reserved | [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md) |
| M8 A-coded 4-position | female / socket-contact, panel | Unit Port (`UIF_PWR_VIN`, `GND`, Unit Link) on a Module or other Unit Interface Host | Assigned — exclusive | [EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md) |
| M8 A-coded 4-position | male / pin-contact, panel | Unit input on a Unit; never energized from inside | Assigned | [EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md) |
| M8 A-coded 4-position | male / pin-contact at the Module end, female / socket-contact at the Unit end, straight | Unit cable — the generic M8 4-position cordset | Assigned | [EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md) |
| M8 A-coded 4-position | same gender at both ends of a cable | None — no Platform cable | Prohibited | [EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md) |
| M12 | any | — ; candidate for a higher-power power profile | Unassigned | — |
| USB-C | receptacle | Direct local transport of a Module; host-facing interface of a Module Hub | Assigned | [EDR-010](./edr/EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md), [EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md) |

## AOID Assignments

Released artifacts that participate in machine-readable identity need an AOID ([AES-ID-006](./04-naming-and-identity.md#aes-id-006-aoid-assignment)); assignments are listed here to prevent collisions. Pre-Release entries may appear provisionally so identifiers cited in draft specs are reserved.

| AOID | Artifact | Maturity |
|---|---|---|
| `AOID:PUB:UNIT:ENV:AENU:001` | AURIORA Environmental Sensor Unit (AENU-01); first realization of the `UIF-RS485-4` profile ([EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md), superseding [EDR-005](./edr/EDR-005-low-bandwidth-managed-unit-interface.md)); re-registered from `AEU` ([EDR-014](./edr/EDR-014-four-letter-family-identifiers-and-register.md)) | Pre-Release (provisional) |
| `AOID:PUB:HUB:GEN:AHUB:001` | AURIORA Hub (AHUB-01); `MCL` concentrator, AEL router, host-facing interface, cascading ([EDR-013](./edr/EDR-013-mcl-cascading-and-path-addressing.md)) | Pre-Release (provisional) |
