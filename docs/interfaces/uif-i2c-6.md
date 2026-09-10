# AURIORA UIF-I2C-6 Unit Interface Profile

**Profile Identifier:** `UIF-I2C-6`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md), [Architecture](../03-architecture.md)

This is a versioned [Unit Interface Profile](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles). The profile-independent rules — `UIF_` signal semantics, `UIF_READY` behavior, discovery and activation ([AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)), and profile versioning ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)) — apply and are not repeated here. This file defines only what is specific to `UIF-I2C-6`.

## 1. Purpose

`UIF-I2C-6` is the small, low-pin-count Unit Interface profile intended for **Passive Units** and simple I²C-based Units: sensor, identity and low-power functional Units that the host Module drives directly and that need only discovery, power control and a readiness indication.

This profile is defined by its *management model*, not by its transport. A Unit that runs its own controller and exposes a versioned Unit API is a Managed Unit and belongs on [`UIF-MI2C-8`](./uif-mi2c-8.md) — the same I²C transport with an added generic event signal, a second ground and a distinct 8-position connector — or on [`UIF-MSPI-14`](./uif-mspi-14.md) where throughput or timing demands it. See the selection rule, [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection).

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

### Electrical baseline and first realization

The profile was originally seeded by the AURIORA Environmental Sensor Unit (`AOID:PUB:UNIT:ENV:AEU:001`, AEU-01). AEU-01 has since been reworked as a **Managed Unit** and now realizes [`UIF-MI2C-8`](./uif-mi2c-8.md) ([EDR-005](../edr/EDR-005-low-bandwidth-managed-unit-interface.md)), so `UIF-I2C-6` currently has no committed hardware realization; its electrical layer is finalized when the first Passive Unit on this profile is designed.

The working assumption carried across all UIF profiles remains:

- `UIF_PWR_VIN`: nominally **+3V3**. A host on this profile SHALL supply 3V3-class VIN until a wider range is fixed here, and SHALL NOT exceed the VIN range the Unit's EEPROM power metadata declares.

These values are **not yet profile-normative**. Promotion to a normative range (with tolerance, current limits and logic thresholds) is required before `UIF-I2C-6` leaves Draft (see [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness)).

Baseline rules that apply regardless of the numbers:

- The Unit locally switches its functional power from `UIF_PWR_EN`; the connector provides no separate discovery-power pin.
- Disabled Unit circuitry MUST NOT be back-powered through `UIF_I2C_SCL`, `UIF_I2C_SDA` or `UIF_READY` while `UIF_PWR_EN` is LOW.
- `UIF_READY` MUST have a defined LOW state when the Unit is absent, disabled, starting or faulty.

## 4. Communication Layer

Discovery and identity use I²C on `UIF_I2C_SCL`/`UIF_I2C_SDA`. The Unit EEPROM and its address range, and the metadata layout, follow [EEPROM Metadata](../06-eeprom-metadata.md) and the Platform address allocation rule [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation): the discovery EEPROM occupies `0x50`–`0x57`, and the Unit's functional devices SHALL respond outside that block. Functional communication for a Passive Unit is host-driven over the same I²C bus per the Unit's own device documentation; `UIF-I2C-6` standardizes discovery and activation, not the Unit's functional register map.

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
| 0.1 (Draft) | Clarification: scope stated as management-model-based (Passive/simple Units) with Managed Units directed to `UIF-MI2C-8` or `UIF-MSPI-14`; AEU-01 recorded as having moved to `UIF-MI2C-8`; functional I²C addressing bound to `AES-IF-009`. | None (draft clarification) |
