# EDR-006: Module Synchronization Interface

## Status

Accepted (2026-09-11)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module relies on this interface.*

## Context

AURIORA experiments combine Modules: a stimulus Module starts a protocol, an acquisition Module records the response, further Modules add stimuli or markers. Reproducibility depends on knowing *when* each of those things happened relative to the others, to a precision that host software talking to each Module over its Host Interface cannot deliver — command latency over USB, BLE or a serial link is variable, and it is not logged at the moment of physical action.

The first Audio Module hardware revision reserved two controller GPIOs, `SYNC_IN` and `SYNC_OUT`, as single-ended 3.3 V logic on a pin header, with no defined pulse, polarity, topology, protection or behavior, and the corresponding firmware plan sketched a configuration in which one output line would pulse on a selectable *mask* of internal events. Left alone, this pattern spreads: each Module grows its own sync pins, its own levels and its own implicit meanings, and two Modules from the same Platform do not synchronize without a per-pair adapter and a per-pair agreement about what a pulse means.

AES had no Module-to-Module interface class. It defines the Host Interface (Module to computer) and the Unit Interface (Module to Unit). The Unit Interface Profiles mention profile-defined synchronization signals, but those are Unit-to-host signals inside one Module, and [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md) records a distributed hardware time reference as an unmet need on the Managed profiles. None of this addresses Module-to-Module event timing.

This is a Platform interface decision — a new interface class, a new versioned interface specification and new normative requirements — and therefore requires an EDR under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger).

## Alternatives Considered

### What SYNC carries

| Alternative | Assessment |
|---|---|
| **A messaged synchronization protocol** (UART, CAN, RS-485 messaging, or timestamped packets carrying event type and parameters) | Rejected. Framing, parsing and arbitration add latency and jitter at exactly the point where the requirement is a timestamp. Every receiver must implement the protocol and its versioning; a passive instrument such as an oscilloscope or a DAQ cannot consume it. Commands and data already have a home: the Host Interface. |
| **Meaning encoded in the pulse itself** (short and long pulses, pulse counts, double pulses for different actions) | Rejected. Lost pulses desynchronize receiver state; width tolerances complicate every receiver; the receiver still needs a table mapping patterns to actions, so nothing is saved over configuring the action directly. It is a protocol without framing. |
| **Automatic forwarding of SYNC IN to SYNC OUT** as the chaining mechanism | Rejected as default behavior. The output would then mark reception of the trigger, not the Module's actual action, and the timing value of SYNC OUT is precisely that it marks what physically happened. Forwarding remains available as an explicitly configured source. |
| **A single event edge; the receiver's configuration supplies the meaning** | **Chosen.** One edge, one meaning: "an event occurred now". Control tells a Module what to do; SYNC tells it when. Works identically for stimulus Modules (start a configured protocol), acquisition Modules (insert a marker) and third-party instruments that only need an edge. |

### Physical layer

| Alternative | Assessment |
|---|---|
| **Single-ended 3.3 V logic on a header** (the first Audio Module revision) | Rejected. No noise margin over laboratory cable lengths, ground-shift sensitive, no defined protection, not a connector a user can wire. Acceptable only as a bring-up expedient inside one enclosure. |
| **Optically isolated single-ended input** | Rejected for the baseline. Removes ground loops but adds optocoupler delay and temperature-dependent jitter, and complicates the Hub. Isolation is recorded as a possible future variant, not part of `0.1`. |
| **RS-485 half-duplex multidrop bus** with all Modules on one pair | Rejected. A multidrop bus needs direction control, biasing and exactly two terminations, and turns every Module into a potential driver on a shared line; a fault on one node disturbs all. It also invites the messaged-protocol path above. |
| **RS-422-compatible differential signaling, point-to-point, one pair per direction** | **Chosen.** Robust over metres of cable, ground-shift tolerant, uses a standard transceiver class, needs one termination per link at the receiver, and lets SYNC IN and SYNC OUT be two independent links on one full-duplex device. Explicitly *not* an RS-422 protocol: only the electrical layer is borrowed. |

### Fan-out

| Alternative | Assessment |
|---|---|
| **Passive splitters or parallel wiring** | Rejected. Multiple terminations on one driver, reflections, undefined loading; timing depends on how many receivers happen to be connected. |
| **Daisy-chain through each Module** (SYNC IN forwarded to SYNC OUT) | Rejected as a required topology. Latency accumulates through firmware on every hop, and a powered-down Module breaks the chain. |
| **Active SYNC Hub** (receive → regenerate → distribute, no controller) | **Chosen.** Each output is an independent point-to-point link with its own termination; the Hub adds a finite, measurable, stable hardware delay and no semantics. Cascadable when needed. |

### Connector

| Alternative | Assessment |
|---|---|
| Pin header or board-to-board connector | Rejected — not user-wireable, no protection, no strain relief. |
| BNC or SMA (laboratory trigger convention) | Rejected as the Platform connector. Single-ended by construction; would force a differential-to-single-ended conversion or abandon the differential layer. Adapters to BNC for third-party instruments remain a legitimate accessory. |
| **M8 3-position A-coded circular connector** | **Chosen**, with gender and keying left open. Compact, sealed, locking, and three contacts is exactly the signal set. Its ubiquity is also its risk: the same form is common in sensor and electrode wiring and may appear on other ports of the same equipment, so the specification requires a cross-mating analysis and a mitigation before `1.0`. |

### Behavior on the receiving Module

| Alternative | Assessment |
|---|---|
| React to every pulse whenever it arrives | Rejected. A stray edge starts an experiment; a retrigger mid-run silently restarts or stops it. |
| **Armed gate, ignore-while-running default, explicit post-completion mode** | **Chosen.** The Module executes only what it was configured and armed for; anything else is logged as ignored. Restart, advance or queue behaviors remain possible as explicit Module configuration, never as implicit SYNC semantics. |

## Decision

1. AES gains a third interface class, the **Module Synchronization Interface (SYNC)**: a Module-to-Module, point-to-point, RS-422-compatible differential event interface carrying a single rising-edge event and no data. Its interface-independent rules are [AES-SYNC-001](../05-interfaces-and-versioning.md#aes-sync-001-sync-is-a-module-level-event-interface) to [AES-SYNC-004](../05-interfaces-and-versioning.md#aes-sync-004-sync-observability) in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-module-synchronization-interface); its physical, electrical and timing layer is the versioned specification [`docs/interfaces/sync.md`](../interfaces/sync.md) (`0.1`, Draft).
2. SYNC is not part of the Unit Interface. Units do not expose or consume it; profile-defined synchronization signals in Unit Interface Profiles are unrelated Unit-to-host signals.
3. Fan-out is performed by an active, controller-less **SYNC Hub**; passive multidrop and required daisy-chaining are excluded.
4. The connector is **M8, 3-position, A-coded**: pin 1 `GND`, pin 2 `SYNC_P`, pin 3 `SYNC_N`, identical on SYNC IN and SYNC OUT. Gender, keying and the cross-mating mitigation are open and will be recorded in a supplementary or superseding record when fixed.
5. A receiving Module implements an armed gate, ignore-while-running as the default retrigger policy, an explicit one-shot or re-arm post-completion mode, a configurable SYNC IN action and a configured SYNC OUT source — all visible through the Host Interface and in the event log with local counters.
6. Module-specific supported actions and sources are documented with each Module, not in AES.

## Rationale

The decision puts the meaning where it can be versioned, read back and logged — in Module configuration — and leaves the wire with the one property a wire does well: timing. Everything a protocol would add (type, parameters, acknowledgment) is already available over the Host Interface at a rate and latency appropriate to configuration, not to triggering.

Differential point-to-point signaling is the cheapest layer that is robust over laboratory cable runs and lets a Hub be a pure hardware device. A Hub with no firmware has a delay that can be measured once and trusted; a Hub with firmware has a delay that depends on its load.

Arming is what turns a physical trigger into a reproducible one. The experiment is defined by "configure, arm, wait", and the log records every pulse that arrived outside that window. This is also the safety posture [AES-MOD-004](../03-architecture.md#aes-mod-004-safety-policy-ownership) expects: the Module, not the cable, decides when its outputs change.

The interface is defined firmly where the architecture is settled and left open where only hardware will tell: pulse width, cable length, fail-safe thresholds, protection level and connector gender are recorded as open items rather than guessed, following the same discipline as the Draft Unit Interface Profiles.

## Consequences

- AES gains requirements `AES-SYNC-001` to `AES-SYNC-004`, supporting terms for the interface, the SYNC event, the SYNC Hub, the SYNC IN action and the SYNC OUT source, a new versioned interface specification and this record. The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) and the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) each gain an implementation section (§5.1 and §14.2 respectively).
- The Audio Module's reserved single-ended `SYNC_IN`/`SYNC_OUT` GPIOs and its planned multi-event output mask do not conform. The next Audio Module hardware revision and its firmware are expected to align: differential ports on M8 connectors, one configured SYNC OUT source, an armed SYNC IN action and the SYNC event log. The same applies to the Plant Electrophysiology Module before it acquires a SYNC port.
- **Standard-form naming, deliberately and narrowly.** [EDR-004](./EDR-004-default-controller-platforms.md) records that AES names vendor platforms in one place and that any further specific naming needs its own decision. This EDR is that decision for the SYNC connector: the specification names the **M8 3-position A-coded** connector form because a complete interface contract requires a named physical connector ([AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness) sets that bar for Unit Interfaces and SYNC follows it) and because a cross-mating analysis is only meaningful within a named form. M8 is a standardized connector form (IEC 61076-2-104), not a vendor part; no transceiver, protection device or cable part is named anywhere in the standard or the guides.
- SYNC does **not** answer the distributed hardware time reference (PPS-class) need recorded in [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md). SYNC marks events; it does not distribute a clock. That item stays open.
- The specification is **Draft**: no Released conformance may be claimed until its electrical layer is fixed and it reaches `1.x`.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

Not resolved here; they belong to the SYNC `1.0` finalization, informed by the first SYNC-capable Module and Hub bring-up:

- Connector gender for SYNC IN and SYNC OUT, keying, marking, and the cross-mating analysis against other M8 interfaces on AURIORA products.
- Minimum and nominal pulse width; minimum event spacing.
- Termination value, cable construction and impedance, maximum cable length.
- Receiver fail-safe and logic thresholds; common-mode range.
- ESD/transient protection level.
- Latency and jitter budget of a conformant Module; Hub propagation delay, skew and jitter; whether a maximum cascade depth is needed.
- SYNC Hub product identity and naming; whether an AOID interface class is needed for SYNC.

## Affected Requirements / Documents

- [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-module-synchronization-interface) — new section; `AES-SYNC-001` to `AES-SYNC-004` (new).
- [`docs/interfaces/sync.md`](../interfaces/sync.md) — new specification.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — supporting terms.
- [Architecture §3](../03-architecture.md#3-module-design) — Module Design note on SYNC.
- [Worked Example: Module Synchronization](../../examples/worked-example-module-synchronization.md) — informative.
- [Document Index](../document-index.md), `STANDARD.md` — indexing.

## Future Review Criteria

Revisit if: a use case needs data or multiple distinct commands on the synchronization path (the answer is a control interface, not a SYNC extension); galvanic isolation becomes necessary for a Module class; a distributed clock or time reference becomes a Platform requirement; or the M8 cross-mating analysis shows that a different connector form is the only safe mitigation.
