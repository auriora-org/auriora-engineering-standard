# 06 EEPROM Metadata Specification

**Document ID:** AES-EEPROM
**Status:** Normative
**Depends On:** [Architecture](./03-architecture.md), [Interfaces and Versioning](./05-interfaces-and-versioning.md)

## 1. Purpose

AES EEPROM metadata provides machine-readable identity and compatibility data for replaceable Units. It is the default electronic identity contract required by [AES-UNIT-001](./03-architecture.md#aes-unit-001-electronic-identity) for Released replaceable Units.

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

**Requirement:** Modules SHALL validate EEPROM metadata in this order before enabling dependent functions: physical presence, readable bus, magic, length bounds, CRC, schema compatibility, AOID format, Unit Interface compatibility, Unit capability limits, calibration validity where applicable.

**Rationale:** A deterministic validation order produces consistent faults and safer default behavior.

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
