# ADR-003: EEPROM Metadata as Unit Identity Contract

## Status

Accepted

## Context

Replaceable Units are central to AURIORA. Physical interchangeability alone is insufficient because Units may differ in electrical limits, calibration, interface revision and safety behavior. Manual labels and documentation are useful but cannot provide deterministic runtime compatibility checks.

## Decision

AES makes electronic Unit identification mandatory when replaceability affects electrical behavior, data interpretation, safety, calibration or compatibility. The default mechanism is AES EEPROM metadata containing AOID, Unit Interface version, serial number, hardware revision, CRC and calibration reference where applicable.

## Consequences

Units require additional design, programming and production verification. The benefit is deterministic discovery, safer replacement, traceable calibration and better automated test coverage.

## Affected Requirements

- [AES-UNIT-001](../03-architecture.md#aes-unit-001-electronic-identity)
- [AES-UNIT-003](../03-architecture.md#aes-unit-003-replaceability-without-source-modification)
- [AES-EEPROM-001](../06-eeprom-metadata.md#aes-eeprom-001-required-identity-fields)
- [AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order)
