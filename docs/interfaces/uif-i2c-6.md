# AURIORA UIF-I2C-6 Unit Interface Profile

**Profile Identifier:** `UIF-I2C-6`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md), [Architecture](../03-architecture.md)

This is a versioned [Unit Interface Profile](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles). The profile-independent rules — `UIF_` signal semantics, `UIF_READY` behavior, discovery and activation ([AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)), and profile versioning ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)) — apply and are not repeated here. This file defines only what is specific to `UIF-I2C-6`.

## 1. Purpose

`UIF-I2C-6` is the small, low-pin-count Unit Interface profile intended for **Passive Units** and simple I²C-based Units: sensor, identity and low-power functional Units that the host Module drives directly and that need only discovery, power control and a readiness indication.

## 2. Pin Assignment

Six signals:

| Pin | Signal | Direction (host view) | Description |
|---:|---|---|---|
| 1 | `UIF_PWR_VIN` | Host → Unit | Unit input power. Powers the EEPROM and minimum discovery circuitry at all times; powers functional circuitry only when the Unit's local switch is enabled by `UIF_PWR_EN`. |
| 2 | `GND` | — | Ground reference. |
| 3 | `UIF_I2C_SCL` | Host → Unit | Discovery/identity I²C clock. |
| 4 | `UIF_I2C_SDA` | Bidirectional | Discovery/identity I²C data. |
| 5 | `UIF_PWR_EN` | Host → Unit | Enables the Unit's functional power domain locally (load switch or regulator enable). LOW until the host has validated compatibility and power. |
| 6 | `UIF_READY` | Unit → Host | Active-HIGH functional-ready indication. For a Passive Unit this may be derived from the switched functional power domain via a hardware pull-up or equivalent. |

These six signals SHALL NOT change unless an existing electrical conflict is found and documented; such a change is versioned per [AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles).

## 3. Electrical Layer

Concrete electrical limits — logic levels, `UIF_PWR_VIN` voltage, current limits, `UIF_PWR_EN` drive, `UIF_READY` pull-up value and thresholds, leakage, ESD protection and hot-plug behavior — are defined here when this profile is realized on specific hardware. This profile is **Draft**: it constrains only the signal set and its meaning until these limits are finalized (see [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness)). It SHALL NOT be marked Normative or promoted to a `1.0` release until its connector family, mechanical keying, voltage limits, current limits, logic thresholds, timing requirements, ESD protection, hot-plug behavior and other required electrical and mechanical constraints are finalized.

**OPEN — needs hardware decision:** connector family/part number, mechanical format and keying, and the concrete current/timing numbers and VIN tolerance band.

### First hardware realization (AEU-01)

The first Unit realizing this profile is the AURIORA Environmental Sensor Unit (`AOID:PUB:UNIT:ENV:AEU:001`). Its power decisions inform, but do not yet finalize, the profile electrical layer:

- `UIF_PWR_VIN`: nominally **+3V3**. The Unit carries no on-board regulator; the functional rail is `UIF_PWR_VIN` minus the reverse-protection FET drop. A host on this profile SHALL supply 3V3-class VIN until a wider range is fixed here.
- The Unit's absolute-maximum ratings are governed by the post-protection rail, not by an internal regulator. Hosts SHALL NOT exceed the VIN range the Unit's EEPROM power metadata declares.

These numbers are AEU-01-specific and are **not yet profile-normative**. Promotion to a normative range (with tolerance, current limits and logic thresholds) is required before `UIF-I2C-6` leaves Draft (see [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness)).

Baseline rules that apply regardless of the numbers:

- The Unit locally switches its functional power from `UIF_PWR_EN`; the connector provides no separate discovery-power pin.
- Disabled Unit circuitry MUST NOT be back-powered through `UIF_I2C_SCL`, `UIF_I2C_SDA` or `UIF_READY` while `UIF_PWR_EN` is LOW.
- `UIF_READY` MUST have a defined LOW state when the Unit is absent, disabled, starting or faulty.

## 4. Communication Layer

Discovery and identity use I²C on `UIF_I2C_SCL`/`UIF_I2C_SDA`. The Unit EEPROM and its address range, and the metadata layout, follow [EEPROM Metadata](../06-eeprom-metadata.md). Functional communication for a Passive Unit is host-driven over the same I²C bus per the Unit's own device documentation; `UIF-I2C-6` standardizes discovery and activation, not the Unit's functional register map.

## 5. Identity and Discovery

Presence is established by successful EEPROM discovery ([AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order)); there is no presence pin. A Unit on this profile SHOULD declare execution model, profile identifier `UIF-I2C-6`, profile version and power characteristics via the optional TLV fields of [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata).

## 6. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | Connector, keying and pinout per Section 2 (connector part OPEN). | Fit and insertion test once the connector is chosen. |
| Electrical | Per Section 3 once numbers are fixed. | Power-limit, overcurrent and back-power tests. |
| Communication | I²C discovery + EEPROM read succeeds before `UIF_PWR_EN`. | Bus scan and metadata read test. |
| Semantic | Host validates descriptor, then asserts `UIF_PWR_EN`, then waits `UIF_READY`. | Valid, incompatible and invalid-EEPROM Unit tests. |

## 7. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft: six-signal Passive/simple-I²C Unit Interface; signal set and meaning defined, electrical and mechanical limits left open. | Not release-binding |
