# Interface Specifications

**Status:** Per-specification status stated in each file (all are currently Draft)
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md)

This directory holds the concrete, versioned interface specifications of the Platform: the **Unit Interface Profiles** and the **Module Synchronization Interface**.

## Unit Interface Profiles

The Unit Interface is realized through versioned profiles. The profile-independent rules — the `UIF_` signal set, `UIF_READY` semantics, the discovery and activation sequence, and profile versioning — live in [Interfaces and Versioning](../05-interfaces-and-versioning.md) ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)). The files here define the parts that are specific to one profile: connector, pinout, electrical limits and timing.

Each profile is versioned independently. A Released Unit and its host declare the profile identifier and version they implement in EEPROM metadata ([AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)).

| Profile | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA UIF-I2C-6` | [uif-i2c-6.md](./uif-i2c-6.md) | 6 | Draft | Passive Units and simple I²C-based Units |
| `AURIORA UIF-MI2C-8` | [uif-mi2c-8.md](./uif-mi2c-8.md) | 8 | Draft | Low-bandwidth Managed Units — the default Managed profile |
| `AURIORA UIF-MSPI-14` | [uif-mspi-14.md](./uif-mspi-14.md) | 14 | Draft | Managed Units bound by throughput, latency, deterministic timing or streaming |

Two axes select a profile: the **management model** (Passive or Managed) fixes the host contract, and the **transport** fixes the bus. They are independent — a Managed Unit is not required to use SPI. The selection rule is [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection) and the family table is in [Interfaces and Versioning §3.2](../05-interfaces-and-versioning.md#32-profile-family-and-selection).

Profile identifiers follow `UIF-[M]<transport>-<positions>`. The position counts are deliberately distinct so no two profiles can mate: a host cannot energize or mis-drive a Unit built to a different contract.

## Module Synchronization Interface

The Module-to-Module event interface. Its interface-independent rules — event-only semantics, point-to-point topology with active Hub fan-out, arming and default behavior, observability ([AES-SYNC-001](../05-interfaces-and-versioning.md#aes-sync-001-sync-is-a-module-level-event-interface) to [AES-SYNC-004](../05-interfaces-and-versioning.md#aes-sync-004-sync-observability)) — live in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-module-synchronization-interface); the file here defines the connector, pinout, electrical layer, event edge and the SYNC Hub. SYNC is not a Unit Interface Profile and carries no `UIF_` signal.

| Interface | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA SYNC` | [sync.md](./sync.md) | 3 | Draft | Deterministic event synchronization between Modules: triggering a configured action, or marking an event in an acquisition timeline |
