# ADR-002: Stable Object Identifier Scheme

## Status

Accepted

## Context

Human-readable names change as designs mature. Repository names may change when ownership or packaging changes. Serial numbers identify physical instances, not design families. AURIORA needs a stable identifier that can appear in EEPROM metadata, calibration records, compatibility matrices, manufacturing packages and release notes.

## Decision

AES defines AURIORA Object Identifiers using the `AOID:<NAMESPACE>:<CLASS>:<DOMAIN>:<FAMILY>:<SERIES>` format. AOIDs identify design families and interface families, while serial numbers identify physical instances.

## Consequences

The Platform must maintain an AOID registry or equivalent review practice to prevent collisions. The benefit is stable traceability across documents, firmware, manufacturing and calibration even when public names evolve.

## Affected Requirements

- [AES-ID-006](../04-naming-and-identity.md#aes-id-006-aoid-assignment)
- [AES-ID-008](../04-naming-and-identity.md#aes-id-008-serial-numbers)
- [AES-EEPROM-001](../06-eeprom-metadata.md#aes-eeprom-001-required-identity-fields)
