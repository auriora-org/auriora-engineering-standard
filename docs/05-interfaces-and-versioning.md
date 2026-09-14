# 05 Interfaces and Versioning

**Document ID:** AES-IF
**Status:** Normative
**Depends On:** [Architecture](./03-architecture.md), [Naming and Identity](./04-naming-and-identity.md)
**Supersedes:** AES-VER (Versioning Standard), AES-EVO (Platform Evolution Strategy)

## 1. Purpose

This chapter defines Host Interface and Unit Interface rules, the AURIORA Event Link, the Module Control Interface, versioning and compatibility evolution.

Interfaces are versioned contracts, not merely connectors, buses or firmware functions. This is where AES stays strict even for a small team, because interfaces are exactly the places where today's shortcut becomes next year's incompatibility.

## 2. Version Axes

| Axis | Applies to | Format |
|---|---|---|
| Engineering version | Documents, firmware, software, APIs | `MAJOR.MINOR.PATCH` (semantic) |
| Hardware revision | PCB / mechanical design | `Rev <LETTER>` |
| Interface revision | Host and Unit Interfaces | `MAJOR.MINOR` |
| Calibration schema | Calibration data | `CAL-MAJOR.MINOR` |
| Manufacturing package | Released production bundle | `PKG-MAJOR.MINOR.PATCH` |

### AES-VER-001: Semantic Versioning for Released Contracts

**Requirement:** Released contracts — firmware APIs, Host and Unit Interface contracts, EEPROM schemas, file formats and normative documents — SHALL use semantic versioning: `MAJOR` for incompatible change, `MINOR` for backward-compatible addition, `PATCH` for clarification or defect correction. A Released hardware revision SHALL declare which interface versions and calibration schemas it supports. Before Release, versions are informal (`0.x`, dates, whatever helps).

**Rationale:** Consumers need to know whether an update is safe automatically, with review, or only with migration.

**Breaking change** means: existing compliant consumers must change to keep working — removed or changed required behavior, changed physical/electrical compatibility, changed command semantics, changed metadata interpretation, invalidated calibration data or changed safety behavior. Breaking is defined by impact, not by diff size.

## 3. Interface Contracts

A declared interface contract specifies, where applicable: name and AOID, version, physical layer, electrical limits, communication protocol, timing, discovery and identity behavior, error model, compatibility rules and test method. Use the [interface contract template](../examples/templates/interface-contract-template.md).

Maturity scaling: an Experimental connection between two of your own boards needs a pinout table in the README — nothing more. The contract obligation attaches when the interface is *declared* as a Platform interface or when either side is Released.

### AES-IF-006: Unit Interface Completeness

**Requirement:** A Released Unit Interface SHALL specify physical connector, pinout, voltage/current limits, signal direction, communication protocol, identity method, hot-plug policy, mechanical envelope constraints and compatibility checks.

**Rationale:** Replaceable hardware fails when engineers treat pinout as the entire interface.

### 3.1 Unit Interface Signals and Profiles

`UIF` denotes the **AURIORA Unit Interface**. Externally visible signals belonging to a standardized Unit Interface use the `UIF_` prefix. Standard signal names, where applicable, are:

- `UIF_PWR_VIN` — Unit input power supplied by the host
- `UIF_PWR_EN` — host-asserted enable for the Unit's functional power domain
- `UIF_READY` — Unit-functional-ready indication (see below)
- `UIF_I2C_SCL`, `UIF_I2C_SDA` — discovery/identity I²C bus
- `UIF_SPI_SCK`, `UIF_SPI_MOSI`, `UIF_SPI_MISO`, `UIF_SPI_CS_N` — SPI transport, where a profile uses one
- `UIF_IRQ_N` — generic asynchronous event notification from the Unit to the host
- `UIF_RESET_N` — host-controlled Unit reset, where a profile defines one
- profile-defined synchronization or auxiliary signals — Unit-to-host signals within one Module; the Module-to-Module AURIORA Event Link of Section 4 is not a `UIF_` signal

Physical presence is determined through successful EEPROM discovery, not through a dedicated presence pin. A Unit-presence signal (`UIF_PRESENT`, `UIF_PRESENT_N` or equivalent) SHALL NOT be defined; the connector SHALL NOT require separate discovery and functional power pins — the Unit locally switches or enables the power of its functional circuitry from `UIF_PWR_EN`.

`UIF_READY` is an **active-HIGH** functional-readiness signal:

- **LOW:** the Unit is disabled, starting, not initialized, faulty, or otherwise unavailable.
- **HIGH:** the Unit is powered, initialized, and its functional interface is ready for use.

For a Passive Unit, `UIF_READY` MAY be generated from the switched functional power domain (hardware pull-up or equivalent). For a Managed Unit, `UIF_READY` SHOULD be controlled by the Unit controller and asserted only after successful firmware initialization, and deasserted before shutdown or on entering an unrecoverable fault. The host MUST provide a defined LOW state when no Unit is connected or the Unit functional domain is disabled. `UIF_READY` is a readiness signal, not a physical-presence signal.

Where AES states a Unit Interface obligation on "the Module" — discovery, validation, activation, `UIF_PWR_EN` and `UIF_READY` handling — the obligation binds whatever implements the host side of the port, whether that is a Module, an adapter, a test fixture or a third-party host (*Unit Interface Host*, [Terminology §3](./02-terminology.md#3-supporting-terms)). This is what makes a Unit reusable outside the Module it was designed with. Product-level safety policy stays with the Module ([AES-MOD-004](./03-architecture.md#aes-mod-004-safety-policy-ownership)); it is not transferred by implementing a port.

A Unit Interface is realized through one or more versioned **Unit Interface Profiles**. Rather than forcing every Unit onto one universal connector, the Platform supports multiple profiles, each versioned independently. Concrete connector pinouts, electrical limits and timing live in the versioned profile specifications under [`docs/interfaces/`](./interfaces/); this chapter defines only the profile-independent rules.

Profile identifiers follow the pattern `UIF-[M]<transport>-<positions>`: an optional `M` marking a Managed-Unit profile, the transport, and the connector position count — for example `UIF-I2C-6` and `UIF-MI2C-8`. The position count is part of the identifier because it is the discriminator that prevents cross-profile mating.

### AES-IF-008: Versioned Unit Interface Profiles

**Requirement:** A standardized Unit Interface SHALL be defined as one or more named, independently versioned Unit Interface Profiles, each specifying its connector, pinout, `UIF_` signal set, electrical limits and timing in a versioned profile specification. A Released Unit and its host SHALL declare the profile identifier and profile version they implement (see [EEPROM Metadata](./06-eeprom-metadata.md)), and a host SHALL reject a Unit whose profile or profile version it does not support, leaving `UIF_PWR_EN` LOW. Profiles version per the semantic rules of this chapter; changing a profile's defined signals is a breaking change unless it resolves a documented electrical conflict without altering existing signal meaning.

**Rationale:** Different Unit classes have genuinely different connector needs; one universal connector either over-provisions simple Units or under-serves complex ones. Independent versioning lets each profile evolve without forcing a Platform-wide connector change, while explicit profile declaration keeps incompatible Units from being powered.

### 3.2 Profile Family and Selection

Two independent axes describe a Unit Interface. Conflating them over-provisions simple Units and under-serves demanding ones.

- **Management model** — Passive or Managed ([Architecture §5.1](./03-architecture.md#51-execution-models-and-transport)). It determines the *host contract*: whether the host drives the Unit's peripherals directly or operates the Unit through a versioned Unit API. It does not determine the transport.
- **Transport** — the bus carrying functional traffic. It is selected by throughput, latency, timing determinism and streaming behavior, not by whether a controller sits behind the interface.

The current profile family:

|  | Low bandwidth | High bandwidth |
|---|---|---|
| **Passive / simple Unit** | [`UIF-I2C-6`](./interfaces/uif-i2c-6.md) — 6 positions | Normally not applicable: a Unit needing high-bandwidth host-driven register access is usually better designed as a Managed Unit. |
| **Managed Unit** | [`UIF-MI2C-8`](./interfaces/uif-mi2c-8.md) — 8 positions, generic `UIF_IRQ_N` | [`UIF-MSPI-14`](./interfaces/uif-mspi-14.md) — 14 positions, SPI transport, `UIF_RESET_N` |

A Managed Unit is therefore not required to use SPI. Discovery, `UIF_READY` semantics, the activation sequence and event semantics are identical across all profiles, so a Unit API and its host software port between transports.

### AES-IF-009: Unit Interface I2C Address Allocation

**Requirement:** Every UIF profile carries the discovery I²C bus, so I²C addresses on it are allocated Platform-wide. The address block `0x50`–`0x57` (7-bit) SHALL be reserved for Unit discovery EEPROMs, with `0x50` as the default. A Unit's functional target address — the address at which a Managed Unit serves its Unit API, or at which a Passive Unit's functional devices respond — SHALL lie outside that block and outside the addresses reserved by the I²C specification (`0x00`–`0x07` and `0x78`–`0x7F`). A Managed Unit SHALL declare its Unit API address in EEPROM metadata ([AES-EEPROM-008](./06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)); a host SHALL NOT infer, default to or hard-code it. A Unit SHALL NOT acknowledge any address other than its discovery EEPROM address and its declared functional address or addresses. A host that shares one Unit Interface I²C bus across multiple Unit ports SHALL provide a means of resolving address collisions — a per-port bus, a bus switch or an addressable segment — and SHALL leave `UIF_PWR_EN` LOW for any Unit whose declared functional address collides with an already-active device.

**Rationale:** Once a Managed Unit's controller shares the discovery bus with its EEPROM, address allocation stops being a local implementation choice. Fixing the discovery block and requiring the functional address to be declared rather than assumed keeps discovery uniform across profiles and makes a collision a pre-power validation failure instead of a field fault that appears when the second Unit type ships.

### AES-IF-010: Unit Interface Profile Selection

**Requirement:** A Unit SHALL declare one Unit Interface Profile, selected by its management model and its transport requirements. A Managed Unit SHOULD use `UIF-MI2C-8` by default. A Managed Unit SHOULD use `UIF-MSPI-14` where throughput, latency, deterministic transfer timing or continuous data streaming makes an I²C transport unsuitable. A Passive or simple Unit SHOULD use `UIF-I2C-6`. Where the choice is not obvious from the criteria below, the Unit's design notes SHALL record which criterion decided it. A Unit SHALL NOT add Unit-specific signals to a profile; a genuinely unmet interface need is a versioned profile change ([AES-IF-008](#aes-if-008-versioned-unit-interface-profiles)), not a local pin.

**Rationale:** Without a stated default, the largest profile becomes the safe-looking choice and simple Units inherit connector, power and board-area cost they never use. A default plus explicit escalation criteria makes the larger profile a reasoned decision.

The criteria, in decreasing order of how often they decide the answer. None of them is a fixed byte-rate threshold: throughput alone rarely decides, and an arbitrary number would be wrong for most Units in both directions.

| Criterion | Points to `UIF-MI2C-8` | Points to `UIF-MSPI-14` |
|---|---|---|
| Deterministic transfer timing | Transfers may be delayed by bus arbitration, clock stretching or host scheduling. | A transfer must complete within a bounded, repeatable time. |
| Continuous streaming | Discrete request/response transactions. | Sustained or block-continuous data flow, or DMA-paced transfer. |
| Latency | Response needed in milliseconds or slower. | Sub-millisecond response required. |
| Payload size and update rate | Bytes to a few hundred bytes, at hertz or slower. | Kilobytes per transfer, or high repetition rate. |
| Event frequency | Occasional events, or none — a single generic `UIF_IRQ_N`, or polling, suffices. | Frequent events whose servicing must not contend with the data path. |
| Host transaction count | Few transactions per measurement or command. | Many transactions per unit of work, so per-transaction overhead dominates. |
| Power | Low average power matters; the Unit is idle or asleep most of the time. | Power is secondary to throughput. |
| Connector and cabling | Small PCB, few conductors, simple field cabling. | Board area and cable count are acceptable costs. |
| Host-controlled reset independent of power | Not required; `UIF_PWR_EN` cycling is sufficient recovery. | Required — the controller must be reset while remaining powered. |

Where the criteria conflict, determinism and streaming outrank payload size: a Unit moving very little data under a hard timing constraint belongs on `UIF-MSPI-14`, and a Unit moving more data with no deadline usually does not.

### AES-IF-007: Safe Default State

**Requirement:** Unit Interfaces SHALL define safe default states for power, outputs and communication lines before Unit identity and compatibility are validated. This applies at every maturity level where the interface can energize anything.

**Rationale:** Unknown Units must not be energized or commanded unsafely. This is a safety rule.

### AES-IF-002: Host Interface Determinism

**Requirement:** A Released Host Interface SHALL define command syntax, response syntax, status codes and error behavior in structured, machine-parseable form, and SHOULD provide capability discovery (Module identity, firmware version, supported interface versions). Free-form text that scripts parse by substring is not an interface.

**Rationale:** Automation, testing and reproducible operation need deterministic contracts. Capability discovery and a stable error model are the two SHOULD-level pieces most worth building in early.

### AES-IF-005: Backward Compatibility Within a Major Version

**Requirement:** A Released interface minor version SHALL remain backward compatible with earlier minor versions of the same major version. Incompatible changes SHALL increment the major version.

**Rationale:** Tooling and installed hardware must know when automatic compatibility is safe.

## 4. AURIORA Event Link

The **AURIORA Event Link (AEL)** carries deterministic **typed events** between Modules. An AEL event frame carries a numeric event identifier and an integrity check, and nothing else: no command, no parameter, no address, no payload, no timestamp. The identifier selects which configured event occurred; the receiving Module determines the action from its local bindings and current state, and the deployment record determines what the identifier meant to the experiment.

The dividing line in one sentence: **MCI prepares and observes state; AEL carries the deterministic events of the experiment.** Its complement on the output side: **an AEL OUT frame reports *which* configured internal Module event occurred and *when*; the meaning of the identifier lives in the Module bindings and the deployment record, not on the wire.**

AEL is a **Module-level** interface. It connects Modules to Modules, directly or through an AEL router in a Module Hub. It is not part of the Unit Interface: Units are internal building blocks of a Module and neither expose nor receive AEL. The profile-defined synchronization signals a Unit Interface Profile may carry (§3.1) are Unit-to-host signals inside one Module and are unrelated to AEL. AEL does not replace, extend or forward to any `UIF_` signal.

AEL is deliberately narrow. It is not a data bus, not a measurement or telemetry channel, not a firmware-update transport, not a command channel and not a message protocol with addresses or payloads; it is a small deterministic event frame. Its physical layer is point-to-point differential signaling carrying a four-byte frame as UART-class characters, but AEL is not a serial communication protocol: it has no addresses, commands, payload, acknowledgment or flow control. The physical, electrical, frame and routing specification is the versioned [AEL interface specification](./interfaces/ael.md); this section defines the interface-independent rules.

### 4.1 Topology

The normal AEL link is one **AEL OUT** driving one **AEL IN**: a point-to-point differential link. Two Modules need nothing else:

```text
Module A AEL OUT ──────────────► Module B AEL IN
```

Where events must reach several Modules, or several Modules' events must reach one, an **AEL router** — the event-routing function of a [Module Hub](./03-architecture.md#7-module-hub) — receives frames on its input ports and forwards each, by identifier, onto the selected outputs, each a separate point-to-point link:

```text
Module A AEL OUT ─► ┌──────────────┐ ─► Module B AEL IN     (0x0201 → B, C)
                    │  AEL router  │ ─► Module C AEL IN
Module B AEL OUT ─► │ (port, id) → │ ─► Module A AEL IN     (0x0301 → A)
                    │  output set  │
                    └──────────────┘ ─► Hub-to-Hub AEL link ─► another router
```

The router knows ports, identifiers and routes; it does not know what an identifier means. It forwards a frame only after receiving and validating it completely, adds a bounded, characterized delay, and preserves the identifier. Routers connect to one another through Hub-to-Hub AEL links carrying the same frame; the resulting topology is acyclic. The frame is identical on every path, and a Module cannot tell whether a router lies between it and its peer.

### AES-AEL-001: AEL Is the Module-Level Typed Event Interface

**Requirement:** A Module that exchanges deterministic events with other Modules SHALL do so through the AURIORA Event Link as specified in [`docs/interfaces/ael.md`](./interfaces/ael.md). An AEL event frame SHALL carry a numeric event identifier and an integrity check, plus only the framing the encoding requires; it SHALL NOT carry a command, a parameter, a payload, a source or destination address, a Module identity, a textual name, a timestamp or a priority. The meaning of an identifier SHALL be defined by the Modules' bindings and by the deployment record, never by the frame, and SHALL NOT be assigned to frame timing, pulse width, spacing or repetition. AEL SHALL NOT be used as a data, measurement, telemetry, logging, firmware-update or command transport; a Module that needs to convey commands, parameters or data SHALL use MCI or another declared control or data interface. AEL SHALL NOT be part of any Unit Interface Profile, and a Unit SHALL NOT expose or consume AEL.

**Rationale:** A frame that carries only a key into a table has one property a message protocol never has: it cannot grow. Every field beyond the identifier — an address, a parameter, a timestamp — answers a question that topology, bindings or the deployment record already answer, and each one makes the frame longer, the latency larger and the temptation to put experiment logic on the wire stronger. Keeping AEL out of the Unit Interface keeps the Module the single owner of its external event behavior ([AES-MOD-004](./03-architecture.md#aes-mod-004-safety-policy-ownership)).

### AES-AEL-002: Point-to-Point Links, Direct and Routed Operation

**Requirement:** An AEL link SHALL connect exactly one AEL OUT to exactly one AEL IN over a differential pair; the receiving end SHALL terminate the link and an output SHALL NOT be terminated as a receiver. Passive multidrop wiring, passive splitters and daisy-chaining through a Module SHALL NOT be the means of reaching several receivers. The AEL event frame SHALL be identical whether it travels directly between two Modules, through one AEL router, or through several routers over Hub-to-Hub AEL links; a Module SHALL NOT require knowledge of whether a router is on the path, and a Module Hub SHALL NOT be a prerequisite for two Modules to exchange AEL events. A receiver SHALL resolve to the AEL idle state, and SHALL NOT deliver a valid event, when its input is open, connected to an unpowered or resetting far end, shorted, or being inserted or removed; a device SHALL NOT emit a valid frame as a consequence of power-up, power-down, reset or cable insertion or removal. Physical line activity or a framing or integrity error SHALL never constitute an event.

**Rationale:** A point-to-point link has one driver, one receiver and one termination, so its timing is predictable and a fault on one link cannot disturb another. One frame for every path is what keeps a Module independently usable and serviceable: the smallest bench — two Modules and a cable — and the largest installation run the same firmware against the same contract, and a Hub is infrastructure the experiment can grow into, not a dependency it starts with. The fail-safe rules exist because an event interface whose receivers can be triggered by plugging in a cable is an interface that starts experiments by itself.

### AES-AEL-003: Event Identifiers and Module Event Bindings

**Requirement:** An AEL event identifier SHALL be a 16-bit unsigned value; `0x0000` SHALL be reserved as invalid/unbound and SHALL NOT be transmitted as an event. Identifiers SHALL be allocated by the host per deployment and SHALL be unique per logical event source within the active AEL routing domain — the set of endpoints interconnected by active AEL links and routes during one deployment; the mapping between experiment event names and identifiers SHALL be stored in the deployment record. A Module with an AEL IN SHALL hold configurable **AEL receive bindings**, each mapping an identifier to a configured action and to the Module Lifecycle States in which the binding is enabled; no receive binding SHALL be enabled before the Module is `ARMED`. A Module SHALL execute a bound action only on receipt of a complete, integrity-valid frame whose identifier is bound and whose binding is enabled in the Module's current state; a frame that is invalid, carries an unknown or unbound identifier, or arrives in a state where its binding is not enabled SHALL cause no action and SHALL be recorded. `RUNNING` SHALL NOT by itself disable AEL reception: whether a Module accepts an event while running is decided per binding, and any restart, stop, queue, advance or phase-change behavior SHALL be an explicitly configured action, never an implicit consequence of receiving an event. A Module with an AEL OUT SHALL hold configurable **AEL event source bindings**, each mapping a defined internal event — the actual occurrence, not the receipt of a control operation — to an identifier; a Module SHALL NOT forward a received event to its output unless that forwarding is itself a configured source binding. A configurable, deterministic delay between the frame reference instant and the action MAY be provided; the delay is Module configuration, not frame content. The actions and internal events a Module supports are Module-specific and are documented with the Module; this requirement defines the mechanism, not the list. Active bindings SHALL be readable through MCI or the Module's Host Interface.

**Rationale:** Bindings are the table that gives an identifier its meaning, and holding them on the Module — validated, readable, logged — is what makes an event reproducible and an ignored one a recorded fact. The `ARMED` boundary stays because it is the last moment at which a missing prerequisite or an invalid binding can still be noticed before deterministic execution begins. Ignoring everything while `RUNNING` was the right default for a trigger and is the wrong rule for a closed loop: a recording Module must accept markers while it records, a stimulus Module must accept a phase change while it plays, and a detecting Module must be able to emit while it acquires. Making that a per-binding decision keeps stray events harmless without making useful ones impossible. Emitting at the real occurrence, rather than on command receipt, is what makes the output frame a usable timestamp of what physically happened.

### AES-AEL-004: Deterministic Timing and Observability

**Requirement:** A Module or router SHALL timestamp a received frame at the frame reference instant defined by the AEL specification, in hardware or as close to hardware as its design allows, in local time and — where the Module has an acquisition clock — as a sample or frame index. A Module SHALL characterize and document its source-event-to-frame latency, its frame-to-action latency and the jitter of each; a router SHALL characterize and document its forwarding latency, jitter and fan-out skew under representative load. AES does not fix these figures; a device SHALL declare them and SHALL NOT be described as zero-delay or load-independent. AEL frames SHALL NOT be acknowledged or retransmitted; an invalid frame SHALL be dropped, counted and reported where it was received. A Module with firmware and a Host Interface that provides AEL SHALL record in its event log at minimum every received frame with its identifier and whether it acted or was ignored and why, every transmitted frame with its identifier, and every invalid frame, each with local timestamp and sample index where applicable, the Module state at the time, the related run or Session identifier where one exists, and local per-direction counters. Counters are local to the device and SHALL NOT be presented as synchronized between devices. The active receive and source bindings, delays and per-state enables SHALL be readable through MCI or the Host Interface. During Experimental work a reduced log is acceptable; a Released Module SHALL provide the full set.

**Rationale:** Retransmission would repair the wire at the cost of the one thing the event is for: a retried frame arrives at a different instant and is a different event. Loss is therefore made visible rather than hidden — the sender's log says which event produced each frame, the receiver's says what it did with it, and the counters in between say where a frame went missing. Timing is declared rather than assumed because a Platform-wide latency number would be either unrealistically tight for a routed multi-Hub path or uselessly loose for a direct link; the host validates each deployment against the envelopes the devices actually publish.

### AES-AEL-005: Active Hub Routing and Bounded Overload Behavior

**Requirement:** A device that routes AEL events — the AEL router function of a Module Hub, or a standalone AEL Hub — SHALL receive each frame completely and validate its framing and integrity before forwarding anything, and SHALL NOT forward an invalid frame. It SHALL forward a valid frame according to a route table keyed by ingress port and event identifier to a set of outputs, with the identifier unchanged; it SHALL NOT interpret, alter, merge, suppress, re-prioritize or retry frames and SHALL NOT contain experiment logic. All outputs selected by one routing decision SHALL begin transmission within a characterized maximum channel-to-channel skew. The router SHALL define and document its queue capacity, its deterministic arbitration and ordering rule, its behavior when an output is busy, its maximum supported event rate and its overflow behavior; an overflow SHALL be counted and reported and SHALL NOT be a silent loss. The route table SHALL be staged, validated and committed as a whole; the committed table SHALL have a content identity readable by the host; and the active table SHALL NOT be modified while a deployment that depends on it is `ARMED` or `RUNNING`, except through an explicitly defined and observable abort, fault or recovery operation. A router SHALL NOT reinstate an active route table on its own after power loss or reset. Hub-to-Hub AEL links SHALL carry the unchanged frame and the topology they form SHALL be acyclic; no run-time loop mitigation is defined. A router SHALL be manageable by the host at least to the extent of identity, supported AEL version, capabilities and limits, staged and integrity-checked route configuration with commit and activation, readback of the active configuration's identity, and per-port link, counter, queue and error state; the concrete management contract is defined outside this requirement.

**Rationale:** Typed events need a router, and a router is a processor in the event path — the property that [EDR-007](./edr/EDR-007-module-control-interface-and-module-hub.md) protected against and [EDR-008](./edr/EDR-008-auriora-event-link.md) accepts, on one condition: that the delay becomes a contract. Store-and-forward gives a corrupt frame a location — it stops and is counted where it was received — instead of consequences at every receiver downstream. A route table that is committed as a whole and frozen during a run is what lets a host prove afterwards which routing was in force, and what keeps "the Hub was reconfigured mid-experiment" from being a possible explanation of a result. Requiring published queue, rate and skew figures instead of a Platform-wide algorithm leaves implementers free and gives the host what it needs to refuse a deployment the bench cannot execute. The acyclic rule excludes the routing-loop problem by construction, which is cheaper and more predictable than any run-time mechanism that would solve it.

### 4.2 Guidance (non-normative)

- **Baseline behavioral model.** `IDLE → CONFIGURED → ARMED → RUNNING → COMPLETE`, with `COMPLETE → IDLE` (one-shot) or `COMPLETE → ARMED` (repeat-armed) as the two post-completion modes. A receive binding declares the states in which it is enabled: `START_SESSION` typically only in `ARMED`; `INSERT_MARKER` or `CHANGE_PHASE` in `ARMED` and `RUNNING`; nothing in `IDLE` or `CONFIGURED`. Firmware may use its own state names; what matters is that the armed gate, the per-state enables and the completion choice exist and are visible.
- **Three usage patterns.** *Trigger*: Module A's source binding `PROTOCOL_START → 0x0101` drives Module B's receive binding `0x0101 → START_SESSION`. *Marker*: a continuously recording Module binds `0x0101 → INSERT_MARKER`, enabled while `RUNNING`, and stamps each frame into its acquisition timeline. *Closed loop*: the recording Module's detector emits `DETECTOR_A → 0x0201`, a stimulus Module binds `0x0201 → START_BURST` while `RUNNING`, and reports `BURST_COMPLETE → 0x0301`, which the recording Module binds to a marker. All three use the same frame and the same links.
- **Scheduled actions stay local.** A known timeline — baseline, stimulus, pause, recovery at fixed offsets — belongs in the Module's Session and is executed locally against the Module's own clock. AEL carries what cannot be scheduled: a shared `T0`, detector-driven events, cross-Module reactions and completion markers whose actual time matters. This keeps event traffic small and keeps the Hub from becoming an experiment engine.
- **Feedback is a design, oscillation is a fault.** A closed loop may legitimately cycle — detection → stimulus → completion → detection. The host validates the event/action graph before deployment and requires a guard where a cycle could run unbounded: a detector refractory period, a maximum count, a state transition that disables the repeat, a timeout or hysteresis. None of this belongs in AEL or in Hub firmware; it is experiment design, and the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3.6 covers it.
- **The host is not in the timing path.** Once Modules are armed and routes are committed, the events of the experiment flow without the host. Whether a Module can complete an entire Session autonomously if the host disconnects is a declared Module capability, not a Platform rule; reconnection never re-arms anything.
- **Timing budget.** Distinguish source-event-to-frame latency, frame duration, cable propagation, per-hop router latency, frame-to-action latency and the latency of the physical action. Capture the reference instant as close to hardware as practical and characterize the rest. Implementation guidance is in the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §5.1 and the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) §14.2.
- **Third-party instruments.** An oscilloscope or DAQ sees AEL line activity but not events. Where an external instrument needs a plain trigger or marker edge, an AEL-to-trigger adapter — a receiver that emits an edge for a selected identifier — or a product-specific auxiliary trigger output provides it. AES keeps one Platform event interface.
- A worked multimodal example is [Worked Example: Multimodal AEL Experiment](../examples/worked-example-multimodal-ael-experiment.md).

## 5. Module Control Interface

The **AURIORA Module Control Interface (MCI)** is the Platform's transport-independent Module control contract: the identity, capability, lifecycle, configuration, Asset and Session semantics through which a host manages a Module.

AES has always named the Host Interface as the standard developer and integration interface a Module exposes, but required only that a Released one be deterministic and machine-parseable ([AES-IF-002](#aes-if-002-host-interface-determinism)). That leaves every Module free to invent its own identity query, its own capability model and its own notion of being ready to run — which is how a platform accumulates several incompatible control protocols and host software that special-cases each Module by type. MCI is the Platform's single realization of the Host Interface, so that work is done once.

MCI defines what an operation *means*. It deliberately says nothing about how the bytes travel; that is an **MCI transport binding**.

The dividing line against AEL, in one sentence: **MCI prepares and observes state; AEL carries the deterministic events.** A Module is discovered, configured, loaded and armed over MCI; the events on which armed Modules act are carried by AEL ([Section 4](#4-auriora-event-link)), never by a sequence of MCI operations issued Module by Module.

### 5.1 Transport Bindings

MCI is carried by one or more versioned bindings. A binding defines framing, request/response correlation, error signaling, flow control and — where the transport is a physical link — its electrical layer. Two bindings are intended:

| Binding | Transport | Role |
|---|---|---|
| Direct local transport | A local service connection such as USB | Commissioning, firmware update, diagnostics, recovery, manufacturing test, standalone operation. A Module remains serviceable through it without any infrastructure. |
| `MCL` — Module Control Link | Wired differential, point-to-point, one link per Module Port | Scalable multi-Module management through a [Module Hub](./03-architecture.md#7-module-hub). |

Neither binding is specified in this version of AES. `MCL`'s duplex model, electrical layer, framing and connector are open items ([Architecture §7](./03-architecture.md#7-module-hub)), and are fixed in a versioned binding specification under [`docs/interfaces/`](./interfaces/) when the requirements behind them are settled rather than assumed.

Direct local access is not a fallback that a Module may drop once it supports `MCL`. Loss of infrastructure must never remove the ability to recover, update or diagnose a Module.

### AES-MCI-001: Transport Independence

**Requirement:** MCI SHALL define Module control semantics independently of any transport. An MCI transport binding SHALL define carriage only — framing, request/response correlation, error signaling, flow control and, where the transport is a physical link, its electrical layer — and SHALL NOT add, remove or alter the meaning of an MCI operation. Where a Module implements MCI over more than one transport, an operation SHALL have the same meaning, the same preconditions and the same effect on Module Lifecycle State on each. A binding MAY be unable to carry a particular operation; it SHALL then report a defined error rather than substituting different behavior.

**Rationale:** A Module is commissioned over a local cable and then operated through infrastructure, and the operator, the script and the test are expected to behave identically in both cases. If the meaning of arming depends on whether the request arrived locally or through a Hub, every workflow has to be written and validated twice, and the local service path stops being a usable recovery path for a deployed Module. One contract is also what lets host software run against a simulated Module — already expected by the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3.4 — and what makes a future transport an addition rather than a second protocol.

### AES-MCI-002: Module Identity

**Requirement:** A Module implementing MCI SHALL expose a persistent identity readable before any configuration, unchanged across power cycles, transports, cables, Hub ports, host device paths and enumeration order. That identity SHALL convey at minimum the Module's Product Family and Product, its Product Revision, its firmware version, its manufacturing instance ([AES-ID-008](./04-naming-and-identity.md#aes-id-008-serial-numbers)) and the MCI version and transport bindings it implements; a Released Module SHALL additionally expose its AOID ([AES-ID-006](./04-naming-and-identity.md#aes-id-006-aoid-assignment)). A Module's identity SHALL NOT be derived from or depend on the port, Hub, cable position or host device path through which it is reached. Where a host records physical location, that topology information SHALL be held as metadata separate from identity.

**Rationale:** A Module moved to another Hub port is the same Module; a different Module in the same port is not. Only persistent identity separates those two cases, and they are not rare — recabling a bench is ordinary work. Host software that keys on a device node or a port index rebinds an experiment to the wrong hardware the first time two cables are swapped, and that failure produces plausible-looking data rather than an error, which is the worst class of failure an instrument can have. AES already keeps Family, Product, Revision and Instance identity separate ([AES-ID-001](./04-naming-and-identity.md#aes-id-001-identity-level-separation)); this is that separation made readable at runtime, and the Module-level counterpart of the Unit's electronic identity ([AES-UNIT-001](./03-architecture.md#aes-unit-001-electronic-identity)).

### AES-MCI-003: Module Capability Discovery

**Requirement:** A Module implementing MCI SHALL expose through MCI, before configuration, the optional MCI functions it supports — at minimum whether it provides Assets, Sessions, AEL IN, AEL OUT, event logging and firmware update — together with the limits a host must plan against where applicable, which for AEL SHALL include the supported AEL version, the maximum number of receive bindings and of event source bindings, and the Module's declared event-rate and timing envelope. A host SHALL determine a Module's supported functions by querying capabilities, and SHALL NOT infer them from Product Family, Product number, firmware version or device type. A Module SHALL refuse an operation it does not support with a defined error, never with undefined behavior or silent success.

**Rationale:** Hard-coded per-type assumptions are how host software acquires a table of special cases that has to be edited for every new Module and every firmware revision, and they fail silently when a Module is present but lacks the function assumed of it. Declared capabilities move that knowledge to the Module, where it is already true, which is the same reasoning that put execution model and capabilities in Unit discovery ([AES-UNIT-006](./03-architecture.md#aes-unit-006-declared-execution-model)). Silent success on an unsupported operation is singled out because it is the failure a host cannot detect: the experiment proceeds, and the missing function is discovered in the data.

### AES-MCI-004: Module Lifecycle and the ARM Boundary

**Requirement:** A Module implementing MCI SHALL expose over MCI a Module Lifecycle State carrying at least the meanings `IDLE`, `CONFIGURED`, `ARMED`, `RUNNING` and `COMPLETE`, and SHALL report both its transitions and the reason for any refused transition. A Module SHALL enter `ARMED` only when its configuration is valid, the Assets and selected Session its capabilities require are present and verified, and no blocking fault exists; a host SHALL be able to determine per Module whether arming succeeded before relying on it. Where relative execution timing between Modules matters, the deterministic event SHALL be carried by AEL ([AES-AEL-001](#aes-ael-001-ael-is-the-module-level-typed-event-interface)) and SHALL NOT be produced by issuing an MCI operation to each Module in turn. An MCI operation MAY start execution on a single Module where inter-Module timing does not matter.

**Rationale:** This is the rule that keeps the two interfaces from collapsing into each other. Sending a start operation to four Modules over a control link produces four different start times whose spread depends on link scheduling, queueing and host load; the spread is neither bounded nor recorded, so the resulting data looks synchronized and is not. Making `ARMED` an explicit, verifiable state is what lets an operator establish that every required Module is ready *before* the event — the last moment at which a missing or faulted Module can still be noticed. The receiving side of the same boundary is [AES-AEL-003](#aes-ael-003-event-identifiers-and-module-event-bindings): AEL executes only bindings that were armed.

### AES-MCI-005: Object Transfer Integrity

**Requirement:** Where a Module implementing MCI accepts Assets, Sessions, firmware or other bulk objects, transfer SHALL be staged: the transfer is opened, content is transferred, the received content is verified against an integrity value covering the whole object, and only then is the object committed and made selectable or active. A partially transferred, unverified or failed object SHALL NOT become active or selectable, and SHALL NOT be reported as present. A Module SHALL expose enough of its stored object inventory — identity and content integrity value — for a host to determine whether a transfer is needed before starting one. An interrupted transfer SHALL leave the Module in a defined state with any previously committed object unchanged.

**Rationale:** A half-written waveform that is selectable is a stimulus nobody designed, and neither the Module nor the host can tell it apart from the intended one after the fact; verification before commit is what makes the difference detectable at the only point where it is still cheap. Exposing the inventory addresses the other end of the same problem: when a bench holds many Modules that need the same Asset, blindly retransmitting to each is the difference between a deployment step that is usable and one that is not — and a content integrity value answers "is this already the right object" without transferring anything.

### 5.2 Guidance (non-normative)

- **Desired state over sequences.** Express a multi-Module setup as the state each Module should be in — configuration, Assets, Session — and let the host compare that against what each Module reports and transfer only the difference. This is what makes inventory exposure ([AES-MCI-005](#aes-mci-005-object-transfer-integrity)) worth having, and it degrades gracefully: a Module that is already correct costs one query.
- **Groups are a host concept.** Logical groups — all Modules, a treatment group, a measurement group — are orchestration in host software. They need no shared electrical bus and no broadcast addressing, and keeping them host-side is what lets the same grouping work for locally connected and Hub-connected Modules. Which Modules *receive* a given event is likewise decided by the host — as AEL receive bindings and Hub routes it compiles and commits — not by an addressing scheme on the wire.
- **Hot-plug changes nothing by itself.** Discovering a Module, or rediscovering one after a reconnection, establishes identity and capabilities and nothing more. Restoring configuration is a deliberate host action and re-arming is always explicit — [AES-MCI-004](#aes-mci-004-module-lifecycle-and-the-arm-boundary) and [AES-AEL-003](#aes-ael-003-event-identifiers-and-module-event-bindings) together mean a reconnected Module cannot resume an experiment on its own. A Module that declares the capability may *continue* an already armed or running Session while the host is away; it never *starts* or re-arms one because the host came back.
- **Error categories worth having early.** Unsupported operation, unsupported capability, invalid state, invalid configuration, timeout, transfer failure, integrity failure, busy, fault, storage exhausted, version incompatible, not armed, missing prerequisite. Module-specific faults stay outside the common set unless they are universally meaningful.
- **Asynchronous notification is not part of MCI in this version.** Every MCI operation is a host-initiated request with a response, and a Module reports what has happened to it — lifecycle transitions, refusal reasons, faults, AEL events — by being asked. That covers everything AES currently requires and keeps the first bindings simple. Whether a Module should additionally be able to report a fault unprompted is a real question and is deliberately left open: it changes what every binding must provide, and it is answered with the first binding specification rather than assumed ahead of one.
- **Framing, retries and validation are guide material.** How a binding frames, checks, times out and retries is already governed by the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) §14 and the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3. A binding specification states its own choices; it does not restate that discipline.

## 6. Compatibility

Compatibility claims about Released artifacts name what they cover — electrical, mechanical, firmware, protocol, documentation, manufacturing — and the version range: `Electrical and protocol compatible with UIF 1.1; mechanical incompatible without adapter`, not "compatible with APEM". Unqualified "compatible" is a support case waiting to happen. For prototypes, a compatibility note in the design notes suffices.

## 7. Evolution

### AES-EVO-002: Prefer Additive Evolution

**Requirement:** Interface, EEPROM and API evolution SHOULD prefer additive optional fields, capability flags and minor versions before breaking changes. When a break is necessary, it SHALL be versioned as a major change with migration guidance (adapter, dual support or explicit incompatibility).

**Rationale:** Installed hardware and published open designs cannot be updated like software libraries.

### AES-EVO-003: Deprecation With Migration

**Requirement:** Deprecating a Released interface, schema or artifact SHALL include reason, replacement path (or an explicit statement that none is feasible), affected versions and known risks. Retired contracts SHALL remain documented — reachable through tags or archives — with final supported version and reason for retirement.

**Rationale:** Old hardware still exists; deprecation without migration turns Platform artifacts into traps, and deleting interface history makes safety review impossible.

Breaking changes to Released interfaces additionally require a decision record — see [Decisions and Governance](./08-decisions-and-governance.md).

## 8. Guidance (non-normative)

- Test fixtures or procedures that verify identity discovery, error behavior and compatibility decisions are strongly recommended for Released Unit Interfaces — interface documents without tests drift from implementations.
- Documentation-only changes (typo, clarified example) are PATCH; manufacturing-only changes (approved substitution, process change) update the manufacturing package version and rerun affected tests; interface changes update the interface version even when the implementation diff is small.
