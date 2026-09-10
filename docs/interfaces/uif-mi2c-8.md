# AURIORA UIF-MI2C-8 Unit Interface Profile

**Profile Identifier:** `UIF-MI2C-8`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md), [Architecture](../03-architecture.md)

This is a versioned [Unit Interface Profile](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles). The profile-independent rules — `UIF_` signal semantics, `UIF_READY` behavior, discovery and activation ([AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence)), I²C address allocation ([AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation)), profile selection ([AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection)) and profile versioning ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)) — apply and are not repeated here. This file defines only what is specific to `UIF-MI2C-8`.

## 1. Purpose

`UIF-MI2C-8` is the default Unit Interface profile for **low-bandwidth Managed Units**: Units that contain their own controller, expose a versioned high-level Unit API, hide their internal sensors and peripherals from the host, and move small amounts of data at modest rates.

It exists because *management model* and *transport* are independent axes ([Interfaces and Versioning §3.2](../05-interfaces-and-versioning.md#32-profile-family-and-selection)): a Managed Unit is not required to use SPI. One profile serves Managed Units both with and without asynchronous events (Section 4). The alternatives weighed — including reusing [`UIF-MSPI-14`](./uif-mspi-14.md), widening [`UIF-I2C-6`](./uif-i2c-6.md), and splitting this profile in two — are in [EDR-005](../edr/EDR-005-low-bandwidth-managed-unit-interface.md).

## 2. Pin Assignment

Eight positions. Pins 1–6 are the `UIF-I2C-6` signal order unchanged; pins 7 and 8 are the additions.

| Pin | Signal | Direction (host view) | Mandatory | Description |
|---:|---|---|---|---|
| 1 | `UIF_PWR_VIN` | Host → Unit | Yes | Unit input power. Powers the discovery EEPROM and minimum discovery circuitry at all times; powers the Unit controller and functional circuitry only when the Unit's local switch is enabled by `UIF_PWR_EN`. |
| 2 | `GND` | — | Yes | Ground reference and power return; adjacent to pin 1 to close a tight supply loop. |
| 3 | `UIF_I2C_SCL` | Host → Unit | Yes | I²C clock. Carries both discovery and Unit API traffic. |
| 4 | `UIF_I2C_SDA` | Bidirectional | Yes | I²C data. Carries both discovery and Unit API traffic. |
| 5 | `UIF_PWR_EN` | Host → Unit | Yes | Enables the Unit's functional power domain locally. LOW until the host has validated compatibility and power. |
| 6 | `UIF_READY` | Unit → Host | Yes | Active-HIGH functional-ready indication, driven by the Unit controller. |
| 7 | `UIF_IRQ_N` | Unit → Host | Contact yes, use optional | Active-LOW generic event notification, open-drain, pull-up on the host side. See Section 4. |
| 8 | `GND` | — | Yes | Second ground reference and return, at the opposite end of the connector from pin 2. |

- All eight contacts are **mandatory on both the host connector and the Unit connector**. There is no six- or seven-position variant of this profile.
- Both `GND` contacts are mandatory and SHALL be connected on the host, on the Unit and through the full length of any cable. A cable assembly that populates only one ground conductor is not conformant.
- `UIF_IRQ_N` is the only signal whose *use* is optional: a Unit with no asynchronous events leaves it undriven and declares that in its capability metadata (Section 4).
- No `UIF_RESET_N` is defined (Section 6). No presence pin exists on any UIF profile ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)).
- Unit-specific event signals (`UIF_DATA_READY`, `UIF_FAULT`, `UIF_RX_READY`, `SPECTRUM_READY` or equivalents) SHALL NOT be defined on this profile.

### 2.1 Connector

The connector is an **8-position, 1.00 mm-pitch connector in the JST SH family** — the same family and pitch as the other UIF profile realizations, with a position count distinct from both `UIF-I2C-6` (6) and `UIF-MSPI-14` (14). The exact sub-series and part number are confirmed at BOM time. The connector is intrinsically polarized against reverse insertion; pin 1 SHALL be marked on the PCB.

The distinct position count is a safety property, not a convenience: a Managed Unit cannot be mated into a Passive-Unit port and vice versa, so profile mismating is prevented mechanically rather than by discovery alone ([AES-IF-007](../05-interfaces-and-versioning.md#aes-if-007-safe-default-state)).

Wiring beyond the connector — cable type, shielding, maximum length and bus capacitance budget — is part of the electrical layer and remains open (Section 3).

### 2.2 Ground and return

The profile carries **two ground contacts**, at pins 2 and 8, one at each end of the connector:

- **Pin 2** closes a tight supply loop with `UIF_PWR_VIN` on pin 1, so the Unit's supply current has a short, local return.
- **Pin 8** provides a return at the far end of the signal group. Every signal contact then lies within three positions of a ground, instead of up to five with a single power-end ground, which shortens the return path for `UIF_READY` and `UIF_IRQ_N` and gives `UIF_I2C_SCL` a closer reference.

The second ground earns its contact in the **cable**: metres of thin field wiring in which one 1.00 mm contact and one conductor would otherwise return the supply current *and* every signal, so the Unit's own switching transients land as ground shift on the I²C receiver thresholds. Two returns roughly halve that impedance, and separating them to opposite ends lets a cable assembly reference both sides of the signal bundle ([EDR-005](../edr/EDR-005-low-bandwidth-managed-unit-interface.md)).

## 3. Electrical Layer

Concrete electrical limits are defined here when this profile is realized on specific hardware. This profile is **Draft**: it constrains the signal set, its meaning and its physical arrangement until these limits are finalized (see [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness)). It SHALL NOT be marked Normative or promoted to a `1.0` release until voltage limits, current limits, logic thresholds, I²C bus speed and capacitance budget, clock-stretch and timing bounds, ESD protection, cable limits and hot-plug behavior are finalized.

**OPEN — needs hardware decision:** JST SH sub-series and part number; cable construction and ground-conductor arrangement; `UIF_PWR_VIN` tolerance band; per-rail current limits; I²C pull-up values, bus speed and total bus capacitance budget; `UIF_IRQ_N` pull-up value and thresholds; maximum clock-stretch time; minimum power-off time (Section 6); logic thresholds; ESD protection level; hot-plug behavior; maximum cable length.

Baseline rules that apply regardless of the numbers:

- `UIF_PWR_VIN` is nominally **+3V3**, consistent with the other UIF profiles, until a wider range is fixed here. A host SHALL NOT exceed the VIN range the Unit's EEPROM power metadata declares.
- The Unit locally switches its functional power domain — including its controller — from `UIF_PWR_EN`. The connector provides no separate discovery-power pin.
- Disabled Unit circuitry MUST NOT be back-powered through `UIF_I2C_SCL`, `UIF_I2C_SDA`, `UIF_READY` or `UIF_IRQ_N` while `UIF_PWR_EN` is LOW.
- `UIF_READY` MUST have a defined LOW state when the Unit is absent, disabled, starting or faulty.
- `UIF_IRQ_N` MUST have a defined HIGH (de-asserted) state when the Unit is absent, disabled, starting or faulty. The host owns the pull-up, so no Unit-side pull-up variation exists and the line is defined with no Unit connected.
- The I²C pull-ups are **host-side**. A Unit SHALL NOT fit bus pull-ups, so bus loading does not change with the number of mated Units.

### 3.1 Bus timing and clock stretching

A Managed Unit typically serves I²C transactions from firmware, so clock stretching is expected and is part of this profile's contract rather than an implementation accident:

- A host on this profile MUST tolerate Unit clock stretching up to the profile's maximum clock-stretch time (open, Section 3), and MUST NOT treat stretching within that bound as a bus fault.
- A Unit SHALL bound its clock stretching to that maximum. A Unit that cannot serve a request within the bound SHALL NACK the transaction rather than stretch further, and SHALL report the condition through the Unit API.
- A Unit SHALL NOT hold `UIF_I2C_SCL` or `UIF_I2C_SDA` LOW indefinitely in any state, including boot, fault and shutdown.
- A host MUST implement I²C bus recovery (clock pulsing, or `UIF_PWR_EN` cycling per Section 6) for the case where a Unit violates the above.

### 3.2 First hardware realizations

The first Units realizing this profile are the AURIORA Environmental Sensor Unit (`AOID:PUB:UNIT:ENV:AEU:001`, AEU-01) and the AURIORA Spectral Unit (ASU, AOID not yet assigned). Their bring-up measurements will seed the electrical layer, exactly as AEU-01's power decisions seeded [`UIF-I2C-6`](./uif-i2c-6.md). Those values are Unit-specific and **not yet profile-normative**; promotion to a normative range is required before `UIF-MI2C-8` leaves Draft.

## 4. Event Notification

`UIF_IRQ_N` is a **generic asynchronous event notification** from the Managed Unit to the host. Its semantics are identical to `UIF_IRQ_N` on [`UIF-MSPI-14` §3](./uif-mspi-14.md#3-semantics) — one signal, no encoded cause:

- Assertion means one or more Unit API events are pending: a measurement completed, data is available, a status change occurred, a warning or fault needs attention, or another Unit API event.
- The signal MUST NOT encode the event type. After detecting assertion, the host SHALL query the Unit API to determine the pending event or events.
- Multiple causes MAY be pending simultaneously. The Unit API MUST provide a deterministic method to read, acknowledge and clear pending events.
- The Unit SHALL de-assert `UIF_IRQ_N` only when no unacknowledged events remain, so a level-driven host input cannot lose an event that arrives during servicing.

### 4.1 Optional use, mandatory contact

The contact is always present; using it is a Unit property the host learns at discovery:

- A Unit that generates asynchronous events SHALL drive `UIF_IRQ_N` and SHALL declare event notification in its capability flags ([AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)).
- A Unit with no asynchronous events SHALL leave `UIF_IRQ_N` undriven and SHALL NOT declare the capability. The host pull-up then holds the line de-asserted and the host operates the Unit by polling the Unit API.
- A host on this profile SHALL provide the `UIF_IRQ_N` pull-up and SHALL support polling operation, so it can serve a Unit that does not declare the capability. A host SHOULD support interrupt-driven operation; a host that does not SHALL still operate a declaring Unit correctly by polling, because the Unit API remains the authoritative source of pending events.
- The event signal is an efficiency and latency mechanism, never the only path to an event. Any event reachable through `UIF_IRQ_N` SHALL also be observable by polling the Unit API.

## 5. Power Sequencing

The profile-independent sequence of [AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence) applies unchanged. Profile-specific points:

1. `UIF_PWR_VIN` on. Only the discovery EEPROM is powered. The Unit controller is unpowered; `UIF_READY` is LOW; `UIF_IRQ_N` is HIGH by host pull-up.
2. The host discovers and validates the Unit over I²C, including the profile identifier `UIF-MI2C-8`, profile version, Unit API identifier and version, capability flags, the Unit API I²C address and the power fields.
3. If validation passes, the host asserts `UIF_PWR_EN`. The Unit controller boots.
4. The Unit asserts `UIF_READY` only after its firmware has initialized and its Unit API I²C target is able to serve transactions.
5. The host begins Unit API traffic only after `UIF_READY` is HIGH. Before that the Unit's functional I²C address MUST NOT acknowledge; discovery EEPROM access remains available throughout.
6. On shutdown the Unit de-asserts `UIF_READY` before the host removes `UIF_PWR_EN`, where an orderly shutdown is requested through the Unit API.

The host SHALL bound the wait for `UIF_READY` after asserting `UIF_PWR_EN`. On timeout the host SHALL de-assert `UIF_PWR_EN` and treat the Unit as failed rather than transacting on the bus.

## 6. Reset and Recovery

**This profile defines no `UIF_RESET_N`.** The recovery mechanism is `UIF_PWR_EN`:

- The Unit controller lies entirely within the `UIF_PWR_EN`-switched functional domain, so removing `UIF_PWR_EN` fully de-energizes it. That is a stronger and more predictable recovery than a controller reset pin, which leaves peripherals, latched I/O and external devices (an RS-485 transceiver, a radio) in an undefined state.
- To recover a hung or faulted Unit, the host SHALL de-assert `UIF_PWR_EN`, hold it LOW for at least the profile's minimum power-off time (open, Section 3) so the functional rail fully discharges, then re-run the activation sequence from step 3 of Section 5. Re-running discovery is not required if the descriptor was already validated in this session.
- Firmware update is a Unit API operation, not a pin operation: a Managed Unit that supports field update SHALL expose it through its Unit API and declare it in its capability flags. Hardware bootloader entry, where a controller needs it, is a Unit-internal matter (a test pad, a strap, a programming header) and SHALL NOT be exposed on the Unit Interface connector.

A Unit that genuinely requires host-controlled reset separately from power — one whose controller must stay powered while being reset — does not fit this profile and belongs on [`UIF-MSPI-14`](./uif-mspi-14.md), which defines `UIF_RESET_N`.

## 7. Identity, Discovery and Addressing

Presence is established by successful EEPROM discovery ([AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order)); there is no presence pin. The discovery mechanism is identical to every other UIF profile — same EEPROM layout, same validation order, same TLV extension records — so a host implements it once.

Because the Unit controller and the discovery EEPROM share one bus on this profile, address allocation is not optional. [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation) governs it. Restated for this profile:

- The discovery EEPROM lives in the reserved discovery block `0x50`–`0x57`, default `0x50`.
- The Unit API I²C target address SHALL lie outside that block and outside the I²C reserved addresses, and SHALL be declared in the EEPROM's Unit API Transport Address TLV record. A host SHALL NOT infer, default or hard-code it.
- A Unit SHALL NOT acknowledge any address other than its discovery EEPROM address and its declared Unit API address.

A Unit on this profile SHALL declare, per [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata): execution model `Managed`, profile identifier `UIF-MI2C-8`, profile version, Unit API identifier and version, capability flags (including whether event notification is used), the Unit API I²C address, and the applicable power fields. This is what lets a host decide, before asserting `UIF_PWR_EN`, that it can talk to the Unit at all.

## 8. Unit API

The Unit API is the semantic contract; this profile defines only its transport. The profile does not define the Unit's command set, which follows the Managed Unit API rules of the AURIORA Firmware Style Guide and is versioned and declared per [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata).

A Unit API on this profile SHALL be expressible as I²C transactions bounded by the profile's clock-stretch and payload limits, and SHALL NOT require the host to address the Unit's internal components directly. Internal devices behind the Unit controller — sensors, transceivers, external buses — are implementation detail and SHALL NOT appear on the Unit Interface I²C bus.

## 9. Applicability

The profile-selection rule and its criteria are [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection). Four planned Units are assessed against it — AEU, ASU, the Soil Unit and the Communication & Timing Unit — in the informative [worked example](../../examples/worked-example-unit-interface-profile-selection.md), which also works ASU through end to end.

The practical boundary is worth stating here: what takes a Unit off this profile is timing rather than volume. A distributed hardware time reference (a PPS-class sub-microsecond edge) cannot be carried by a generic event pin whose cause is resolved by an API query, so it fits neither this profile nor `UIF-MSPI-14` as specified. Such a need SHALL be met by a versioned profile addition, never by adding a Unit-specific signal to this profile.

## 10. Relationship to Other Profiles

| Against | Relationship |
|---|---|
| [`UIF-I2C-6`](./uif-i2c-6.md) | **Electrical superset on pins 1–6, mechanically distinct.** Signal order is identical, so PCB layout, ESD arrays and host firmware pin mapping carry over. The 8-position connector cannot mate with a 6-position one, so a Passive host cannot drive a Managed Unit and vice versa. `UIF-MI2C-8` additionally carries a second ground (Section 2.2), which `UIF-I2C-6` does not. The two profiles differ in *management model*, not transport: `UIF-I2C-6` hosts drive Unit peripherals directly; `UIF-MI2C-8` hosts speak only the Unit API. |
| [`UIF-MSPI-14`](./uif-mspi-14.md) | **Same management model, different transport.** Both serve Managed Units through a versioned Unit API with identical discovery, `UIF_READY` and event semantics, so Unit API and host software port between them. `UIF-MSPI-14` adds the SPI transport, `UIF_RESET_N` and a guarded 14-position connector for Units whose throughput, latency or deterministic timing I²C cannot serve. |

Because pins 1–6 match `UIF-I2C-6`, a passive 6-to-8 adapter that leaves pin 7 unmated and ties pin 8 to pin 2 is electrically safe in the direction of a `UIF-I2C-6` Unit into a `UIF-MI2C-8` host: the host pull-up holds `UIF_IRQ_N` de-asserted, and discovery reports the Unit's real profile, which the host then rejects or accepts on its own terms. Such an adapter is a bench convenience and is **not** a conformance path: a host SHALL make its accept/reject decision from the discovered profile identifier, never from the fact that a connector mated.

## 11. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | 8-position 1.00 mm JST SH, pinout per Section 2, both grounds populated end to end (part number OPEN). | Fit and insertion test; cross-profile mismating test against 6- and 14-position ports; cable continuity test on both ground conductors. |
| Electrical | Per Section 3 once numbers are fixed. | Power-limit, overcurrent, back-power and `UIF_IRQ_N`/`UIF_READY` defined-state tests with no Unit mated. |
| Communication | I²C discovery + EEPROM read succeeds before `UIF_PWR_EN`; Unit API address answers only after `UIF_READY`; clock stretching within bound. | Bus scan, metadata read, address-collision and clock-stretch-bound tests. |
| Semantic | Host validates descriptor including profile, API version and Unit API address, then asserts `UIF_PWR_EN`, waits `UIF_READY`, then speaks the Unit API. | Valid, incompatible, invalid-EEPROM, colliding-address and no-event-capability Unit tests. |

## 12. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft: eight-position Managed I²C Unit Interface for low-bandwidth Managed Units — `UIF-I2C-6` pins 1–6 plus generic `UIF_IRQ_N` and a second `GND`; no `UIF_RESET_N`; event notification optional in use, mandatory as a contact; shared-bus address allocation; clock-stretch contract. Electrical and mechanical limits left open. | Not release-binding |
