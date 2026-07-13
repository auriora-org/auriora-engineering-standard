# Interface Contract Template

This template is a worked skeleton. Replace the example values with the new interface values during interface creation; do not leave the example values in a released contract.

**Interface AOID:** `AOID:PUB:UIF:GEN:APEM:001`  
**Name:** `AURIORA Generic Service Unit Interface`  
**Version:** `1.0`  
**Status:** `Draft`  
**Applies To:** `Replaceable low-power sensor and identity Units`

## 1. Purpose

State what interoperability problem this interface solves.

## 2. Physical Layer

Define connector, cable, orientation, keying, retention, envelope constraints and keep-outs.

## 3. Electrical Layer

Define voltage levels, current limits, signal directions, protection, sequencing, default states and hot-plug policy.

## 4. Communication Layer

Define bus/protocol, addresses, framing, timing, retries, reset behavior and unsupported-operation behavior.

## 5. Identity and Discovery

Define AOIDs, EEPROM metadata, capability discovery and invalid identity behavior.

## 6. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | Example: keyed 12-pin board-to-board connector, orientation enforced by connector body. | Fit check and insertion test. |
| Electrical | Example: 3.3 V logic, 5 V Unit power, 500 mA maximum. | Power-limit and overcurrent test. |
| Communication | Example: I2C at 100 kHz or 400 kHz, EEPROM at documented address range. | Bus scan and metadata read test. |
| Semantic | Example: Unit metadata declares capability records before Module enables dependent function. | Valid and incompatible Unit simulation. |
| Calibration | Example: calibration record required only for measurement Units. | Missing and stale calibration tests. |

## 7. Error Model

List structured error codes and recovery guidance.

## 8. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 1.0 | Initial release | Baseline |
