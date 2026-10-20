# 06 EEPROM Metadata Specification

**Document ID:** AES-EEPROM
**Status:** Normative
**Depends On:** [Architecture](./03-architecture.md), [Interfaces and Versioning](./05-interfaces-and-versioning.md)

## 1. Purpose

AES EEPROM metadata provides machine-readable identity and compatibility data for replaceable Units. It is the default electronic identity contract required by [AES-UNIT-001](./03-architecture.md#aes-unit-001-electronic-identity) for Released replaceable Units.

The record is the **Unit identity record**: the Unit controller serves it over the Unit Link in the discovery state ([`UIF-RS485-4` §6–7](./interfaces/uif-rs485-4.md#6-discovery-activation-and-recovery)), and whether the controller holds it in an EEPROM, in its own nonvolatile memory or elsewhere is Unit-internal. The chapter keeps its name and its binary layout from the profiles on which a host read the EEPROM directly ([EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md)).

**Applicability:** this specification binds Units that carry AES EEPROM identity and the Modules that read it. Experimental Units may omit identity entirely or use a draft layout — marked as such — without any exception paperwork.

## 2. Logical Data Model

The metadata SHALL be encoded in a deterministic binary layout or a documented structured encoding preserving these fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| Magic | `u32` | Yes | ASCII `AURM` (`0x4155524D`). |
| Schema Version | `u16.major`, `u16.minor` | Yes | EEPROM schema version. |
| Header Length | `u16` | Yes | Bytes from start through fixed header. |
| Total Length | `u16` | Yes | Bytes used by all metadata. |
| Unit AOID | fixed ASCII | Yes | Unit object identifier. |
| Unit Interface AOID | fixed ASCII | Yes | Required Unit Interface family. |
| Unit Interface Version | `u16.major`, `u16.minor` | Yes | Interface version implemented by Unit. |
| Hardware Revision | fixed ASCII | Yes | Hardware revision string. |
| Serial Number | fixed ASCII | Yes | Physical instance serial. |
| Manufacture Date | `YYYYMMDD` | Yes | Manufacturing date. |
| Capabilities | bitset/TLV | Yes | Declared features and limits. |
| Calibration Record ID | fixed ASCII/TLV | Conditional | Required when Unit function depends on calibration. |
| Payload CRC | `u32` | Yes | CRC over metadata excluding CRC field. |

## 3. Normative Requirements

### AES-EEPROM-001: Required Identity Fields

**Requirement:** Unit EEPROM metadata SHALL contain magic, schema version, Unit AOID, Unit Interface AOID, Unit Interface version, hardware revision, serial number and CRC.

**Rationale:** These are the minimum fields for identity, compatibility and instance traceability.

### AES-EEPROM-002: Deterministic Validation Order

**Requirement:** Modules SHALL validate the Unit identity record in this order before enabling dependent functions: port power and link availability, an answer to the identity request, magic, length bounds, CRC, schema compatibility, AOID format, Unit Interface (profile) compatibility, Unit API compatibility, Unit capability limits, power validation, calibration validity where applicable. The Unit has no dedicated presence signal; physical presence is established by a valid answer to the identity request, not as a separately known step before it.

**Rationale:** A deterministic validation order produces consistent faults and safer default behavior. Presence is discovery: there is nothing to check before the link answers.

### AES-EEPROM-003: Forward-Compatible Extensions

**Requirement:** Extensions SHALL use length-delimited fields or TLV records. Readers SHALL ignore unknown optional extension records after validating length and CRC. Mandatory new fields force a major schema version.

**Rationale:** Units and Modules evolve independently; optional data must not break older compliant readers.

### AES-EEPROM-004: Calibration Reference Integrity

**Requirement:** If Unit behavior depends on calibration, EEPROM metadata SHALL contain either calibration constants with schema version and units, or a calibration record identifier resolving to an immutable calibration record.

**Rationale:** Measurements and stimulation values are not credible without traceable calibration.

### AES-EEPROM-005: Writable Field Control

**Requirement:** Production Unit identity fields SHOULD be write-protected after manufacturing verification. Writable runtime fields SHALL be separated from immutable identity fields.

**Rationale:** Identity is only useful if it cannot drift accidentally.

### AES-EEPROM-006: Binary Header Compatibility

**Requirement:** Units using the standard binary layout SHALL implement the offsets in Section 4 exactly for schema major version 1.

**Rationale:** Fixed offsets simplify low-resource discovery and production programming.

### AES-EEPROM-007: Metadata Trust Model

**Requirement:** Modules SHALL treat EEPROM metadata as unauthenticated input. The CRC is an integrity check, not proof of origin. Module-level safety limits SHALL be enforced regardless of what a Unit declares. Applications where counterfeit or tampered Units are a credible risk SHOULD document additional verification.

**Rationale:** A corrupted, cloned or maliciously programmed EEPROM can claim anything; the Module must remain safe even when the metadata lies.

### AES-EEPROM-008: Profile and API Metadata

**Requirement:** Where a Unit declares its Unit Interface Profile, Unit API or power characteristics electronically, it SHALL do so through optional, versioned TLV extension records (per [AES-EEPROM-003](#aes-eeprom-003-forward-compatible-extensions)), not by expanding the fixed header. The following optional fields are defined for this purpose:

| Field | Purpose |
|---|---|
| Unit Interface Profile Identifier | The profile the Unit implements (e.g. `UIF-RS485-4`). |
| Unit Interface Profile Version | `MAJOR.MINOR` of the implemented profile. |
| Unit API Identifier | Unit API family identifier. |
| Unit API Version | `MAJOR.MINOR` of the Unit API. |
| Capability Flags | Declared features and supported operations. |
| Required / Supported Input Voltage | Required input voltage or supported voltage range. |
| Maximum Startup Current | Worst-case current during Unit start-up. |
| Startup Peak Duration | How long the Unit may draw more than its maximum operating current after *enable*. Informational. |
| Maximum Operating Current | Worst-case current in normal operation. |
| Nominal Operating Current | Typical current in normal operation, for energy and runtime estimation. Informational. |
| Maximum Discovery-State Current | Worst-case current drawn from `UIF_PWR_VIN` while the functional domain is disabled, before *enable*. |

These extension records are optional at the schema level, but they become mandatory when the Unit's interface profile requires them. A Unit SHALL provide the Unit Interface Profile identifier and version, the Unit API identifier and version, capability flags, and all applicable power requirement fields the host needs to validate compatibility before *enable*. The execution-model and transport-address records of schema `1` drafts before AES `0.14.0` are withdrawn ([EDR-017](./edr/EDR-017-unit-link-profile-and-family-consolidation.md)): a profile has one execution model and no addressing, and a reader that meets either record ignores it as an unknown optional record.

Current fields are worst-case values in milliamperes and duration fields are in milliseconds, unless the record defines otherwise. The two fields marked informational describe expected rather than bounding behavior: they exist so a host that wants to estimate energy, log consumption or size a battery has better data than a worst-case figure. A host SHALL NOT substitute an informational field for a worst-case field in any decision that enforces a limit or authorizes power.

A host SHALL be able to reject a Unit whose profile or API version it does not support before sending *enable*, and SHALL verify the Unit's power metadata against its port's capability before sending *enable* (see [AES-UNIT-007](./03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)). Unknown optional records remain forward-compatible per [AES-EEPROM-003](#aes-eeprom-003-forward-compatible-extensions).

**Rationale:** Profile, API and power draw are exactly the facts a host needs to decide *before* enabling a Unit. Keeping the records optional at schema level preserves older readers, while making them mandatory per profile guarantees the host actually gets what it needs to validate a Unit.

## 4. Standard Binary Header

The default layout for small EEPROMs. Multibyte integers are little-endian.

| Offset | Size | Field |
|---:|---:|---|
| 0 | 4 | Magic `AURM` |
| 4 | 2 | Schema major |
| 6 | 2 | Schema minor |
| 8 | 2 | Header length |
| 10 | 2 | Total length |
| 12 | 48 | Unit AOID, NUL-padded ASCII |
| 60 | 48 | Unit Interface AOID, NUL-padded ASCII |
| 108 | 2 | Unit Interface major |
| 110 | 2 | Unit Interface minor |
| 112 | 16 | Hardware revision, NUL-padded ASCII |
| 128 | 32 | Serial number, NUL-padded ASCII |
| 160 | 4 | Manufacture date as `YYYYMMDD` BCD |
| 164 | 4 | Payload CRC32 |
| 168 | variable | TLV extension records |

## 5. Design Trade-offs

AES rejects human-label-only identity because it cannot support runtime compatibility decisions, and rejects Module-specific ID tables because they require source changes for replacement. The chosen model gives low-resource hardware a fixed identity header with forward-compatible TLV extension.
