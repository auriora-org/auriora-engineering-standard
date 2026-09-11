# AURIORA Module Synchronization Interface (SYNC)

**Interface Identifier:** `SYNC`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [Architecture](../03-architecture.md)

This is the versioned specification of the **AURIORA Module Synchronization Interface**. The interface-independent rules — what SYNC is and is not, topology, event binding, arming, default behavior and observability ([AES-SYNC-001](../05-interfaces-and-versioning.md#aes-sync-001-sync-is-a-module-level-event-interface) to [AES-SYNC-004](../05-interfaces-and-versioning.md#aes-sync-004-sync-observability)) — live in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-module-synchronization-interface) and are not repeated here. This file defines the physical, electrical and timing layer and the SYNC Hub.

While this specification is Draft, it is not release-binding: no Module or Hub may claim Released conformance until the open items in Section 7 are resolved and the specification is versioned to a `1.x` release.

## 1. Purpose

SYNC lets one Module tell another *when* — and nothing else. A rising edge on SYNC IN means "an external synchronization event occurred now"; the receiving Module already knows from its configuration what to do with it. The same physical interface serves stimulus Modules that start a protocol on the edge, acquisition Modules that insert a marker into their timeline, and any future Module that needs a deterministic external time reference for an event.

SYNC is a Module-to-Module interface. It is not a Unit Interface Profile, it carries no `UIF_` signal, and it has no discovery, identity or power role. The electrical layer is RS-422-compatible differential signaling; SYNC is **not** an RS-422 or RS-485 communication protocol and has no baud rate, framing, addressing, command codes, checksum or message structure.

## 2. Physical Layer

- **Connector.** M8, 3-position, A-coded circular connector (IEC 61076-2-104 form), one connector per SYNC port. A Module provides a **SYNC IN** port, a **SYNC OUT** port, or both; the two ports are physically separate connectors, never a shared one.
- **Pinout.** Identical for SYNC IN and SYNC OUT:

| Pin | Signal | Notes |
|---:|---|---|
| 1 | `GND` | Signal reference, connected to the Module's ground |
| 2 | `SYNC_P` | Differential pair, non-inverting |
| 3 | `SYNC_N` | Differential pair, inverting |

  On the Module the nets are distinguished by port: `SYNC_IN_P`/`SYNC_IN_N` and `SYNC_OUT_P`/`SYNC_OUT_N`. A cable is a straight three-conductor assembly, pin 1 to pin 1, with `SYNC_P`/`SYNC_N` as a twisted or otherwise coupled pair.
- **Gender and keying — OPEN.** SYNC IN and SYNC OUT SHOULD be mechanically distinguishable from each other, and every SYNC connector SHALL either be prevented from mating with, or be electrically harmless when mated with, any other M8 interface present on the same AURIORA product family — including sensor or electrode inputs that may use the same 3-position A-coded form. The form is common in sensor and laboratory wiring, so an accidental cross-connection is a realistic event. The final gender assignment, keying and marking scheme is a Platform hardware decision and is recorded when it is made ([EDR-006](../edr/EDR-006-module-synchronization-interface.md) lists it as open); until then a Module's SYNC connector selection SHALL be recorded in its design notes together with the cross-mating analysis against every other M8 connector on the product family.
- **Labeling.** Ports are labeled `SYNC IN` and `SYNC OUT` on the enclosure.

## 3. Electrical Layer

- **Signaling.** RS-422-compatible differential signaling: one unidirectional differential pair per link, driven by a differential transmitter at SYNC OUT and received by a differential receiver at SYNC IN. There is no bus arbitration, direction control or addressing.
- **Transceiver class.** A 3.3 V-compatible, full-duplex RS-422/RS-485-compatible transceiver with separate receiver and transmitter differential pairs, a fail-safe receiver output for an open, idle or shorted input, and ESD-rated bus pins. Because SYNC IN and SYNC OUT are physically separate links, a half-duplex transceiver SHALL NOT be used as the single-device implementation of both ports. Part selection follows the Hardware Design Guide's parameter-based rules; this specification names no part.
- **Termination.** Termination belongs at the receiver: each SYNC IN provides a differential termination across `SYNC_P`/`SYNC_N` of nominally **120 Ω** (reference value, to be validated against the selected transceiver class and the cable's characteristic impedance). SYNC OUT and Hub outputs are not terminated as receivers.
- **Idle and fail-safe state.** The idle state of a link is the inactive (logic-LOW) state at the receiver output. With no cable connected, with a cable connected to an unpowered source, or with the pair shorted, a SYNC IN receiver SHALL resolve to the inactive state and SHALL NOT produce an event. Cable insertion or removal SHALL NOT produce an event. An unpowered Module SHALL NOT be back-driven through its SYNC pins.
- **Protection.** Every SYNC port is an external, user-wired connector and SHALL carry ESD/transient protection at the connector, ahead of the termination and the transceiver, per the Hardware Design Guide. The transceiver's internal ESD rating is not sufficient on its own.
- **Isolation — not required.** Galvanic isolation is not part of this version. `GND` on pin 1 is the link's reference and ties the two Modules' grounds through the cable; a design sensitive to ground loops records the consequence in its design notes.

## 4. Event Definition

- **Event edge.** The SYNC event is the **rising edge** of the differential signal (`SYNC_P` going positive relative to `SYNC_N`, receiver output going active). The rising edge is the event timestamp; the falling edge carries no meaning.
- **Pulse.** The transmitter drives a single active pulse per event and returns to idle. The pulse SHALL be long enough to be detected reliably by every conformant receiver. The **minimum pulse width** and a **nominal reference width** are open items (Section 7), to be fixed from transceiver and receiver-capture characterization; until then a Module SHALL make its SYNC OUT pulse width configurable or document the fixed value it uses.
- **One meaning.** Pulse width, pulse count, pulse spacing and inverted polarity SHALL NOT be used to distinguish events ([AES-SYNC-001](../05-interfaces-and-versioning.md#aes-sync-001-sync-is-a-module-level-event-interface)). A transmitter SHALL NOT emit more than one pulse for one event, and a receiver SHALL treat every rising edge as a separate event.
- **Minimum event spacing.** A receiver is not required to resolve two events closer than the minimum pulse width plus its capture dead time; the figure is a Module characterization item, documented with the Module.

## 5. SYNC Hub

A SYNC Hub is an active fan-out device with one SYNC IN and *N* SYNC OUT ports, all conforming to Sections 2–4.

- **Function.** The Hub receives the input event through a standard SYNC IN receiver (terminated as a receiver) and regenerates it onto every output through a standard SYNC OUT transmitter. It performs no filtering, stretching, gating, counting or interpretation. Its output pulse follows the input pulse: the source defines the pulse width, not the Hub.
- **No intelligence.** The baseline Hub requires no controller and no firmware; it is a receive → regenerate → distribute circuit. A simple realization uses one transceiver of the standard class per output, with the first device's receiver serving as the input and its transmitter as the first output, and the receiver output fanned out to every transmitter data input. A separate logic buffer is added only where loading or timing analysis shows it is needed.
- **Timing.** A Hub SHALL document its input-to-output propagation delay, channel-to-channel skew and, where relevant, jitter as measured values. A Hub is never described as zero-delay.
- **Cascading.** Hubs MAY be cascaded (a Hub output driving another Hub's input). Each stage remains point-to-point; delays accumulate stage by stage; an experiment that depends on absolute timing records the SYNC topology in its configuration or log. No maximum depth is fixed in this version.
- **Power.** The Hub is powered independently of the Modules it connects. Loss of Hub power SHALL leave every output in the idle state, not toggling.

## 6. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | M8 3-position A-coded; pin 1 `GND`, pin 2 `SYNC_P`, pin 3 `SYNC_N`; gender and keying per Section 2 once fixed. | Fit check against every other M8 port on the product family; mis-mate harmlessness check in both directions. |
| Electrical | RS-422-compatible differential pair; receiver-side ~120 Ω termination; fail-safe idle; protection at the connector. | Inactive state with open, unpowered-source and shorted input; no event on cable insertion or removal; transient test per the Hardware Design Guide. |
| Event | Rising edge is the event; one pulse per event; no meaning in width or count. | Edge-to-action latency and jitter measured over at least 100 events; a widened or doubled pulse produces no additional action. |
| Behavioral | Armed gate, ignore-while-running default, explicit post-completion mode, configured SYNC OUT source ([AES-SYNC-003](../05-interfaces-and-versioning.md#aes-sync-003-event-binding-arming-and-default-behavior)). | Unarmed and mid-run events are logged as ignored and cause no action; the SYNC OUT edge coincides with the configured internal event within the documented latency. |
| Observability | Received, transmitted and ignored events logged with timestamp, state, reason, run identifier and local counter; configuration readable ([AES-SYNC-004](../05-interfaces-and-versioning.md#aes-sync-004-sync-observability)). | Counter comparison across sender and receivers after a run detects a deliberately dropped event. |

## 7. Open Items (require a hardware decision or characterization)

The following are **OPEN** and deliberately unresolved in this Draft. They are decided from bring-up measurements of the first SYNC-capable Modules and a SYNC Hub, and recorded before this specification reaches `1.0`:

- Connector gender for SYNC IN and SYNC OUT, keying and marking, and the cross-mating analysis against other M8 interfaces on AURIORA products.
- Minimum detectable pulse width and the nominal reference pulse width; minimum event spacing.
- Termination value confirmed against the selected transceiver class and cable impedance; cable construction, characteristic impedance and maximum cable length.
- Receiver fail-safe and logic thresholds; common-mode range required for the intended cable lengths.
- ESD/transient protection level.
- Edge-to-action latency and jitter budget expected of a conformant Module; Hub propagation delay, skew and jitter figures; whether a maximum cascade depth is needed.
- Identity and naming of the SYNC Hub product, and whether SYNC-capable artifacts need an AOID interface class.

## 8. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft: Module-level RS-422-compatible differential event interface, M8 3-position pinout, receiver-side termination, rising-edge event, active SYNC Hub; connector gender/keying, pulse width, cable and protection figures left open. | Not release-binding |
