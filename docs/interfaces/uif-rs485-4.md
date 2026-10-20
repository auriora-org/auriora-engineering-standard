# AURIORA UIF-RS485-4 Unit Interface Profile

**Profile Identifier:** `UIF-RS485-4`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [Unit Identity Record](../06-eeprom-metadata.md), [Architecture](../03-architecture.md), [Module Power Interface](./module-power.md)

This is a versioned [Unit Interface Profile](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles). The profile-independent rules — the `UIF_` signal set, the *enabled* and *ready* states, discovery and activation ([AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)), one Unit per port ([AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-one-unit-per-port)), profile declaration ([AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration)) and profile versioning ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)) — apply and are not repeated here. This file defines only what is specific to `UIF-RS485-4`.

While this specification is Draft, it is not release-binding: no Unit, Module or cable may claim Released conformance until the open items in Section 11 are resolved and the specification is versioned to a `1.x` release. Section 11 separates what this Draft has **settled** from what is still **open**.

## 1. Purpose

`UIF-RS485-4` is the Unit Interface Profile of the Platform: the one connector, cable and link through which a Module powers, discovers, activates and operates a Unit, whether the Unit sits on the same board stack, inside the Module's enclosure, or metres away on its own cable. It replaces the three board-level profiles of AES `0.13.0` and earlier — `UIF-I2C-6`, `UIF-MI2C-8` and `UIF-MSPI-14` — under [EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md).

The profile moves the Unit Interface from single-ended buses meant for centimetres to a differential link meant for metres, and it moves the discrete control signals of the earlier profiles — `UIF_PWR_EN`, `UIF_READY`, `UIF_IRQ_N` — into the link protocol, so that a Unit needs exactly four conductors: power, return and one pair. The model is the Module Port one level down: a Unit Port on a Module is to a Unit what a Module Port on a Hub is to a Module — a point-to-point, polled, half-duplex differential link on a small circular connector, with the port end as master.

## 2. Topology

```text
Module, Unit Port n ── Unit cable ── Unit                      (external; metres)
Module, Unit Port n ── internal lead or connector ── Unit      (inside the enclosure; same link)
```

- **Point to point.** One Unit Port connects exactly one Unit over one link. There is no multidrop, no bus address and no Unit-to-Unit traffic ([AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-one-unit-per-port)).
- **The port polls.** The Unit Port end is the link master: it initiates every transaction, and the Unit transmits only in answer to it. A Unit never initiates.
- **Any Unit, any port.** A Module does not fix which Unit goes on which port. Discovery establishes what is connected; the port index is topology metadata the Module may report, never part of the Unit's identity ([AES-MCI-002](../05-interfaces-and-versioning.md#aes-mci-002-module-identity) applies the same separation one level up).
- **Port count is a product decision** and part of the Module's host-visible contract: a Module with a different number of Unit Ports is a different product ([Naming and Identity §5](../04-naming-and-identity.md#5-product-numbers-and-revisions)).
- **Same link inside and outside.** A Unit mounted inside the Module's enclosure is connected over the same four conductors and the same protocol; only the connector may differ (Section 3.3). The Unit's identity record declares the same profile either way.

## 3. Connector

### 3.1 Unit Port on the Module

- **Form.** M8, 4-position, A-coded circular connector, IEC 61076-2-104 form, panel-mounted on the Module.
- **Gender.** **Female / socket-contact.** The Unit Port is the source of `UIF_PWR_VIN`, so its free contacts are live when the port is enabled; the Platform's gender rule puts live free contacts on female connectors only ([AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation)).
- **Reservation.** The M8 4-position A-coded female / socket-contact panel form is assigned to the Unit Port on every Platform device that carries one ([Document Index, External Connector Register](../document-index.md#external-connector-register)); it SHALL NOT serve another function on a Platform device.
- **Labeling.** `UNIT PORT` with the port index the Module reports.
- **Say the gender twice.** Schematics, BOMs and drawings name *female / socket-contact*, because supplier terms for plug, receptacle and socket are not uniform.

### 3.2 Unit input on the Unit

- **Form.** M8, 4-position, A-coded, **male / pin-contact**, panel-mounted on the Unit — an input that nothing energizes from inside, exactly as the Module Power Interface input is on a Module.
- **Captive cable permitted.** A Unit MAY omit the panel connector and carry a **captive cable** ending in the Unit cable's Module-end plug (Section 4). Small Units whose board is not much larger than an M8 panel part take this form. The cable length is then part of the Unit's declared mechanical envelope ([AES-UNIT-004](../03-architecture.md#aes-unit-004-declared-limits)).
- **No label obligation.** A Unit has one connection; a label is a product choice.

### 3.3 Internal realization

Where a Unit is mounted **inside** the Module's enclosure, the M8 pair MAY be replaced by an internal connector or lead of the product's choice carrying the same four conductors. The electrical layer, the discovery and activation protocol and the Unit API are unchanged, and a Unit built this way is the same Unit with a different termination. The internal connector is not a Platform-facing connector and is not registered; the Module's design notes record it. The internal realization SHOULD use a **4-position, 1.00 mm-pitch connector of the JST SH family** with the same position assignment as Section 4 — 1 `UIF_PWR_VIN`, 2 `UIF_LINK_P`, 3 `GND`, 4 `UIF_LINK_N` — so that internal Units and internal ports share one pinout across products and an internal Unit reaches an external Unit Port through one adapter cable. A Unit designed for internal mounting only SHOULD still be electrically conformant to an external port, so that it can be tested on one.

## 4. Contacts and the Unit Cable

| Position | Signal | Direction (host view) | Description |
|---:|---|---|---|
| 1 | `UIF_PWR_VIN` | Host → Unit | Unit input power, in the Module Power Interface band (Section 5.1). Powers the Unit's discovery domain whenever the port is enabled; the Unit switches its functional domain locally on the *enable* state. |
| 2 | `UIF_LINK_P` | Bidirectional | Unit Link, non-inverting side of the half-duplex differential pair. |
| 3 | `GND` | — | Power return and signal reference. |
| 4 | `UIF_LINK_N` | Bidirectional | Unit Link, inverting side. |

- **The insert's own numbering.** Positions 1 and 3 carry power and return on the M8 3-position Module Power Interface insert too; this profile keeps them there deliberately (Section 9).
- **Polarity naming.** `P` and `N`, as on every Platform differential link; the RS-485 letters `A`/`B` are not used.
- **All four contacts are mandatory** on the port, on the Unit and through any cable. There is no three-conductor variant.
- **Shield.** Where a shielded cable is used, its shield terminates to the connector shells and bonds to chassis or shield ground at the Module's point of entry; the shield is not `GND`. A shield is not required at the bit rates this profile targets (Section 5.2); whether one is, and from what length, is an open item.

### 4.1 Unit cable

- **Form.** M8 4-position A-coded, **male / pin-contact at the Module end**, **female / socket-contact at the Unit end**, wired **straight**: 1-1, 2-2, 3-3, 4-4. This is the industry-standard M8 4-position sensor cordset; a conforming cable is a procurement item, not a Platform design.
- **Conductors.** `UIF_LINK_P`/`UIF_LINK_N` SHOULD be a twisted or otherwise coupled pair in a cable built for this profile. A generic four-conductor cordset without a defined pair is acceptable up to the length validated for it (Section 11); the validation is what makes it acceptable, not the catalogue.
- **Conductor size.** At least 0.25 mm² for power and return; the per-port current (Section 5.1) and the length set the drop, and the Unit's declared input range absorbs it.
- **Never female-to-female, never male-to-male.** A cable with two female ends would join two Unit Ports; a cable with two male ends would present an energized male contact. Neither is a Platform cable.
- **Marking.** No special marking is required: a generic M8 4-position straight cordset *is* a Unit cable. A cable built with a defined pair and a validated length MAY be marked `AURIORA UNIT` with its length.

## 5. Electrical Layer

### 5.1 Power

- **Band.** When a Unit Port is enabled, `UIF_PWR_VIN` at the port is within the Module Power Interface operating band, **10.0–15.0 V**, derived from the Module's regulated or protected input, never `MPI_VIN` wired straight through ([Hardware Design Guide §6.1](https://github.com/auriora-org/auriora-hardware-design-guide/blob/main/GUIDE.md#61-unit-port-power-and-states)). A Unit regulates every internal rail from it.
- **Unit input.** A Unit operates over the full 10.0–15.0 V band at its input and declares its own no-damage range; the figure the Platform fixes for the band's upper no-damage bound is open.
- **Per-port switch, limit and protection.** Every Unit Port has its own power switch and current limit under host control, so that an unknown or faulted Unit is contained to its port, a port can be power-cycled independently, and the host can de-energize a Unit that never answers. The limit is the barrier; the Unit's declared power figures are unauthenticated input ([AES-EEPROM-007](../06-eeprom-metadata.md#aes-eeprom-007-metadata-trust-model)).
- **Ceiling.** The connector family's rating bounds any port: **3 A per contact** is the ceiling below which a product sets its per-port limit. The profile fixes no Platform-wide per-port figure; a Module declares its per-port and simultaneous capability and validates each Unit's declared currents against it before enabling the functional domain.
- **Discovery domain.** With the port enabled and the Unit's functional domain disabled, the Unit draws at most the profile's **maximum discovery-state current** from `UIF_PWR_VIN` (open; a figure small enough that every host can energize an unknown port under its current limit without consulting metadata first). The Unit's controller, in a low-power state, and its transceiver in receive are what this current pays for.
- **Local switching.** The Unit switches its functional domain — sensors, actuators, radios, the controller's full-speed operation — locally on the *enable* state of the link (Section 6). The connector provides no separate functional-power contact.
- **No back-powering.** Nothing on the Unit is powered through `UIF_LINK_P`/`UIF_LINK_N` while the port is disabled; an unpowered Unit SHALL NOT be back-driven through, and SHALL NOT source current into, any contact.
- **Ports are not additive.** The number of Unit Ports is not a promise that all can draw their per-port maximum at once; the Module declares the combinations it supports ([AES-MOD-003](../03-architecture.md#aes-mod-003-unit-compatibility-matrix)).
- **A Module without 12 V.** A Module running from its direct local transport or a battery that cannot hold the band at a port keeps that port disabled and reports it; it does not offer an out-of-band `UIF_PWR_VIN`.

### 5.2 Link

- **Class.** The Unit Link is one **half-duplex differential pair of RS-485 class** (TIA/EIA-485-A-compatible transceivers), terminated at both ends because both ends drive, with a defined idle established by fail-safe receiver biasing at the Module end so that an open or unpowered far end reads idle, never a start bit. These are the same electrical requirements the Platform places on `MCL` ([Interfaces and Versioning §5.1](../05-interfaces-and-versioning.md#51-transport-bindings)); the Unit Link and `MCL` share one electrical profile and one framing when the `MCL` binding is written, so that a product carries one transceiver class and one line discipline.
- **Line discipline.** The Module end owns the line at idle and drives only to transmit a request; the Unit drives only to answer, and releases the line at end of frame within the turnaround bound. Driver enable on both ends is under firmware control with a defined receive (idle) state through reset, power-up and firmware start.
- **Survive the wrong state.** Two drivers on the pair — a firmware fault, a mis-mated cable (Section 9) — SHALL cause no damage at either end for as long as it lasts; the transceiver's contention and short-circuit limits cover it, verified, not assumed.
- **Bit rate, turnaround, termination value, idle differential state, maximum validated length** — open (Section 11), shared with the `MCL` binding.
- **Isolation.** Galvanic isolation of a Unit Port is a **product decision, documented**: the profile permits an isolated port (isolated `UIF_PWR_VIN` and transceiver, `GND` of the port isolated from the Module's reference) and a non-isolated one, and a Unit cannot tell them apart. A Module records which it chose and why, with the ground-loop analysis for its measurement front end; a Module whose reference is a measurement reference — an electrophysiology front end with electrodes on the same ground — has every reason to isolate.

### 5.3 States and timing

- **Ready state.** The Unit's *ready* state has the semantics the earlier profiles gave `UIF_READY`: *not ready* — disabled, starting, not initialized, faulty or absent; *ready* — powered, initialized, functional interface able to serve. The Unit reports it in every status answer; the host MUST treat a Unit that does not answer as *not ready*.
- **Bounded waits.** The time from *enable* to *ready*, the response time to a poll and the turnaround are bounded by figures this profile fixes before `1.0` (open). On expiry the host de-energizes the port and treats the Unit as failed rather than transacting with it ([AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)).
- **Sleep and wake.** A Unit MAY sleep between polls. It SHALL wake on line activity and answer within the response bound; the poll cadence a host uses is therefore the Unit's event latency, and a host that needs lower latency polls faster.

## 6. Discovery, Activation and Recovery

The profile-independent sequence of [AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence) maps onto the link as follows:

1. **Port power on.** The host enables the Unit Port's power switch. The Unit's discovery domain starts; its functional domain stays off.
2. **Identity request.** The host polls the port with an identity request. **Presence is a valid answer**: a port that answers has a Unit, a port that does not has none, and no presence contact exists.
3. **Identity record.** The Unit answers with its Unit identity record — the field set and binary layout of the [Unit Identity Record](../06-eeprom-metadata.md), served by the Unit controller from nonvolatile memory. Where the controller keeps it in an EEPROM behind it is a Unit-internal matter.
4. **Validation.** The host validates in the order of [AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order): magic, length, CRC, schema, AOID format, profile identifier `UIF-RS485-4` and version, Unit API identifier and version, capability limits, power requirements against the port's capability, calibration validity where applicable.
5. **Enable.** If the Unit is supported, the host sends *enable*. The Unit switches its functional domain on locally. If the Unit is unsupported, incompatible, invalid or exceeds the port's power capability, the host does not send *enable*; it MAY leave the port powered in the discovery state or de-energize it.
6. **Ready.** The host polls status until the Unit reports *ready*, within the bound of Section 5.3.
7. **Unit API.** Functional traffic begins only after *ready*. The Unit API identifier and address the earlier profiles declared for an addressed transport are not needed: the link has one Unit.

**Disable and recovery.** An orderly shutdown is *disable* over the link, after which the Unit reports *not ready* and switches its functional domain off. Recovery of a hung or faulted Unit is a **port power cycle**: the host de-energizes the port for at least the profile's minimum off-time (open) so the Unit fully discharges, then restarts from step 1. No reset contact exists; a power cycle clears the controller, its peripherals and its external devices alike, which a reset line would not. Firmware update, where a Unit supports it, is a Unit API operation declared in the capability flags; bootloader entry is a Unit-internal matter and never on the connector.

## 7. Identity Record

A Unit on this profile serves the [Unit Identity Record](../06-eeprom-metadata.md) over the link: the fixed header of its Section 4 and the TLV extension records of [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-profile-and-api-metadata). It SHALL declare profile identifier `UIF-RS485-4`, profile version, Unit API identifier and version, capability flags, and the power fields — required input voltage, maximum start-up current and its duration, maximum operating current, nominal operating current, maximum discovery-state current — that the host validates against its port before *enable*. A Unit API transport address is not declared: the profile has none.

The identity record SHALL be readable in the discovery state, SHALL NOT change while the port is powered, and SHOULD be write-protected after manufacturing verification ([AES-EEPROM-005](../06-eeprom-metadata.md#aes-eeprom-005-writable-field-control)).

## 8. Unit API and Events

The Unit API is the semantic contract; this profile defines only its transport. A Unit API on this profile SHALL be expressible as request/response transactions bounded by the link's payload and response limits, SHALL NOT require the host to address the Unit's internal components, and SHALL NOT expose internal devices — sensors, radios, external buses — on the link.

**Events.** No event contact exists. A Unit with asynchronous events reports *events pending* in every status answer, and the host reads, acknowledges and clears pending events through the Unit API by a deterministic method; a Unit SHALL NOT clear *events pending* until no unacknowledged event remains. Event latency is the poll cadence (Section 5.3). A Unit with no asynchronous events reports none and declares no event capability.

**What this profile does not carry.** A distributed hardware time reference — a PPS-class sub-microsecond edge — and deterministic, streaming or sub-millisecond transfer are outside this profile, as they were outside its predecessors. A Unit that needs them is served by a new versioned profile decided by EDR ([AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration)), never by a Unit-specific contact or a side channel on this one.

## 9. Mis-mating

The M8 4-position A-coded insert and the M8 3-position A-coded insert of the Module Power Interface are related: the 3-position insert is the 4-position insert without position 2, so a **3-position male plug enters a 4-position female socket**, while a 4-position male plug does not enter a 3-position female socket and a 3-position female socket does not accept a 4-position male plug. This profile places `UIF_PWR_VIN` and `GND` on positions 1 and 3 — the same positions as `MPI_VIN` and `MPI_RTN` — so that every mating that is physically possible is harmless:

| Mis-mating | Result |
|---|---|
| Power cable female end (live, 3-position) → Unit input (male, 4-position) | **Does not mate.** A live power cable never enters a Unit. |
| Power cable male end (3-position; never live on its own) → Unit Port (female, 4-position) | Mates. The Unit Port energizes positions 1 and 3 of the power cable in the band of a power source; `UIF_LINK_N` on position 4 meets the power cable's wired-through, open-ended reserved conductor; position 2 has no contact. If the cable's far end is in a device power input, that device is powered from the Unit Port within the port's current limit — a nuisance, not a hazard, and visible as a Unit Port that never discovers a Unit. |
| Unit cable female end (live when the Module end is in an enabled Unit Port, 4-position) → Module or Hub power input (male, 3-position) | Mates. `UIF_PWR_VIN` lands on `MPI_VIN`, `GND` on `MPI_RTN`, both in the power input's operating band; `UIF_LINK_N` lands on the input's open, tolerant position 4; `UIF_LINK_P` has no mating contact. The device is powered from a Unit Port within the port's current limit; the link sees one side floating and reads idle. Harmless. |
| Unit cable male end (never live) → power source output (female, 3-position) or female measurement port | **Does not mate.** |
| Unit cable female end → Unit Port (female) | Does not mate. |
| Any 4-position plug → Module Port (8-position); Link Cable → Unit Port | Do not mate ([Module Port](./module-port.md)). |

A product that carries Unit Ports records this table for its own ports with the Section 11 assembly review of the Hardware Design Guide, and confirms that a Unit Port's current limit contains the two powered mis-matings.

## 10. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | M8 4-position A-coded; female / socket-contact Unit Port on the Module, male / pin-contact input or captive cable on the Unit; contacts per Section 4; Unit cable straight, male-to-female. | Fit check of a Unit cable into every Unit Port and into every other M8 connector of the product; the Section 9 table verified on real parts. |
| Electrical | `UIF_PWR_VIN` in band when enabled; per-port switch and current limit; discovery-state current within the profile maximum; RS-485-class pair terminated both ends with fail-safe idle; no back-drive when unpowered; survives contention indefinitely. | Band at the port under the declared load; port limit trips and recovers; unknown-Unit energization under limit; idle read with the far end open, unpowered and shorted; contention soak for the product's documented time. |
| Communication | Identity record readable in the discovery state; *enable*, *disable*, status with *ready* and *events pending*; response and turnaround within bound; the Unit never initiates. | Identity read before *enable*; functional traffic refused before *ready*; response-time and turnaround measurement; silence from the Unit between polls. |
| Semantic | Host validates the record, enables, waits *ready* within bound, then speaks the Unit API; absent, incompatible, invalid and over-budget Units are never enabled; a Unit that never reports *ready* is de-energized. | Valid, incompatible, invalid-record, over-budget and never-ready Unit tests; port power cycle recovers a hung Unit. |
| Topology | One Unit per port; any Unit on any port; port index reported as topology, never as identity. | Two Units swapped between ports are reported under their own identities at their new indices. |

## 11. Settled and Open Items

### 11.1 Settled in this Draft

Decided by [EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md); an implementer may build against these:

- M8 4-position A-coded; female / socket-contact Unit Port on the Module, male / pin-contact input or captive cable on the Unit; positions 1 `UIF_PWR_VIN`, 2 `UIF_LINK_P`, 3 `GND`, 4 `UIF_LINK_N`.
- Straight male-to-female Unit cable — the generic M8 4-position cordset; never female-to-female or male-to-male.
- `UIF_PWR_VIN` in the Module Power Interface band 10.0–15.0 V, locally regulated on the Unit; per-port switch and current limit; discovery domain powered from the port; functional domain switched locally on *enable*.
- One half-duplex RS-485-class pair, terminated both ends, fail-safe idle owned by the Module end; the Module polls, the Unit answers; one electrical profile and framing shared with `MCL`.
- Discovery, *enable*, *disable*, *ready* and *events pending* as link protocol; presence is a valid answer; recovery is a port power cycle; no reset, presence, event or enable contact.
- The Unit identity record (AES chapter 06) served over the link; no transport address.
- Isolation a documented product decision; internal realization with a product-chosen connector, the JST SH 1.00 mm 4-position with the same position assignment recommended; captive cable permitted on the Unit.
- The same mis-mating logic as the Module Power Interface, by sharing positions 1 and 3.

### 11.2 Open

Decided before this specification reaches `1.0`, by an explicit Platform decision or from bring-up measurement of the first Module and Units:

- **Framing, request/response correlation, error signaling and the message set** — identity request, *enable*, *disable*, status, Unit API carriage — as the Unit Link binding, written together with the `MCL` binding so that the two share framing.
- **Bit rate, turnaround time, response bound, termination value, idle differential state, fail-safe bias values**; **maximum validated cable length** with a paired cable and with a generic cordset; whether and from what length a shield is required.
- **Maximum discovery-state current**; the **minimum port off-time** for recovery; the **enable-to-ready bound** and whether it is a profile constant or a declared Unit figure.
- **Unit input no-damage range**; the Platform's recommended per-port current limit and the Unit cable's recommended conductor size per length.
- **Sleep and wake**: the maximum wake-up time on line activity, and whether a wake preamble is part of the framing.
- **Environmental rating** (IP class, temperature) of the connector and cable, as a Platform minimum or a product statement.
- **Origin assurance.** A signed identity record — a TLV carrying a manufacturing-key signature over the record and the controller's unique identifier ([AES-EEPROM-007](../06-eeprom-metadata.md#aes-eeprom-007-metadata-trust-model)) — is defined by EDR when a Unit needs proof of origin; the profile's discovery exchange is designed so that such a record rides in the same identity answer.
- **Transceiver supply.** Whether the Unit transceiver runs at 3.3 V or 5 V is a Unit-internal choice as long as the line levels meet the profile; whether the profile constrains it is decided with the electrical figures.

## 12. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft ([EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md)): the Platform's single Unit Interface Profile on an M8 4-position connector with power in the Module Power Interface band and one half-duplex RS-485-class pair; discovery, enable, disable, ready and events as link protocol; point to point, port polls; generic cordset as the Unit cable; internal realization and captive cable permitted; isolation a documented product decision; mis-mating made harmless by sharing positions 1 and 3 with the power interface. Framing, bit rate, timing figures, currents and lengths left open. | Not release-binding; replaces `UIF-I2C-6`, `UIF-MI2C-8` and `UIF-MSPI-14`, none of which had a Released realization |
