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
| `AES-EXAMPLE-MODULE-LIFECYCLE` | Worked Example (informative) | `examples/worked-example-module-lifecycle.md` |

## Unit Interface Profile Specifications

Concrete, independently versioned Unit Interface Profiles (see [AES-IF-008](./05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)):

| Profile | Version | Status | Source Path |
|---|---|---|---|
| `AURIORA UIF-I2C-6` | 0.1 | Draft | `docs/interfaces/uif-i2c-6.md` |
| AURIORA Managed SPI Profile | 0.1 | Draft | `docs/interfaces/managed-spi.md` |

## Companion Document IDs (reserved)

| Document ID | Title | Repository |
|---|---|---|
| `AHDG` | AURIORA Hardware Design Guide | [auriora-hardware-design-guide](https://github.com/auriora-org/auriora-hardware-design-guide) |
| `AFSG` | AURIORA Firmware Style Guide | [auriora-firmware-style-guide](https://github.com/auriora-org/auriora-firmware-style-guide) |
| `ASSG` | AURIORA Software Style Guide | [auriora-software-style-guide](https://github.com/auriora-org/auriora-software-style-guide) |
| `ADS` | AURIORA Documentation Standard | [auriora-documentation-standard](https://github.com/auriora-org/auriora-documentation-standard) |

## AOID Assignments

Released artifacts that participate in machine-readable identity need an AOID ([AES-ID-006](./04-naming-and-identity.md#aes-id-006-aoid-assignment)); assignments are listed here to prevent collisions. Pre-Release entries may appear provisionally so identifiers cited in draft specs are reserved.

| AOID | Artifact | Maturity |
|---|---|---|
| `AOID:PUB:UNIT:ENV:AEU:001` | AURIORA Environmental Sensor Unit (AEU-01); first realization of the `UIF-I2C-6` profile | Pre-Release (provisional) |
