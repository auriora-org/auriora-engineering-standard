# EDR-002: Unit Identity Is Electronic and Runtime-Discoverable

## Status

Accepted

## Context

AURIORA Units are replaceable. Replaceability affects compatibility, calibration, safety and data interpretation. Human labels and documentation are necessary but cannot support deterministic runtime checks.

## Alternatives Considered

| Alternative | Assessment |
|---|---|
| Human labels only | Cheap, but not machine-checkable and unsafe for automated compatibility. |
| Module-specific firmware tables | Works for one product, but requires source changes and blocks generic replacement. |
| Electronic metadata on Units | Adds production effort, but supports runtime discovery and traceability. |

## Decision

Units that affect electrical behavior, data interpretation, safety, calibration or compatibility SHALL provide electronic identity. AES EEPROM metadata is the default mechanism.

## Rationale

Runtime identity lets Modules reject incompatible Units, load correct calibration references and report clear Host Interface errors. This is central to AURIORA's repairability and scientific credibility.

## Consequences

Unit production must include metadata programming and verification. Modules must implement deterministic metadata validation before enabling dependent functions.

## Affected Requirements

- [AES-UNIT-001](../03-architecture.md#aes-unit-001-electronic-identity)
- [AES-EEPROM-001](../06-eeprom-metadata.md#aes-eeprom-001-required-identity-fields)
- [AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order)

## Future Review Criteria

Revisit if an alternative identity mechanism provides equal or stronger runtime discoverability, traceability, write protection and compatibility semantics with lower implementation burden.
