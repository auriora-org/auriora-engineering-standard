# AURIORA Event Link (AEL)

**Interface Identifier:** `AEL`
**Version:** `0.2`
**Status:** Draft
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [Architecture](../03-architecture.md)

This is the versioned specification of the **AURIORA Event Link**. The interface-independent rules — what AEL is and is not, topology, event identifiers and Module bindings, timing and observability, Hub routing ([AES-AEL-001](../05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface) to [AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)) — live in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link) and are not repeated here. This file defines the electrical layer, the event frame and its encoding, the timing reference and the behavior of an AEL router; the connector and cable through which AEL links leave a device are the [Module Port specification](./module-port.md).

While this specification is Draft, it is not release-binding: no Module or Hub may claim Released conformance until the open items in Section 10 are resolved and the specification is versioned to a `1.x` release. Section 10 separates what this Draft has **settled** from what is still **open**, so that an implementer knows which parameters may still move.

## 1. Purpose

AEL lets one Module tell another **which** configured event occurred and **when** — and nothing else. An AEL event frame carries a numeric event identifier; the receiving Module already knows from its bindings what that identifier means to it, and the deployment record knows what it meant to the experiment. The same link serves a stimulus Module that starts a protocol on one identifier and changes phase on another, an acquisition Module that inserts markers while recording and emits a detector event of its own, and any future Module that needs to react to, or announce, a deterministic event.

AEL is a Module-to-Module interface. It is not a Unit Interface Profile, carries no `UIF_` signal and has no discovery, identity or power role. It is not a control interface: a Module is discovered, configured, loaded and armed over [MCI](../05-interfaces-and-versioning.md#5-module-control-interface); AEL carries the events of the experiment once the Modules are prepared. It is not a data path: measurements, logs and Assets never travel in an AEL frame. Although its frame is carried with UART-class character framing, AEL is not a serial communication protocol: it has no addresses, commands, payload, acknowledgment or flow control.

## 2. Topology

Every AEL link is one **AEL OUT** driving one **AEL IN**. Three paths exist and carry the *same* frame:

```text
direct     Module A  AEL OUT ─────────────────────────────► AEL IN  Module B

routed     Module A  AEL OUT ──► Module Hub (AEL router) ──► AEL IN  Module B
                                                          └► AEL IN  Module C

multi-Hub  Module A  AEL OUT ──► Hub 1 ──Hub-to-Hub AEL link──► Hub 2 ──► AEL IN  Module D
```

A Module cannot tell, and must not need to know, which path a frame took. A Hub is optional infrastructure, never a prerequisite for two Modules to exchange events. Hub-to-Hub AEL links carry the same frame with the identifier unchanged; the topology of Hub-to-Hub links is **acyclic** (a tree or a chain), so a frame cannot circulate. Experiment-level feedback — Module A's event causes an action on Module B whose completion event causes an action on Module A — is a legitimate experiment design and is not a routing loop; it is validated by the host, not prevented by the network.

A Module's AEL IN and AEL OUT leave the device through its single **Module Port**, which packages them with `MCL` in one connector and one **AURIORA Link Cable** ([Architecture §7.1](../03-architecture.md#71-the-module-port), [Module Port specification](./module-port.md)); the links remain electrically and semantically independent inside it. The direct path is one Link Cable between two Modules; the routed paths are Link Cables between Modules and Hub ports and between Hubs.

## 3. Physical Layer

AEL has no connector of its own. A Module's AEL IN and AEL OUT are two of the three differential links carried by its single **Module Port** — an M8 8-position A-coded female connector shared with `MCL` — and leave the device through it ([Module Port specification](./module-port.md), [Architecture §7.1](../03-architecture.md#71-the-module-port)). The standalone M8 3-position AEL ports of AEL `0.1` are withdrawn ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)).

- **Contacts.** The Module Port carries `AEL_IN_P`/`AEL_IN_N` — the received pair, terminated at this device — and `AEL_OUT_P`/`AEL_OUT_N` — the driven pair — with the Module Port's `GND` contact as the reference of both. `P` is the non-inverting and `N` the inverting side. The position numbering is assigned in the Module Port specification; the contact roles and net names are fixed.
- **Cable.** Module Ports are connected only by the **AURIORA Link Cable**, which crosses AEL OUT to AEL IN with polarity preserved, so that one non-oriented cable joins a Module to a Hub port, a Module directly to one peer Module, and a Hub to a Hub. A generic straight-through M8 8-position cable connects two AEL OUT drivers to one pair and is **not compatible**; every port survives one indefinitely without emitting a valid frame (Module Port specification Section 5.1).
- **Direct operation is 1:1.** Two Modules joined by one Link Cable exchange events in both directions with no infrastructure. Three or more Modules in one event exchange use an AEL router.
- **Router ports.** On a Module Hub every Module Port is a router port pair — its `AEL_IN` pair a router ingress, its `AEL_OUT` pair a router egress — and a Hub-to-Hub link port is a Module Port connector whose Link Cable carries one link in each direction (Section 8.6).
- **Adapters and instruments.** An AEL-to-trigger adapter or a test fixture presents a Module Port and is connected with a Link Cable like any other device.
- **Labeling.** `AEL IN` and `AEL OUT` name links, not connectors, and do not appear on an enclosure; the connector is labeled as the Module Port specification requires.

## 4. Electrical Layer

- **Signaling.** Point-to-point differential signaling: one unidirectional differential pair per link, driven by a differential driver at AEL OUT and received by a differential receiver at AEL IN. There is no bus arbitration, direction control or addressing on the wire, and never more than one driver on a pair. AEL IN and AEL OUT are therefore two simplex links, not one bidirectional link: a single half-duplex AEL pair would let two legitimate events collide with no recovery, or need a medium-access rule that couples a Module's event latency to its peer's traffic, and was rejected ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)).
- **Electrical profile — OPEN.** The intended direction is an **RS-485-compatible driver/receiver electrical contract** (driver levels, receiver sensitivity, common-mode range) used in AEL's point-to-point topology. Which standard or profile AEL normatively follows, and with it the driver output requirements, receiver threshold, common-mode range and termination assumptions, is decided explicitly before `1.0` (Section 10). This specification does not treat RS-422 and RS-485 as interchangeable and does not quote threshold or common-mode numbers until the profile is chosen.
- **Transceiver class.** A 3.3 V-compatible differential transceiver with separate receiver and driver pairs, a **true fail-safe** receiver (defined receiver output for open, shorted and idle inputs — a property that SHALL be established from the device's specification, not assumed of every generic RS-422/RS-485 receiver), ESD-rated bus pins, and a rated data rate with margin above the AEL bit rate (Section 5.3). Because AEL IN and AEL OUT are physically separate links, a half-duplex transceiver SHALL NOT be used as the single-device implementation of both ports. Part selection follows the Hardware Design Guide's parameter-based rules; this specification names no part.
- **Termination.** Termination belongs at the receiver: each AEL IN provides a differential termination across `AEL_IN_P`/`AEL_IN_N`; **120 Ω** is the reference design assumption, to be validated against the selected transceiver, connector, PCB, cable and length (Section 10). AEL OUT and Hub outputs are not terminated as receivers.
- **Logical idle and fail-safe.** AEL defines a **logical idle state** — the state of a link on which no frame is in progress — which in the baseline encoding is the UART mark state, logic HIGH at the receiver output (Section 5.2). The AEL receiver path SHALL provide fail-safe behavior such that an open input, a disconnected cable, an unpowered or resetting remote transmitter and a shorted differential pair resolve to the logical AEL idle state and cannot by themselves produce a valid AEL event; cable insertion and removal SHALL NOT produce one either. Physical line activity, a framing error or an integrity failure is never an event.
- **Protection.** Every AEL link enters a device through its Module Port, an external, user-wired connector, and SHALL carry ESD/transient protection at that connector, ahead of the termination and the transceiver, per the Hardware Design Guide. The transceiver's internal ESD rating is not sufficient on its own. ESD and transient levels are product and guide matters, not fixed here.
- **No back-drive.** An unpowered device SHALL NOT be back-driven through, and SHALL NOT source current into, its AEL pins.
- **Power-up, power-down and reset.** A device SHALL NOT emit a valid AEL frame as a consequence of powering up, powering down, resetting, or having a cable inserted or removed. A transmitter that cannot guarantee a defined line state through these transitions holds its output disabled until it can.
- **Isolation — not required.** Galvanic isolation is not part of this version. The Module Port's `GND` contact is the link's reference and ties the two devices' grounds through the cable; a design sensitive to ground loops records the consequence in its design notes.

## 5. Event Frame

### 5.1 Frame format

An AEL event frame is exactly **four bytes**:

| Byte | Content | Rule |
|---:|---|---|
| 0 | `event_id[15:8]` | Event identifier, most significant byte first (big-endian) |
| 1 | `event_id[7:0]` | `0x0000` is reserved as invalid/unbound and is never transmitted as an event (Section 6) |
| 2 | `CRC[15:8]` | 16-bit integrity check over bytes 0 and 1 in transmitted order (Section 5.4) |
| 3 | `CRC[7:0]` | |

Nothing else is in the frame: no source or destination address, Module identity or AOID, textual name, payload or parameters, timestamp, sequence number, priority or class, and no experiment logic. Routing and topology already know where a frame came from and where it goes; the deployment record knows what the identifier meant. A field is added only through a new version of this specification justified by a requirement that bindings, topology or the deployment record cannot satisfy.

Meaning SHALL NOT depend on inter-frame spacing or repetition; the identifier is the only semantic content, and two identical frames are two events.

### 5.2 Character framing and idle

The frame is carried as **UART-class asynchronous NRZ characters, 8N1**: one start bit (space, logic LOW), eight data bits least-significant bit first, no parity, one stop bit (mark, logic HIGH). The **logical AEL idle state is mark (HIGH)**; a start bit is the transition mark → space. The former SYNC rule that defined the inactive state as LOW does not apply to AEL.

Under this encoding the fail-safe requirement of Section 4 has a concrete form: a true fail-safe receiver resolves an open, shorted or unpowered-source input to mark, which is idle, so no fault condition resembles the start of a frame. A line stuck at space is seen as a break — a framing error, counted, never a frame — and even the byte pattern such a line would produce, `00 00 00 00`, is not a valid frame: `event_id 0x0000` is reserved and the integrity check over `00 00` is `0x1D0F`, not `0x0000`.

### 5.3 Bit rate

The **Draft baseline bit rate is 1 Mbit/s**. It is a design baseline that the first AEL-capable Modules and a Hub validate against real transceivers, connectors and cables before `1.0`; it is not a claim about achievable cable length. At 1 Mbit/s one character is 10 µs, a frame is 40 µs, and with the minimum inter-frame gap of Section 5.5 the minimum frame-to-frame period is about 60 µs — a theoretical ceiling of roughly 16 000 events per second per link, well above the event rates of biological experiments. Faster speed classes MAY be introduced later only as an explicit, versioned extension.

### 5.4 Integrity check

The integrity check is a 16-bit CRC with the following complete parameterization, over the two `event_id` bytes in transmitted order:

```text
width  = 16
poly   = 0x1021
init   = 0xFFFF
refin  = false
refout = false
xorout = 0x0000
check  = 0x29B1      (CRC of the ASCII string "123456789")
```

The name "CRC-16/CCITT" is ambiguous across implementations and is not used normatively; the parameters above are. The specification defines the result, not the method: hardware acceleration is welcome where a controller offers a compatible unit and is not assumed of any platform, and a software computation over two bytes is entirely acceptable.

### 5.5 Inter-frame gap and resynchronization

Frames are delimited by **idle**, not by a start-of-frame byte.

- A transmitter SHALL keep the link in AEL idle for at least **two character times** between the end of one frame and the start of the next, and SHALL transmit the four characters of a frame contiguously — any idle between characters of one frame SHALL be shorter than one character time.
- A receiver SHALL treat continuous idle of at least two character times as a **qualifying gap**, and MAY treat idle of one character time or more between characters of a candidate frame as a framing violation.
- A receiver operates conceptually as: *wait for a qualifying gap → receive exactly four characters → require the next qualifying gap → validate*. The candidate frame is invalid, in its entirety, if fewer or more than four characters arrive between two qualifying gaps, if any character carries a UART framing error, if the CRC does not match, if `event_id` is `0x0000`, or on any other framing violation. Only a complete, valid four-byte frame reaches the binding or routing layer.

This makes resynchronization bounded and deterministic: a receiver that joins mid-stream or sees corruption discards at most until the next qualifying gap, then frames correctly again. It also fixes a latency property implementers must plan for: because a frame is confirmed only by the gap that follows it, the earliest instant at which a receiver may act is one frame plus one qualifying gap after the frame reference instant (Section 7).

### 5.6 What is not on the link

There is no acknowledgment, no flow control and no retransmission. A frame that fails framing or integrity is dropped, counted and reported by the receiver that saw it; it is never forwarded, acted on or retried. A retry would be a new event at a different instant, and an event interface that retries has lost the property it exists for. Loss is made visible through counters and logs ([AES-AEL-004](../05-interfaces-and-versioning.md#aes-ael-004-deterministic-timing-and-observability)), not repaired on the wire.

## 6. Event Identifiers

- **Width and reserved value.** `event_id` is a 16-bit unsigned integer. `0x0000` is reserved as *invalid/unbound* and is the safe default of an unconfigured binding; a receiver treats a frame carrying `0x0000` as invalid.
- **Scope.** Identifiers are **deployment-scoped**: they are allocated by the host for one deployment and mean nothing outside it. AES maintains no registry of event identifiers and assigns no Platform-wide meaning to any value.
- **Routing-domain uniqueness.** An **AEL routing domain** is the set of AEL endpoints interconnected by active AEL links and routes during one deployment. Within a routing domain, one logical event source SHALL map to one identifier and one identifier SHALL be emitted by one logical event source. Two Modules that can emit into the same routing domain SHALL NOT be given the same identifier for two different events, even if the events are semantically similar. Two routing domains that are physically and logically separate MAY reuse the same values. This rule is what allows a frame to omit a source address and cross several Hubs unchanged.
- **Semantic names stay off the wire.** Names such as `detector_a_fired` or `phase_complete` exist in the experiment definition and in the Module's declared event sources and actions ([AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery)); the host maps them to identifiers before the run and stores the mapping in the deployment record so that every logged `event_id` can be decoded afterwards.
- **Hubs never rewrite identifiers.** A frame leaves a Hub with the identifier it arrived with.

## 7. Timing Reference

Three instants are distinct and are named separately in every timing statement:

1. **Source event occurrence** — the physical or logical event inside the originating Module: a detector threshold crossing, the first stimulus sample leaving a converter, a protocol phase ending.
2. **Frame reference instant (SOF)** — the **start-bit transition of the first character of the frame after a qualifying idle gap**: the mark → space edge that begins byte 0. It is the same physical event at the transmitter and at the receiver, offset by propagation. How a device captures it — timer input capture, a UART-related hardware feature, programmable logic or an equivalent mechanism — is an implementation choice and is not prescribed.
3. **Action execution** — the instant the receiving Module's configured action takes physical effect after the frame has been received completely, confirmed by the following gap, and validated.

Consequences of this model:

- A receiver **timestamps at the frame reference instant** and **acts only after the complete frame is valid**. With the baseline encoding the action therefore trails the reference instant by at least one frame plus one qualifying gap (about 60 µs at 1 Mbit/s) plus validation and the Module's own reaction; that latency is bounded and characterized per Module, and a configured delay counts from the captured reference instant, not from validation.
- A transmitter emits the frame so that its reference instant follows the source event occurrence with a characterized, bounded latency — the frame marks what physically happened, not when a command arrived.
- A router distinguishes its **input SOF timestamp** and its **output SOF timestamp** per frame; each routing hop adds at least one frame plus one gap (store-and-forward, Section 8) plus the router's own forwarding latency. Multi-hop latency accumulates and is characterizable from the per-hop figures and the recorded topology.
- The frame carries no timestamp. Receivers timestamp locally, as close to hardware as practical, in local time and — where the Module has one — as a sample or frame index in its acquisition clock. Cross-Module time alignment beyond what the event itself provides is a separate concern, not an AEL function.

AEL does not require nanosecond-class latency. It requires bounded latency, bounded jitter, deterministic behavior and published figures; a device declares its timing envelope and the host validates a deployment against it. No numeric latency, jitter or skew limit is fixed by this Draft.

## 8. AEL Router

An **AEL router** is the event-routing function of a Module Hub, or a standalone AEL Hub. It has *N* AEL IN ports and *M* AEL OUT ports — on a Module Hub, the `AEL_IN` and `AEL_OUT` pairs of its Module Ports — and optionally one or more **Hub-to-Hub AEL link** ports; every port conforms to Sections 3–5. Its behavior is governed by [AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior); this section states the mechanism.

### 8.1 Forwarding

```text
frame arrives on ingress port P            → input SOF timestamp, count RX
complete frame + following gap received     → validate UART framing, CRC, event_id
invalid                                     → drop, count, report; nothing forwarded
valid                                       → route lookup (P, event_id) → output set
output set                                  → enqueue on each selected output; launch within skew bound
frame transmitted on each output            → output SOF timestamp, identifier unchanged, count TX per port
```

- **Store-and-forward.** A router forwards nothing before the complete frame has been received, confirmed by its following gap, and validated. There is no cut-through: a corrupt frame stops at the first router that sees it.
- **Route key and output set.** The route table maps `(ingress port, event_id)` to a set of zero or more outputs, where an output is an AEL OUT port or a Hub-to-Hub link. An event with no route is dropped and counted as unrouted; it is not an error, it is a fact the host can read.
- **No interpretation.** The router knows ports, identifiers and routes. It does not know, and cannot be configured with, what an identifier means, which Module is on a port beyond what `MCL` management separately tells the Hub, or any experiment state. A router SHALL NOT contain conditional experiment logic.
- **No modification.** The forwarded frame carries the identifier it arrived with. A router does not merge, split, delay-by-policy, re-order by priority or suppress duplicates.
- **Router as event source.** A Module Hub MAY additionally *originate* events — a host-requested `T0`, a scheduled marker — as an **AEL event source** with its own source bindings. Origination is a distinct role from routing and is subject to the same frame and identifier rules; an originated event enters the route table like any ingress event.

### 8.2 Fan-out skew

All outputs selected by one AEL routing decision SHALL begin transmission within a **declared maximum channel-to-channel skew**, documented by the router. "Simultaneous" is not claimed; the skew is a measured figure. Fan-out skew (outputs of one decision, inside one router) and path latency (accumulated across hops) are two separate figures and are documented separately.

### 8.3 Queueing, arbitration and overload

Two ingress events may select the same output while it is transmitting. A router SHALL define and document:

- **queue capacity** per output, or the shared capacity and how it is divided;
- the **arbitration and ordering rule** — for example arrival order at the input SOF timestamp — applied deterministically;
- behavior when an **output is busy** — the frame is queued, never interleaved, never truncated, and the inter-frame gap of Section 5.5 is always honored;
- the **maximum sustained and burst event rate** the router supports without overflow;
- **overflow behavior** — which frame is dropped when capacity is exceeded, counted per output and reported as a fault. Overflow SHALL never be a silent loss.

AES does not fix one arbitration algorithm; interoperability does not depend on it. It does require that every router publish enough of these figures for a host to validate a deployment against them.

### 8.4 Route configuration lifecycle

```text
stage   → the host transfers a complete route table and its integrity value
validate→ the router checks capacity, port existence and consistency; reports the result
commit  → the validated table becomes the active table; the router reports its identity
```

- The **active route table SHALL NOT change** while a deployment that depends on it is `ARMED` or `RUNNING`, except through an explicitly defined abort, fault or recovery operation that is itself observable. A table prepared during a run is staged for later activation and does not alter the running experiment.
- The committed table SHALL have a **content identity** (a hash or equivalent) readable by the host, so that the deployment record can prove which routing was in force.
- A route change SHALL NOT glitch a link or emit a spurious frame.
- Loss of router power, or a router reset, SHALL leave every output in AEL idle. On recovery the router reinstates nothing unless the host has set a **route recovery policy** of *reinstate* ([AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)); then it restores the last committed table only after verifying its content identity, records the reinstatement with the reset cause and reports it to the host — the counterpart of a Module's recovery under [AES-MCI-007](../05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance). Under the default policy, *none*, the host verifies and re-commits, exactly as a Module is never re-armed by reconnection ([AES-MCI-004](../05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary)).

### 8.5 Observability

A router SHALL expose per port: received, forwarded, unrouted, invalid (framing / integrity / reserved identifier) and overflowed frame counts, link state, and — where it timestamps — the input and output SOF timestamps of recent frames; and globally: the active and staged route table identities, its supported AEL version, its port topology, its route and queue capacity, and its documented timing figures. Counters are local to the router and are not presented as synchronized with any Module.

### 8.6 Hub-to-Hub links and depth

A Hub-to-Hub AEL link is an AEL OUT on one router driving an AEL IN on another, carrying unchanged frames; a router treats a frame arriving on such a link as an ingress event like any other. Physically a Hub-to-Hub link port is a Module Port connector, and one AURIORA Link Cable between two such ports carries a link in each direction ([Module Port specification](./module-port.md)). The number of such links a router provides is a product decision. The topology formed by Hub-to-Hub links SHALL be acyclic; the host validates this before deployment, and no run-time mechanism (hop count, spanning tree, duplicate suppression) exists to compensate for a cycle. A link whose cable joins a downstream Hub's link port to an upstream Hub's Module Port is also an `MCL` cascade ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)) and is known to the host from discovery; a link between two link ports carries AEL only and is declared to the host by the operator. **No maximum depth is defined by AEL.** A path is valid when the experiment's timing requirement is met by the sum of the declared per-hop timing envelopes along it, which the host checks per deployment; a product MAY publish a recommended or validated maximum depth for itself.

### 8.7 Timing contract

A router SHALL document, as measured values under representative load: forwarding latency from input SOF to output SOF (minimum, typical, maximum), forwarding jitter, fan-out skew (Section 8.2), and the load conditions under which the figures were taken. A router is never described as zero-delay or as load-independent; it is described by its envelope. No numeric limit is fixed by this Draft.

## 9. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | Carried in the Module Port: `AEL_IN_P`/`AEL_IN_N` and `AEL_OUT_P`/`AEL_OUT_N` with the port's `GND` as reference; connected only by the AURIORA Link Cable ([Module Port specification](./module-port.md)). | Two Modules exchange events in both directions over one Link Cable; a straight-through cable yields zero valid frames and no damage. |
| Electrical | Point-to-point differential pair; receiver-side termination (120 Ω reference); true fail-safe receiver; logical idle (mark) on open, unpowered, shorted, inserted and removed links; protection at the connector; no frame on power or reset transitions. | Idle and zero valid frames under each fault condition and during 100 insertion/removal cycles and 100 power/reset cycles at each end; transient test per the Hardware Design Guide. |
| Frame | 8N1 at 1 Mbit/s; exactly four bytes, big-endian `event_id` + CRC-16 (0x1021 / 0xFFFF / no reflection / no xorout); `0x0000` invalid; ≥ 2 character times idle between frames; contiguous characters within a frame; gap-based resynchronization. | The `check` value 0x29B1 reproduced; a corrupted frame, a three- or five-byte burst, a frame with `0x0000`, and a break each produce no action and one invalid count; two identical frames produce two events; resynchronization after injected corruption at the next qualifying gap. |
| Behavioral | Receive bindings with per-state enable; action only after a complete valid frame confirmed by its gap; unknown, unbound and disabled events ignored and recorded; source bindings emit at the real occurrence; no implicit IN→OUT forwarding; no retry ([AES-AEL-003](../05-interfaces-and-versioning.md#aes-ael-003-event-identifiers-and-module-event-bindings)). | Every state × bound identifier combination exercised; an unbound identifier and a disabled-in-state identifier are logged and cause no action; a bound identifier acts while `RUNNING` where so configured; the source frame's reference instant coincides with the internal event within the documented latency. |
| Timing | Reference instant = first start-bit edge after a qualifying gap; characterized source-to-frame, frame-to-action, forwarding latency, jitter and skew ([AES-AEL-004](../05-interfaces-and-versioning.md#aes-ael-004-deterministic-timing-and-observability)). | Latency and jitter measured over at least 100 events per figure under representative load; router skew measured across all outputs of one route. |
| Routing | Store-and-forward after validation; `(port, event_id)` routes; identifier unchanged; staged/validated/committed table with content identity; frozen while `ARMED`/`RUNNING`; deterministic queueing; counted overflow; acyclic Hub-to-Hub topology ([AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)). | Corrupt ingress frame yields zero egress frames; unrouted identifier counted, not forwarded; committed identity readable; commit attempt during an armed deployment refused; overload test reaches the documented capacity and reports overflow counts equal to frames lost. |
| Observability | Module and router counters and logs as required by `AES-AEL-004` and Section 8.5; configuration readable. | Counter reconciliation across sender, router and receivers after a run with a deliberately corrupted frame detects the loss at the point it occurred. |

## 10. Settled and Open Items

### 10.1 Settled in this Draft

Decided by [EDR-008](../edr/EDR-008-auriora-event-link.md) and its baseline review; an implementer may build against these:

- UART-class asynchronous NRZ character framing, 8N1; logical idle = mark (HIGH); start bit = space.
- True fail-safe receiver requirement expressed as resolution to logical idle; physical activity and framing errors are never events.
- Frame reference instant = start-bit edge of the first character after a qualifying gap; capture mechanism not prescribed.
- Fixed four-byte frame: 16-bit big-endian `event_id`, `0x0000` reserved, CRC-16 with the complete parameter set of Section 5.4 over the two identifier bytes.
- Idle-gap delimiting: ≥ 2 character times between frames, contiguous characters within a frame, deterministic gap-based resynchronization, whole-frame invalidation on any violation.
- 1 Mbit/s Draft baseline bit rate; faster classes only as a versioned extension.
- Store-and-forward routing after complete validation; invalid frames dropped and counted, never forwarded, never retried.
- Bounded, declared fan-out skew; fan-out skew and path latency kept as separate figures.
- Event identifiers unique per logical source within the active AEL routing domain, host-allocated per deployment.
- No fixed Platform maximum Hub depth; path validity from declared per-hop envelopes.
- No dedicated AOID class for AEL; AEL support and version are ordinary device capabilities.
- Two unidirectional pairs per link — AEL IN and AEL OUT — with one driver per pair; no half-duplex AEL.
- Carriage in the Module Port with the `AEL_IN_*`/`AEL_OUT_*` contact roles and net names; the AURIORA Link Cable crossover; receiver-side termination with 120 Ω as reference design assumption.

### 10.2 Open

Decided before this specification reaches `1.0`, from an explicit Platform decision or from bring-up measurement of the first AEL-capable Modules and a router:

- **Electrical profile:** the normative RS-485-compatible driver/receiver contract AEL follows, and with it driver output requirements, receiver threshold, common-mode range and termination assumptions.
- **Module Port position numbering**, Link Cable impedance and `MCL`-to-AEL crosstalk limits — decided in the [Module Port specification](./module-port.md) (its Section 8).
- **Cable and termination validation:** actual Link Cable impedance, termination behavior, maximum validated cable length at 1 Mbit/s, signal integrity, insertion/removal and false-frame immunity, EMC/ESD behavior where product validation requires it.
- **Timing envelopes:** real Module source-event-to-frame and frame-to-action latency and jitter; router input-SOF-to-output-SOF latency (min/typ/max), jitter and measured fan-out skew; event-rate saturation and queue behavior under worst-case load.
- **Router management contract:** the form in which the host reads a router's identity and capabilities — *what* it reads is fixed by [AES-HUB-004](../03-architecture.md#aes-hub-004-hub-identity-and-capability-discovery) — and stages, verifies, commits and reads back route tables; MCI reuse is the preferred candidate ([EDR-008](../edr/EDR-008-auriora-event-link.md)). Its transport is the host-facing interface ([AES-HUB-003](../03-architecture.md#aes-hub-003-host-facing-interface-and-traffic-separation)) or cascaded `MCL` ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)).
- **AEL-to-trigger adapter** as a product; **naming** (AOID) of an AEL router product and of a Module Hub — the identity content a Hub exposes is fixed by [AES-HUB-004](../03-architecture.md#aes-hub-004-hub-identity-and-capability-discovery).
- Separate architectural concerns, not AEL extensions: long-duration cross-Module clock alignment; bulk measurement-data transport; the experiment description language (`AEDL`, informative).

## 11. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.2 (Draft) | Physical layer re-based on the Module Port ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)): the standalone M8 3-position AEL IN / AEL OUT connectors are withdrawn; AEL IN and AEL OUT are carried as `AEL_IN_P`/`AEL_IN_N` and `AEL_OUT_P`/`AEL_OUT_N` in the M8 8-position Module Port, connected only by the AURIORA Link Cable, which crosses OUT to IN; direct operation is 1:1 and Hub-to-Hub links use the same port and cable. Electrical layer, frame, identifiers, timing reference and router unchanged; the open gender/keying item is closed by the withdrawal. | Not release-binding; not mechanically compatible with AEL `0.1` ports; frame unchanged |
| 0.1 (Draft) | Initial draft, superseding the SYNC `0.1` Draft ([EDR-008](../edr/EDR-008-auriora-event-link.md)): typed fixed four-byte event frame — 16-bit big-endian identifier plus fully parameterized CRC-16 — carried as 8N1 UART-class characters at a 1 Mbit/s baseline with idle-gap delimiting and gap-based resynchronization; logical idle = mark with a true fail-safe receiver requirement; start-of-frame reference instant; deployment-scoped, routing-domain-unique identifiers; store-and-forward AEL router with committed route tables, declared timing contract, deterministic queueing and counted overflow; acyclic Hub-to-Hub links with no fixed depth; M8 3-position pinout and receiver-side termination carried over from SYNC. Electrical profile, connector gender/keying, cable and termination validation, timing envelopes and the router management contract left open. | Not release-binding; not wire-compatible with SYNC `0.1` |
