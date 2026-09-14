# EDR-008: AURIORA Event Link

## Status

Accepted (2026-09-14)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module or Module Hub relies on this interface.*

**Supersedes** the Module Synchronization Interface decision of [EDR-006](./EDR-006-module-synchronization-interface.md) — items 1, 3 and 5 of its Decision — and the SYNC-related parts of [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) — the firmware-free SYNC event path, the static fan-out model and the SYNC terminology of the Module Hub and Module Port (items 5, 6 and 7 of its Decision, in the parts that concern SYNC). The MCI and `MCL` decisions of EDR-007 (items 1 to 4) remain in force unchanged. Both earlier records are preserved as history, as [AES-EDR-002](../08-decisions-and-governance.md#aes-edr-002-decision-record-structure-and-immutability) requires.

## Context

[EDR-006](./EDR-006-module-synchronization-interface.md) gave AES a Module-to-Module event interface: one differential link, one rising edge, one meaning — "an event occurred now" — with everything else in the receiver's configuration. [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) then placed that interface inside the Module Hub as a firmware-free fan-out with static, pre-ARM port grouping, and defended the absence of a processor in the event path as the property that kept the Hub's delay independent of its load.

Both records were written from the use case that was in view at the time: a few Modules, one deterministic instant per run — a stimulus Module starts a protocol on the edge, an acquisition Module inserts a marker. For that case the single edge is the right answer, and the records say why.

The full experiment model that AURIORA is actually built for arrived afterwards. A realistic bench holds a Plant Electrophysiology Module recording continuously, an acoustic stimulus Module, an ultrasound stimulus Module and a multi-wavelength photobiology Module, connected through one or more Module Hubs, running baseline → stimulus → recovery protocols, repeated and sham trials, long unattended runs and — the case that breaks the single edge — **closed-loop experiments**: the electrophysiology Module detects a condition during acquisition and stimulus Modules react to it, then report their own phase completions, which other Modules react to in turn. Worked through against the 1.x model, this exposes four things the single edge cannot do:

1. **One Module originates several distinct events.** A detector crossing, an acquisition start and a phase completion are different events with different consequences downstream. On a single-meaning line they are indistinguishable, and adding a physical line per event type multiplies connectors, cables and Hub ports by the number of event types.
2. **Receivers must select, not merely receive.** A stimulus Module wants the detector event and not the phase-completion event of its neighbour. A fan-out that regenerates every edge to every grouped port forces the selection into per-trial reconfiguration over MCI, which puts the host back in the timing path and cannot separate two events that arrive close together.
3. **Events must be accepted while `RUNNING`.** A continuously recording Module accepts markers while acquiring; a stimulus Module accepts a phase change during playback; a detecting Module emits while running. The ignore-while-running default of EDR-006 is safe for a trigger and wrong for a closed loop.
4. **Events cross Hubs.** An installation larger than one Hub's port count needs an event on one Hub to reach a Module on another, without waiting for the `MCL` cascading question that EDR-007 and the 1.6.1 patch deliberately left open.

Once an event carries a type, the Hub has to look at it to route it, and a Hub that looks at events has a processor in the event path. That is the property EDR-007 protected, and the reason this is a supersession rather than an amendment: the earlier decision was correct for its inputs, and its inputs have changed. Changing a Platform interface class is platform-wide and requires an EDR under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger).

## Alternatives Considered

### What the link carries

| Alternative | Assessment |
|---|---|
| **Keep the single edge; one physical line per event type** | Rejected. Connectors, cables and Hub ports scale with Modules × event types; a Hub would need a fan-out plane per type; a closed loop with several event types per Module becomes a wiring problem. It also does not solve selective reception. |
| **Keep the single edge; pre-arrange its meaning per trial over MCI** | Rejected. The meaning of an edge then depends on the host having reconfigured every receiver between two events, which places the host in the timing path and fails as soon as two events arrive closer together than an MCI round trip. Host-disconnected execution becomes impossible. |
| **Meaning in pulse width, count or spacing** | Rejected, as in EDR-006. A protocol without framing, with the failure modes of one. |
| **A general message protocol** — event type, source and destination addresses, timestamp, parameters | Rejected. It becomes a data bus, duplicates MCI, makes frames variable and long, and invites experiment logic onto the wire. Every field beyond the type answers a question the topology or the Module's own log already answers. |
| **A small fixed event frame: numeric event identifier plus integrity check, nothing else** | **Chosen.** The frame says *which* configured event occurred and *when* (its start-of-frame is the timestamp reference). Meaning stays in Module bindings and in the deployment record, exactly where EDR-006 put it; only the *selector* moves onto the wire. |

### Event identity

| Alternative | Assessment |
|---|---|
| **Platform-wide registered event numbers** ("0x0010 always means acquisition start") | Rejected. A registry has to anticipate every Module and every experiment, and two Modules of the same type in one bench still need to be told apart. |
| **Textual event names on the wire** | Rejected. Variable length, slow, and the name is documentation, not a routing key. |
| **Compact numeric identifiers, allocated per deployment by the host, unique within the routing domain, decoded through the deployment record** | **Chosen.** A 16-bit identifier is small enough to keep the frame short and large enough for any bench. Uniqueness within the active routing domain is what lets the frame omit a source address and cross Hubs unchanged; the mapping stored with the run is what lets the log be decoded years later. |

### The Hub

| Alternative | Assessment |
|---|---|
| **Retain the firmware-free fan-out** (EDR-007) | Rejected. It cannot route by identifier, so it either forwards every event to every grouped port — moving selection to the receivers and burdening every link with every event — or it does not support typed events at all. |
| **A Hub that understands experiment semantics** ("if spike then start audio") | Rejected. Experiment logic in infrastructure firmware has to be revised for every Module and every experiment, cannot be validated by the host before a run, and breaks [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope). |
| **An active router: `(ingress port, event ID) → set of output ports`, with a staged, validated and committed route table, no knowledge of meaning** | **Chosen.** The Hub knows numbers, ports and routes. Its timing becomes a contract — bounded, characterized forwarding latency, jitter and fan-out skew, deterministic queueing and explicit overflow — rather than a property of the circuit. This is what EDR-007 rejected, and it is accepted here because typed routing has no other home. |
| **Cut-through forwarding** (begin transmitting before the frame is validated) | Rejected. A corrupted frame propagates through every Hub, and its consequences appear at receivers rather than at the point of corruption. |
| **Store-and-forward after validation** | **Chosen.** One frame time of added latency per hop, in exchange for a fault model in which a corrupt frame is dropped and counted where it was received and never reaches a Module. For AURIORA experiments the added microseconds are far cheaper than uncertain propagation. |

### Framing and encoding of the baseline frame

| Alternative | Assessment |
|---|---|
| **A purpose-built line code** (Manchester, pulse-position or a custom bit-serial format) | Rejected for the baseline. Not receivable by an ordinary serial peripheral, so every device needs programmable logic or bit-level firmware in the event path; no interoperability gain over a character-framed frame for a four-byte payload. |
| **UART-class asynchronous NRZ, 8N1** | **Chosen.** Every intended controller receives and transmits it through a hardware serial peripheral with DMA; its idle state (mark, HIGH) coincides with the output of a true fail-safe differential receiver, which resolves the idle-polarity question by construction; a stuck-LOW line is a break — a framing error, never a frame. |
| **A start-of-frame byte** to delimit frames | Rejected. A qualifying idle gap delimits frames at no cost in bits, and with a fixed four-byte frame the receiver needs no further alignment aid. |
| **Idle-gap delimiting: ≥ 2 character times between frames, exactly four bytes between gaps, whole-frame invalidation on any violation** | **Chosen.** Resynchronization is bounded and deterministic. The price is accepted knowingly: a frame is confirmed only by the gap that follows it, so the earliest action is one frame plus one gap after the reference instant. |
| **Integrity check named by convention** ("CRC-16/CCITT") | Rejected. The name is ambiguous across implementations. |
| **CRC-16, poly 0x1021, init 0xFFFF, no reflection, no xorout, check 0x29B1, over the two identifier bytes** | **Chosen.** Non-zero init makes the all-zero line pattern invalid twice over (`event_id 0x0000` reserved and CRC 0x1D0F ≠ 0x0000). The result is normative; hardware acceleration is welcome where a controller offers a compatible unit and is not assumed of any platform — a two-byte software CRC is acceptable. |
| **Leave the bit rate open** | Rejected. The bit rate is the precondition of every cable measurement, not its result. |
| **1 Mbit/s Draft baseline** | **Chosen.** Available on every UART; 40 µs frame, ~60 µs minimum frame period, far above biological event rates; validated against cable and transceiver before `1.0`; faster classes only as a versioned extension. |

### Scaling beyond one Hub

| Alternative | Assessment |
|---|---|
| **Solve `MCL` Hub cascading first and carry events over it** | Rejected. It couples the event plane to an unspecified control binding and reintroduces the "SYNC as a message on `MCL`" pattern EDR-007 excluded. |
| **Network-style mechanisms** — hop counts, spanning tree, duplicate suppression, routing protocols | Rejected. Complexity without a driving requirement. |
| **Hub-to-Hub AEL links carrying the same frame, acyclic topology required, identifiers unchanged across hops** | **Chosen.** The event plane scales on its own contract; `MCL` cascading stays a separate open question; the routing-loop problem is excluded by construction rather than solved at run time. Experiment-level feedback loops remain legitimate and are a host validation concern, not a network one. |

### Third-party laboratory equipment

| Alternative | Assessment |
|---|---|
| **Retain SYNC as a second Platform interface** for instruments that consume a bare edge | Rejected. Two Platform-wide event interfaces with two behavioral models, two Hub functions and two sets of ports, for the benefit of instruments that an adapter serves. |
| **An AEL-to-trigger adapter or a product-specific auxiliary trigger output** | **Chosen.** The adapter is an accessory; the Platform contract stays singular. The loss is real and is recorded below. |

### Hub management

| Alternative | Assessment |
|---|---|
| **Extend MCI to cover the Hub now** | Deferred. MCI is a Module control contract with a Module lifecycle; stretching its meaning to infrastructure before its first binding exists is the "factor ahead of both" pattern EDR-007 avoided. |
| **A second, separately named management protocol** | Rejected for now. A new acronym and a full specification for a device that has no host-facing transport yet. |
| **A normative logical requirement — what a host must be able to do to a Hub — with the concrete contract left open, MCI reuse recorded as the preferred candidate** | **Chosen.** Identity, capabilities, staged → verified → committed route configuration and readable state are required; whether they are carried by MCI, an MCI-shared core or a dedicated binding is decided with the Hub's host-facing transport. |

### Fail-safe idle

| Alternative | Assessment |
|---|---|
| **Inherit the SYNC rule** — receiver output inactive (logic LOW) on open, unpowered or shorted input | Rejected. With framed signaling a fixed LOW is not automatically harmless: under a UART-class encoding a continuous LOW is a start bit or a break, so cable insertion could look like the beginning of a frame. |
| **A logical AEL idle state, to which the receiver resolves on every fault, and which the chosen line encoding is obliged to make indistinguishable from "no frame"** | **Chosen.** The requirement is stated at the level that matters — no fault condition and no physical activity ever yields a valid event — and the electrical polarity is decided with the encoding, not ahead of it. |

### Requirement identifiers and version

| Alternative | Assessment |
|---|---|
| **Reuse `AES-SYNC-001` to `AES-SYNC-004`** for the new semantics | Rejected. The identifiers would then mean different things in different AES versions. |
| **New `AES-AEL-*` identifiers; `AES-SYNC-*` retired in the Document Index** | **Chosen.** |
| **A minor AES version** — the SYNC specification was Draft | Rejected. The Draft was the physical layer; the normative model in Interfaces and Versioning §4 stated that SYNC carries no identifier and defined the Hub's behavior, and both change incompatibly. [AES-VER-001](../05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts) defines breaking by impact. |
| **AES `2.0.0`** | **Chosen.** The Platform's event interface should not begin its life by evading the Platform's own versioning rule. |

## Decision

1. The Module Synchronization Interface (SYNC) is superseded as the Platform's Module-to-Module event interface by the **AURIORA Event Link (AEL)**: a Module-level, point-to-point differential link carrying small, fixed-format, integrity-protected **typed deterministic events**. Its interface-independent rules are `AES-AEL-001` to `AES-AEL-005` in [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link); its physical, frame and routing specification is [`docs/interfaces/ael.md`](../interfaces/ael.md) (`0.1`, Draft).
2. An AEL event frame is **exactly four bytes**: a **16-bit big-endian event identifier** and a **16-bit CRC** (poly `0x1021`, init `0xFFFF`, no reflection, no xorout, check `0x29B1`) over the identifier — and nothing else: no source or destination address, no Module identity, no name, no payload, no timestamp, no sequence number, no priority. It is carried as **UART-class 8N1 characters at a 1 Mbit/s Draft baseline**, delimited by **at least two character times of idle** between frames and validated as a whole. Event identifiers are allocated by the host per deployment, are **unique within the active AEL routing domain**, and are decoded through the mapping stored in the deployment record. `0x0000` is reserved as invalid/unbound.
3. A Module holds **AEL receive bindings** (event identifier → configured action, with the states in which it is enabled) and **AEL event source bindings** (internal event → event identifier). The **`ARMED` boundary is retained**; the global ignore-while-running default is not. Whether an event acts is decided by identifier, current state and binding; every non-acting event is observable.
4. The **direct Module-to-Module link is a first-class case**: the same frame travels Module → Module, Module → Hub → Module and Module → Hub → Hub → Module, and a Module cannot tell whether a Hub is on the path.
5. The Module Hub's event role becomes an **active AEL router**: store-and-forward after validation, routing by `(ingress port, event identifier)` to a set of outputs, from a route table that is staged, validated, committed and not modified while an affected deployment is `ARMED` or `RUNNING`. The Hub does not know what an identifier means. Its forwarding latency, jitter, fan-out skew, queue depth, arbitration and overflow behavior are a documented, characterized timing contract. Corrupt frames are dropped and counted, never forwarded, never retried.
6. Hubs scale through **Hub-to-Hub AEL links** carrying the same frame with the identifier unchanged; the baseline topology is **acyclic**. No hop count, routing protocol or duplicate suppression is introduced. `MCL` cascading remains a separate open question.
7. A Module Hub SHALL be manageable by the host to the extent of identity, capabilities and limits, staged and integrity-checked route configuration with commit/activation, readback of the active configuration's identity, and port, queue, error and counter state. The concrete host-facing contract is **open**; reuse of MCI is the preferred candidate. The Hub is not thereby a Module.
8. The electrical layer keeps EDR-006's settled choices where they were settled: point-to-point differential signaling with one driver per pair, receiver-side termination (120 Ω as a reference design assumption), protection at the connector, no back-drive, and M8 3-position A-coded connectors for the standalone **AEL IN** and **AEL OUT** ports. The fail-safe rule is restated as a **logical AEL idle** — mark (HIGH) under the baseline encoding — with a **true fail-safe receiver** requirement: open, disconnected, unpowered-transmitter, shorted and inserted/removed links resolve to idle and never yield a valid event; the **frame reference instant** is the start-bit edge of the first character after a qualifying gap, and how it is captured is not prescribed. The **normative electrical profile stays open**: the intended direction is an RS-485-compatible driver/receiver contract used point-to-point, and the driver, receiver-threshold, common-mode and termination figures are quoted only once that profile is explicitly chosen — RS-422 and RS-485 are not treated as interchangeable. **Connector gender and keying stay open** and are decided against the full AURIORA connector inventory, not for AEL in isolation.
9. The Module Port carries `MCL` together with **AEL IN and AEL OUT** as electrically independent links; everything physical about it remains open as recorded in EDR-007. Standalone AEL ports are retained.
10. Third-party trigger interoperability is provided by an **AEL-to-trigger adapter** or a product-specific auxiliary output, not by a second Platform-wide interface.
11. `AES-SYNC-001` to `AES-SYNC-004` and the document identifier `AES-EXAMPLE-SYNC` are retired; `docs/interfaces/sync.md` becomes a superseded notice pointing to the last AES release that carried the full SYNC specification (`v1.6.1`). AES is released as **`2.0.0`**.

## Rationale

The decision keeps everything EDR-006 got right and changes the one thing it got wrong for the experiments that followed. Meaning is still not on the wire — an identifier is a key into a table that lives in Module configuration and in the deployment record, and a frame observed without that table says only "event 0x0201 at this instant". The link is still narrow: it is not a data bus, not a control path, not a clock, and its frame has no room to become any of those by accident. Arming is still the boundary between preparation and deterministic execution. What changes is that the receiver can now tell one event from another, and so can a Hub, which is what a closed loop between several Modules needs.

The Hub takes on a processor in its event path because there is no other place for routing to happen, and the argument of EDR-007 — that a Hub with firmware has a load-dependent delay — is answered not by denying it but by making the delay a contract: bounded, measured, published, with deterministic queueing and an overflow that is a counted fault rather than a silent loss. A Hub that meets that contract is characterizable in the way a firmware-free one was measurable; the experiment records the numbers either way. Store-and-forward is chosen for the same reason: a corrupt frame that stops at the first Hub is a fault with a location, and one frame time per hop is a price AURIORA experiments can pay.

Identifier uniqueness within the routing domain is what allows the frame to stay small across several Hubs: the topology already knows where a frame came from and where it goes, and a second Hub that cannot distinguish two upstream sources does not need to, because their identifiers already differ. Host allocation, rather than a Platform registry, keeps the Platform out of experiment semantics and lets two isolated benches reuse the same numbers.

Keeping AES lean is a deliberate part of the decision. Experiment compilation, route generation, feedback-loop analysis, provenance detail and host-disconnect workflows are real and are placed in the Software Style Guide and an informative worked example. AES states the interface invariants and nothing that belongs to a host application.

## Consequences

- AES gains `AES-AEL-001` to `AES-AEL-005`, a rewritten [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link), a rewritten [Architecture §7](../03-architecture.md#7-module-hub) and §7.1, AEL supporting terms replacing the SYNC ones, a new Draft interface specification [`docs/interfaces/ael.md`](../interfaces/ael.md), a new informative [multimodal worked example](../../examples/worked-example-multimodal-ael-experiment.md), and this record. `AES-MCI-003` and `AES-MCI-004` are updated to refer to AEL and to the AEL properties a host must discover. Frozen core vocabulary is unchanged.
- **`AES-SYNC-001` to `AES-SYNC-004` are retired**, not renumbered, and listed in the [Document Index](../document-index.md). Historical releases, changelog entries and EDR-006/007 keep the SYNC wording.
- **This is an incompatible normative change: AES `2.0.0`.** No Released Module or Hub exists, so nothing deployed breaks; the number records the change of model honestly.
- **A deliberately accepted loss.** EDR-006 chose a bare edge partly so that an oscilloscope or a DAQ could consume it directly. A typed frame cannot be consumed that way. Interoperability with such equipment moves to an AEL-to-trigger adapter or a product-specific auxiliary output. The more distinguishable deterministic events of real multimodal and closed-loop experiments were judged the more important Platform requirement.
- **Gap-confirmed frames have a floor on action latency.** Because a frame is confirmed only by the idle gap that follows it, the earliest a receiver may act is one frame plus one gap after the reference instant — about 60 µs at 1 Mbit/s — and each routing hop adds at least the same again plus the router's forwarding latency. Timing statements and host validation reason from this floor; it is the accepted price of deterministic resynchronization without a start-of-frame byte.
- **A Module Hub now contains firmware in the event path.** Its timing is a contract that must be measured under load and published; a Hub without a published timing envelope does not conform. The Hardware Design Guide's controller-less Hub guidance is replaced.
- The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §5.1, the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) §14.2 and the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3.5 are rewritten for AEL; the software guide gains experiment-deployment guidance (event-identifier allocation, route generation, topology and capacity validation, feedback-loop analysis, provenance, reconnection). The private engineering knowledge base is re-derived afterwards.
- The Audio Module's reserved single-ended `SYNC_IN`/`SYNC_OUT` GPIOs remain non-conformant, now to AEL; the alignment expected of the next hardware revision is to framed AEL signaling on differential M8 ports, which is a firmware-visible change (a hardware serial peripheral rather than a captured edge).
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Architecturally settled by this record:** typed fixed four-byte frames carried as 8N1 UART-class characters at a 1 Mbit/s Draft baseline, with the CRC-16 parameter set, idle-gap delimiting (≥ 2 character times) and gap-based resynchronization; 16-bit host-allocated identifiers unique per routing domain, `0x0000` reserved; logical idle = mark with a true fail-safe receiver requirement; frame reference instant at the first start-bit edge after a qualifying gap; receive and source bindings with state-aware policy; direct and routed operation with one frame; store-and-forward active Hub routing after complete validation, with a committed route table and a declared timing contract including fan-out skew; acyclic Hub-to-Hub links with no fixed depth; point-to-point differential electrical layer and M8 3-position standalone ports with 120 Ω reference termination; no dedicated AOID class; no host in the event timing path.

**Open — explicit Platform decisions still to take:**

- The normative **electrical profile**: which RS-485-compatible driver/receiver contract AEL follows, and with it driver output requirements, receiver threshold, common-mode range and termination assumptions.
- **Connector gender, keying and marking** for AEL IN / AEL OUT, decided against the full AURIORA connector inventory (AEL IN, AEL OUT, Module Port, electrode and sensor connectors, every other existing or planned M8 interface) with the cross-mating analysis.
- The Hub's **host-facing management contract** (MCI reuse preferred) and its transport.

**Open — measurement-dependent, from the first AEL-capable Modules and a router:**

- Validated cable length at 1 Mbit/s; actual cable impedance and termination behavior; signal integrity; insertion/removal characterization and false-frame immunity; EMC/ESD behavior where product validation requires it.
- Module source-event-to-frame and frame-to-action latency and jitter; router input-SOF-to-output-SOF latency (min/typ/max), jitter and measured fan-out skew; event-rate saturation and queue behavior under worst-case load.

**Separate architectural or product concerns, not closed here:** the AEL-to-trigger adapter as a product; Module Hub Product Family identifier and naming; long-duration cross-Module clock alignment and absolute time (the PPS-class need of EDR-005 also remains open); bulk measurement-data transport — explicitly not AEL; the experiment description language (informative working name `AEDL`) — no grammar, syntax or file format is standardized.

## Affected Requirements / Documents

- [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link) — rewritten; `AES-AEL-001` to `AES-AEL-005` (new); `AES-SYNC-001` to `AES-SYNC-004` (retired). §3.1 and §5 (`AES-MCI-003`, `AES-MCI-004`, §5.2) updated to AEL.
- [`docs/interfaces/ael.md`](../interfaces/ael.md) — new specification; [`docs/interfaces/sync.md`](../interfaces/sync.md) — superseded notice.
- [Architecture §3 and §7](../03-architecture.md#7-module-hub) — Module Design note, Module Hub and Module Port rewritten; `AES-HUB-001` and `AES-HUB-002` updated for AEL routing.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — SYNC supporting terms replaced by AEL terms; Module Port, Module Hub and Module Lifecycle State updated.
- [Worked Example: Multimodal AEL Experiment](../../examples/worked-example-multimodal-ael-experiment.md) — new, informative; the SYNC worked example is withdrawn.
- [Document Index](../document-index.md), `STANDARD.md`, [`docs/interfaces/README.md`](../interfaces/README.md) — indexing and retirement.

## Future Review Criteria

Revisit if: a use case needs a payload, an address or a timestamp inside the event frame (the presumption is that the answer lies in bindings, topology or the deployment record, not in the frame); a Hub timing contract proves unachievable with store-and-forward for a real experiment class; the acyclic baseline is outgrown by an installation that genuinely needs redundant paths; the Hub management contract is decided, which may close item 7; or the M8 cross-mating analysis shows that a different connector form is the only safe mitigation.
