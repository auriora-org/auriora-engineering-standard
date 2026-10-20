# Interface Specifications

**Status:** Per-specification status stated in each file (all are currently Draft)
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md)

This directory holds the concrete, versioned interface specifications of the Platform: the **Unit Interface Profile**, the **AURIORA Event Link**, the **Module Port** and the **Module Power Interface**.

The **Module Control Interface (MCI)** is defined transport-independently in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) and has no specification here yet: its transport bindings — a direct local transport and the Module Control Link (`MCL`) — are open items ([EDR-007](../edr/EDR-007-module-control-interface-and-module-hub.md), [EDR-010](../edr/EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md)) and will be added as versioned binding specifications when their requirements are settled. `MCL`'s connector and its half-duplex single-pair model are already fixed by the Module Port specification below ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)), and the Unit Link of `UIF-RS485-4` shares its electrical profile and framing ([EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md)), so one binding specification will serve both.

## Unit Interface Profile

The Unit Interface is realized through versioned profiles. The profile-independent rules — the `UIF_` signal set, the *enable*, *ready* and *events pending* link states, the discovery and activation sequence, one Unit per port, and profile versioning — live in [Interfaces and Versioning](../05-interfaces-and-versioning.md) ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)). The file here defines the parts that are specific to the profile: connector, contacts, cable, electrical layer, link protocol mapping and mis-mating.

Each profile is versioned independently. A Released Unit and its host declare the profile identifier and version they implement in the Unit identity record ([AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-profile-and-api-metadata)).

| Profile | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA UIF-RS485-4` | [uif-rs485-4.md](./uif-rs485-4.md) | 4 | Draft | Every Unit: power in the Module Power Interface band and one half-duplex RS-485-class pair on an M8 4-position connector, point to point, inside the enclosure or metres away |

The Platform has one profile ([EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md)). A second cell — deterministic, streaming or time-reference transfer — is recognized and empty; it is filled by a new profile when a Unit needs it ([AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration)), never by a Unit-specific contact. Profile identifiers follow `UIF-<transport>-<positions>`.

[uif-i2c-6.md](./uif-i2c-6.md), [uif-mi2c-8.md](./uif-mi2c-8.md) and [uif-mspi-14.md](./uif-mspi-14.md) are the withdrawn notices of the board-level profiles of AES `0.2.0`–`0.13.0`; they are not current interfaces.

## AURIORA Event Link

The Module-to-Module typed event interface. Its interface-independent rules — typed event frame and what it may not carry, point-to-point topology with direct and routed operation, event identifiers and Module bindings, timing and observability, active Hub routing ([AES-AEL-001](../05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface) to [AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)) — are in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link). The specification below defines the electrical layer, the event frame, the timing reference and the AEL router; its links are carried in the Module Port.

| Interface | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA AEL` | [ael.md](./ael.md) | in Module Port | Draft | Deterministic typed events between Modules: triggering configured actions, marking events in an acquisition timeline, and closed-loop reactions between measurement and stimulus Modules, directly or through one or more Module Hubs |

## Module Port and Module Power Interface

The two external connectors of a Module besides its service connection ([AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation)): the **Module Port** carries everything that is communication with a Hub or a peer Module — `MCL`, AEL IN and AEL OUT — and the **Module Power Interface** carries the Module's primary operating power. They never share a connector, and their inserts do not mate ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)).

| Interface | File | Positions | Status | Intended for |
|---|---|---:|---|---|
| `AURIORA Module Port` | [module-port.md](./module-port.md) | 8 | Draft | One connector per Module for `MCL`, AEL IN and AEL OUT, and the AURIORA Link Cable that connects Module Ports to a Hub, to a peer Module and Hub to Hub |
| `AURIORA Module Power Interface` | [module-power.md](./module-power.md) | 3 | Draft | The primary 12 V DC power input of a Module and of a Module Hub, the source output that feeds it and the male-to-female power cable between them |

[sync.md](./sync.md) is the superseded notice of the former Module Synchronization Interface (`SYNC`, AES `0.6.0`–`0.7.1`); it is not a current interface.
