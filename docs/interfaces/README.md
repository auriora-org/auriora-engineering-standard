# Interface Specifications

**Status:** Per-specification status stated in each file (all are currently Draft)
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md)

This directory holds the concrete, versioned interface specifications of the Platform: the **Unit Interface Profiles** and the **AURIORA Event Link**.

The **Module Control Interface (MCI)** is defined transport-independently in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) and has no specification here yet: its transport bindings — a direct local transport and the Module Control Link (`MCL`) — are open items ([EDR-007](../edr/EDR-007-module-control-interface-and-module-hub.md)) and will be added as versioned binding specifications when their requirements are settled.

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

## AURIORA Event Link

The Module-to-Module typed event interface. Its interface-independent rules — typed event frame and what it may not carry, point-to-point topology with direct and routed operation, event identifiers and Module bindings, timing and observability, active Hub routing ([AES-AEL-001](../05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface) to [AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)) — are in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link). The specification below defines the physical and electrical layer, the event frame, the timing reference and the AEL router.

| Interface | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA AEL` | [ael.md](./ael.md) | 3 | Draft | Deterministic typed events between Modules: triggering configured actions, marking events in an acquisition timeline, and closed-loop reactions between measurement and stimulus Modules, directly or through one or more Module Hubs |

[sync.md](./sync.md) is the superseded notice of the former Module Synchronization Interface (`SYNC`, AES `1.5.0`–`1.6.1`); it is not a current interface.
