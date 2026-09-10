# AURIORA UIF-MSPI-14 Unit Interface Profile

**Profile Identifier:** `UIF-MSPI-14`
**Version:** `0.1` (Draft)
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md), [Architecture](../03-architecture.md)

This is a Draft [Unit Interface Profile](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles) for **Managed Units** that require a high-level SPI-transported Unit API. It is versioned independently from [`UIF-I2C-6`](./uif-i2c-6.md). The profile-independent rules apply and are not repeated here.

While this profile is Draft, it is not release-binding: no Unit or host may claim Released conformance until the open items below are resolved and the profile is versioned to a `1.x` release.

## 1. Purpose

The `UIF-MSPI-14` profile serves Units that expose a versioned, high-level Unit API over an SPI transport — for example radio, GNSS or compute-bearing Units — where the host operates the Unit through its API rather than through register-level access.

**This is not the default Managed profile.** The Managed execution model does not imply SPI. `UIF-MSPI-14` is selected when throughput, latency, deterministic transfer timing, continuous data streaming, or a need for host-controlled reset independent of power makes an I²C transport unsuitable; a low-bandwidth Managed Unit uses [`UIF-MI2C-8`](./uif-mi2c-8.md) instead. The selection rule and its criteria are [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection); discovery, `UIF_READY`, activation and event semantics are identical on both profiles, so a Unit API ports between them.

## 2. Signal Set

The profile retains the discovery/power/ready core shared with `UIF-I2C-6`:

- `UIF_PWR_VIN`
- `GND`
- `UIF_I2C_SCL`
- `UIF_I2C_SDA`
- `UIF_PWR_EN`
- `UIF_READY`

and additionally provides the Managed-Unit transport and control signals:

- `UIF_SPI_SCK`
- `UIF_SPI_MOSI`
- `UIF_SPI_MISO`
- `UIF_SPI_CS_N`
- `UIF_IRQ_N`
- `UIF_RESET_N`
- one or more profile-defined synchronization or auxiliary signals when required

Discovery and identity remain on the I²C bus (`UIF_I2C_SCL`/`UIF_I2C_SDA`) exactly as for `UIF-I2C-6` and `UIF-MI2C-8`, so a host discovers and validates a Managed Unit before enabling it, then uses SPI for functional Unit API traffic. I²C addresses on that bus follow [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation); because the Unit API is carried on SPI, no Unit API Transport Address is declared on this profile.

## 3. Semantics

- SPI is the **transport**; the semantic contract is the Unit API defined per [EEPROM Metadata](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata) and the AURIORA Firmware Style Guide (Managed Unit API rules). The profile does not define the Unit's functional command set.
- `UIF_READY` is controlled by the Unit controller and asserted only after successful firmware initialization, per [Interfaces and Versioning](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles).
- Where a dedicated hardware synchronization signal is provided, the host must not depend on timing derived only from software message latency.
- **`UIF_IRQ_N` — general event notification.** `UIF_IRQ_N` is a general active-LOW **asynchronous event notification** signal from the Managed Unit to the host. It signals that one or more Unit API events are pending — for example: new data is available, a received communication packet is available, a status change occurred, a warning or fault requires host attention, or another Unit API event is pending. It MAY therefore serve as a data-ready indication when a Managed Unit requires one.
  - The signal MUST NOT encode the exact event type directly. After detecting assertion of `UIF_IRQ_N`, the host SHALL query the Managed Unit through the Unit API to determine the pending event or events.
  - Multiple event causes MAY be pending simultaneously. The Unit API MUST provide a deterministic method to read, acknowledge and clear pending events.
  - Separate standardized signals such as `UIF_DATA_READY`, `UIF_RX_READY` or `UIF_FAULT` SHALL NOT be introduced unless a future interface profile has a demonstrated timing or safety requirement that `UIF_IRQ_N` cannot satisfy.
  - The concrete electrical implementation of `UIF_IRQ_N` — drive type, pull-up requirements, voltage thresholds, assertion timing and behavior while the Unit is unpowered — remains an open item until this profile's electrical specification is finalized (Section 4).

## 4. Open Items (require a hardware decision)

The following are **OPEN** and deliberately unresolved in this Draft. They must be decided and recorded (an EDR is required for a Platform interface decision, per [Decisions and Governance](../08-decisions-and-governance.md)) before this profile reaches `1.0`:

- **Connector family, part number, mechanical format and keying.** Not selected.
- **Final pin count and pin ordering.** The signal *set* above is defined; the physical pinout is not.
- **Number and definition of the profile-specific synchronization/auxiliary signal(s).**
- **Concrete electrical limits:** logic levels, `UIF_PWR_VIN` range, per-rail current limits, SPI clock rate, timing, `UIF_RESET_N` polarity and drive, `UIF_IRQ_N` drive type / pull-up / thresholds / assertion timing / unpowered behavior (its active-LOW *semantics* are defined in Section 3), ESD and hot-plug behavior.

## 5. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft: defines the required Managed-Unit signal set and semantics; connector, pin count and electrical limits left open. | Not release-binding |
| 0.1 (Draft) | Clarification: defined `UIF_IRQ_N` as a general active-LOW asynchronous event-notification signal (host queries the Unit API for the cause; no per-event signals); electrical implementation kept open. | None (draft clarification) |
| 0.1 (Draft) | Clarification: purpose narrowed to throughput-, latency-, determinism- or reset-bound Managed Units, with low-bandwidth Managed Units directed to `UIF-MI2C-8` ([EDR-005](../edr/EDR-005-low-bandwidth-managed-unit-interface.md)); I²C address allocation bound to `AES-IF-009`; identifier pattern noted. | None (draft clarification) |
| 0.1 (Draft) | Rename: the provisional identifier `UIF-MSPI` is confirmed as `UIF-MSPI-14`, aligning with the Platform pattern `UIF-[M]<transport>-<positions>`; the specification moved to `uif-mspi-14.md`. Signal set, semantics and the EDR-003 pinout are unchanged. | Naming only (draft) |
