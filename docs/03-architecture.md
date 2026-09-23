# 03 Architecture

**Document ID:** AES-ARCH
**Status:** Normative
**Depends On:** [Terminology](./02-terminology.md), [Interfaces and Versioning](./05-interfaces-and-versioning.md)

## 1. Purpose

This chapter defines the architectural structure of the AURIORA Platform and the design rules for Modules, Controllers and Units.

Canonical definitions live in [Terminology](./02-terminology.md). The reuse order for new capabilities is the [decision tree in STANDARD.md](../STANDARD.md#7-primary-architectural-decision-tree).

## 2. Platform Model

The Platform owns standards and compatibility. Modules own product-level function and safety policy. Controllers own dedicated control implementation. Units own replaceable function. Interfaces own interoperability contracts.

Ownership boundaries, in one table:

| Owner | Owns | Does not own |
|---|---|---|
| Platform | Vocabulary, AES, compatibility policy, identifier governance. | Product-specific experiment policy. |
| Product Family | Family identity, design scope, compatibility expectations across products and revisions. | Manufacturing instance records. |
| Module | Product function, safety policy, external behavior, supported interfaces, release completeness. | Private changes to Platform terminology or Unit Interface semantics. |
| Controller | Control implementation, startup sequence, fault containment, firmware update path. | Module-level product identity or public safety claims. |
| Unit | Replaceable function, declared limits, identity metadata, Unit-specific calibration linkage. | Module experiment policy. |
| Host / Unit Interface | The interoperability contract: commands, errors, electrical/mechanical/protocol compatibility. | Product behavior beyond the contract. |

Every externally visible behavior, safety limit and compatibility promise has one accountable owner. In a one-person team that owner is the maintainer — the point is that the *boundary* is stated, not that different people hold it.

## 3. Module Design

A Module is a standalone product: it is usable and reviewable even if its Controller implementation changes. For Active Development and Released Modules, keep the following visible in the README or design notes: intended function, supported Host and Unit Interface versions, Controller inventory, power architecture and safety limits, calibration dependencies, and known issues. A single living document is fine; separate formal design records are not required.

A Module's control surface is the [Module Control Interface](./05-interfaces-and-versioning.md#5-module-control-interface) (MCI): the Platform's transport-independent contract for identity, capabilities, lifecycle, configuration, Assets and Sessions. A Module that exposes a Host Interface SHOULD expose it as MCI rather than as a private command set, so that host software, test fixtures and a Module Hub reach every Module the same way. This remains a SHOULD in this version because no MCI transport binding is specified yet ([Interfaces and Versioning §5.1](./05-interfaces-and-versioning.md#51-transport-bindings)); [AES-MOD-002](#aes-mod-002-host-interface-for-released-modules) continues to require only a documented Host Interface. A Module that takes part in a multi-Module installation — through a [Module Hub](#7-module-hub) or directly with one peer — does so through its single Module Port (§7.1), which does not replace the Module's own local service transport; its primary operating power arrives on a separate connector ([AES-MOD-005](#aes-mod-005-external-interfaces-and-power-separation)).

A Module MAY provide AURIORA Event Link links (AEL IN, AEL OUT), carried in its Module Port, for deterministic typed events with other Modules. If it does, it follows [Interfaces and Versioning §4](./05-interfaces-and-versioning.md#4-auriora-event-link) and the [AEL specification](./interfaces/ael.md), and its README or design notes list the receive actions and internal event sources it can bind. AEL is a Module responsibility: it is never delegated to a Unit or carried on a Unit Interface.

A Module MAY support **unattended autonomous operation**: continuing a prepared Session, managing its own Units, storage and faults, and recovering after a reset without a connected host or Module Hub. This is a declared capability with explicitly configured behavior — *autonomous continuation* and a *deployment policy*, [AES-MCI-006](./05-interfaces-and-versioning.md#aes-mci-006-autonomous-continuation-and-deployment-policy) and [AES-MCI-007](./05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance) — never an assumption a host makes from the product type. When declared, the Module's Controller owns continued Session execution, local data handling and the configured recovery behavior for as long as the host is absent, and neither a Module Hub nor AEL is a prerequisite: a single Module on a local cable, prepared and then left alone, is an ordinary way to use the Platform. A Module that does not declare the capability is operated exactly as before. A Module that records data locally exposes what it recorded as stored objects through the same control interface ([AES-MCI-008](./05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval)), so that a recording made alone in the field and one made under a Module Hub are enumerated and read the same way.

### AES-MOD-003: Unit Compatibility Matrix

**Requirement:** A Released Module that accepts Units SHALL publish a compatibility matrix listing supported Unit Interface Profiles and versions, compatible Unit classes, calibration requirements, and the Module's own Unit-facing electrical limits: how many ports of each profile it provides, what one port supplies, and any restriction on operating those ports simultaneously. During Active Development a running list in the design notes is sufficient.

**Rationale:** Replaceable Units are useful only when compatibility can be determined before installation. A Unit is required to declare what it needs, with numbers ([AES-UNIT-004](#aes-unit-004-declared-limits), [AES-EEPROM-008](./06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)); the matrix is where the other side of that contract is stated. Port count is not a power promise: a Module may expose more ports than it can drive at once, which is a compatibility fact its users need before installation rather than a defect to hide.

### AES-MOD-004: Safety Policy Ownership

**Requirement:** The Module SHALL own safety policy for its complete externally visible function, including Unit behavior, Controller behavior, power limits and Host commands. This applies at every maturity level: even an Experimental Module states its hazards and enforces its own limits.

**Rationale:** Safety emerges from the integrated product, not from any single board. A replaceable Unit's self-declared capability is never a safety authorization (see [AES-EEPROM-007](./06-eeprom-metadata.md#aes-eeprom-007-metadata-trust-model)).

### AES-MOD-002: Host Interface for Released Modules

**Requirement:** Every Released Module with firmware SHALL expose at least one documented Host Interface, unless the Module is purely passive.

**Rationale:** Host Interfaces enable testing, calibration, automation and reproducibility. An undocumented debug UART is not an interface others can build on.

### AES-MOD-005: External Interfaces and Power Separation

**Requirement:** A Module SHALL keep its **Platform-facing** external interfaces — those by which it communicates with the Platform and receives its primary operating power — to at most three roles, each on its own connector: the **Module Port** ([§7.1](#71-the-module-port)) carrying `MCL`, AEL IN and AEL OUT; the **Module Power Interface** ([`docs/interfaces/module-power.md`](./interfaces/module-power.md)) carrying its primary operating power; and its **direct local transport** ([Interfaces and Versioning §5.1](./05-interfaces-and-versioning.md#51-transport-bindings)) for service, configuration, firmware update and local data access, for which USB-C SHOULD be the connector. A Module SHALL provide at most one Module Port and SHALL NOT provide a separate AEL connector. The Module Port SHALL NOT carry a Module's primary operating power, and a Module SHALL NOT depend on a Module Hub, a power distributor or any other infrastructure device for that power. Where a Module has an external primary power input it SHALL be a Module Power Interface input at a nominal 12 V DC, from which the Module generates every internal rail; a battery or a product-specific input MAY exist in addition where the product definition justifies and documents it. A Module MAY accept power from its direct local transport for development, service, configuration or declared low-power operation where it does so safely; USB SHALL NOT be the required primary power of a deployed Module, a Module SHALL NOT present voltage on its power-input contacts from any other source, and neither the Module Power Interface nor any Module rail SHALL back-drive a host's USB port or any other connected source. Measurement-side connectors — electrodes, sensors, actuators and externally mounted Unit Interface ports — are outside this rule and belong to the product definition. The Module-to-Unit managed power of the Unit Interface (`UIF_PWR_VIN`, `UIF_PWR_EN`) is a separate contract and SHALL NOT be confused with, or carried on, either Platform-facing interface.

**Rationale:** What a Module says and what it eats arrive on different connectors, and everything else about the outside of a Module follows from that. A communication port that also powers the far end turns the Hub into a power distributor whose budget is the sum of its ports; a Module that regulates its own rails from one standard input works on a bench, in a field enclosure and under a Hub with the same hardware; and one connector per role means one cable per role and nothing that can be plugged into the wrong place. USB stays optional as a power source because its negotiation, cable drop and host behavior are outside the Platform's control, and a high-power Module could not honestly promise to run from an arbitrary computer. The back-feed rules are the safety property behind the gender rule of the power specification: the only male power contacts in the system are the Module's own input, and nothing but the cable plugged into them may make them live ([EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md)).

## 4. Controller Design

A Controller is the dedicated control implementation inside a Module — a PCB, MCU firmware assembly, embedded computer or FPGA design. Controllers are separated from Modules (see [EDR-001](./edr/EDR-001-controller-module-separation.md)) so control implementation can evolve without erasing the Module-level contract. For any Controller beyond a throwaway experiment, state in the design notes: which Module it serves, what it owns (typically startup, discovery, sampling, fault containment), and how firmware is updated and identified.

### AES-CTRL-002: Deterministic Startup

**Requirement:** Controller firmware that can energize outputs, actuators or Unit power SHALL implement a documented startup sequence in which such outputs remain in a safe state until configuration, identity and calibration checks (where applicable) have passed. This applies at every maturity level.

**Rationale:** Undefined startup behavior causes intermittent failures and unsafe states — on breadboards as much as in products.

### AES-CTRL-003: Fault Containment

**Requirement:** Released Controllers SHALL detect and contain the faults applicable to their design — power, communication, identity mismatch, calibration mismatch, firmware corruption, timing overrun — with defined responses. During earlier maturity this SHOULD guide the design, with known gaps listed in the design notes.

**Rationale:** A modular ecosystem must fail in ways that are diagnosable and bounded.

## 5. Unit Design

A Unit is the Platform mechanism for concentrating reusable engineering investment — sensing, stimulation, interface, calibration or mechanical capability — into bounded, identifiable, replaceable building blocks. If a board has no reusable interface, identity or calibration contract, it is a Module subassembly, not a Unit; calling it a subassembly is fine.

For Active Development and Released Units, keep visible: Unit class and function, supported Unit Interface version, electrical limits, mechanical envelope, EEPROM metadata fields, and calibration ownership.

### 5.1 Execution Models and Transport

Every Unit is realized as one of two execution models. Both remain Units under the same identity, interface and compatibility rules — these are execution models, not separate top-level product categories.

- **Passive Unit.** A Unit without independently executing application firmware. The host Module directly controls the Unit's sensors, actuators, converters or other functional circuits through the Unit Interface. A Passive Unit is not required to contain a microcontroller.
- **Managed Unit.** A Unit containing one or more programmable controllers and exposing a versioned, high-level Unit API. The host Module operates the Unit through that API and is not required to know or control the Managed Unit's internal components, register-level interfaces, radio configuration, GNSS configuration, sensor configuration or other implementation details. A Managed Unit is therefore designed and documented as a capability provider, not as a collection of low-level peripheral drivers exposed to the host.

The execution model is independent of the **transport** the Unit Interface uses. Managed does not imply SPI: the execution model fixes the host contract — direct peripheral control versus a versioned Unit API — while throughput, latency, timing determinism and streaming behavior select the transport and therefore the Unit Interface Profile. A low-bandwidth Managed Unit legitimately uses an I²C transport. The profile family and the selection rule are in [Interfaces and Versioning §3.2](./05-interfaces-and-versioning.md#32-profile-family-and-selection) ([AES-IF-010](./05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection)).

### AES-UNIT-006: Declared Execution Model

**Requirement:** A Unit SHALL declare its execution model — Passive or Managed — in its documentation, and a Managed Unit SHALL additionally expose, through the Unit discovery mechanism, its supported capabilities and Unit API version. A host Module SHALL NOT be required to know or control a Managed Unit's internal components or register-level interfaces to operate it through its declared Unit API.

**Rationale:** The host contract differs by model: a Passive Unit is driven directly, a Managed Unit is driven through a high-level API. Making the model discoverable lets the host apply the right contract without hard-coded assumptions. The model is declared separately from the Unit Interface Profile because the two are independent: the model says how the host talks to the Unit, the profile says over what.

### AES-UNIT-007: Deterministic Discovery and Activation Sequence

**Requirement:** A Module SHALL activate a Unit in this order: (1) supply `UIF_PWR_VIN`; (2) discover the Unit through the Unit EEPROM on the Unit Interface I²C bus; (3) read and validate the Unit descriptor; (4) check Unit type, interface profile, hardware compatibility, API compatibility, capabilities and power requirements; (5) if the Unit is supported, assert `UIF_PWR_EN`; (6) wait a bounded time for `UIF_READY`; (7) begin functional communication only after `UIF_READY` is HIGH. If the Unit is unsupported, incompatible, invalid, or exceeds the host power capability, `UIF_PWR_EN` SHALL remain LOW. The Unit EEPROM and the minimum circuitry required for discovery SHALL remain powered and readable from `UIF_PWR_VIN` while `UIF_PWR_EN` is LOW. The wait at step (6) SHALL be bounded; on expiry the host SHALL de-assert `UIF_PWR_EN` and treat the Unit as failed rather than transacting with it. The bound itself is a profile or product property, not a Platform constant.

**Rationale:** A single deterministic sequence keeps unknown or incompatible Units unpowered and un-commanded until compatibility and power are validated (see [AES-IF-007](./05-interfaces-and-versioning.md#aes-if-007-safe-default-state) and [AES-EEPROM-002](./06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order)). Physical presence is established by successful EEPROM discovery, so no separate presence signal is required. Discovery power is not optional: the sequence validates a Unit before enabling it, so the discovery domain must be readable while the functional domain is off. An unbounded wait for `UIF_READY` is the one step that can hang the host on a Unit that never initializes, so the wait is bounded even though its length is not.

### AES-UNIT-001: Electronic Identity

**Requirement:** A Released replaceable Unit whose replacement affects electrical behavior, data interpretation, safety, calibration or compatibility SHALL provide electronic identity using the [AES EEPROM metadata specification](./06-eeprom-metadata.md) or a documented equivalent. Experimental Units, and Units whose replacement affects none of those, are exempt; Active Development Units SHOULD design the identity in early, because it is hard to retrofit. This exemption is about the identity contract, not the execution model: a Passive Unit that participates in discovery still carries the EEPROM used by the activation sequence ([AES-UNIT-007](#aes-unit-007-deterministic-discovery-and-activation-sequence)).

**Rationale:** Human labels cannot support automated compatibility and calibration decisions (see [EDR-002](./edr/EDR-002-runtime-unit-identity.md)).

### AES-UNIT-003: Replaceability Without Source Modification

**Requirement:** Replacing a compatible Released Unit SHALL NOT require source-code modification, firmware rebuild or undocumented configuration.

**Rationale:** Replaceability is architectural, not merely physical.

### AES-UNIT-004: Declared Limits

**Requirement:** Units SHALL declare the electrical, mechanical, thermal, optical, acoustic, chemical or biological-contact limits applicable to their function, with numbers and units. For Experimental Units a limits note in the README satisfies this.

**Rationale:** Modules cannot enforce safe operation without knowing Unit limits. This is a safety rule and applies at every maturity level.

### AES-UNIT-005: Calibration Ownership

**Requirement:** A Unit whose function depends on measured characteristics SHALL state, before Release, where calibration data lives (on the Unit, in a Module database, in a release package or in an external record) and how it links to the Unit's serial number.

**Rationale:** Ambiguous calibration ownership causes invalid data and irreproducible experiments.

## 6. Default Controller Platform Strategy

AURIORA concentrates its firmware, tooling and reuse investment on a small number of controller platforms. This section states the Platform's *default* choice; it does not restrict what a design may use.

Two workload profiles carry the default:

| Workload profile | Characteristics | Default platform |
|---|---|---|
| **Bounded low-power function** | One well-bounded sensor, actuator or interface function; local device control; Unit Interface or Host Interface communication; low to moderate compute; low power as a priority; simple firmware; integrated program Flash and minimal external part count. | Low-power **STM32-class** MCU (e.g. the STM32U0 or STM32L0 families). |
| **Local processing** | Sustained or high-rate data flow; significant DMA and buffering demand; DSP or signal generation; several concurrent time-critical tasks; peripheral behavior that benefits from programmable I/O, a second core or larger SRAM. | **RP2040-class** MCU. |

Most Units fall in the first profile, and Modules that perform substantial local processing fall in the second — but the profile, not the architectural role, selects the platform. A Managed Unit doing continuous DSP belongs in the second profile; a thin Module belongs in the first.

Examples, illustrative only: the Environmental, Spectral, Communication & Timing, Soil and Geophysical Units are STM32-class (the Spectral and Communication & Timing Units on STM32U031); the Plant Electrophysiology and Audio Modules are RP2040-class.

### AES-ARCH-001: Default Controller Platform

**Requirement:** A new AURIORA Controller or Managed Unit controller SHOULD use the default platform for its workload profile: a low-power STM32-class MCU for a bounded low-power function, and an RP2040-class MCU where higher local processing, buffering, DSP or parallel real-time workloads justify it. A design MAY use another platform where its technical requirements warrant it; the choice and its reasons SHALL then be stated in the project's design notes or an ADR.

**Rationale:** Converging on two platforms concentrates firmware reuse, HAL work, toolchain support and part familiarity, and makes controller substitution predictable across product families. It is a default, not a restriction: naming the two defaults is what makes a departure from them a visible, reasoned decision rather than an accident (see [EDR-004](./edr/EDR-004-default-controller-platforms.md)).

This is the one place where AES names vendor *controller* platforms. Everything else about a Controller — peripheral choice, part numbers, packages, memory sizing — remains routine engineering judgment, recorded per [Decisions and Governance §3](./08-decisions-and-governance.md#3-when-a-decision-needs-a-record). The other admitted vendor naming is the connector family in the Unit Interface Profile specifications, where [AES-IF-006](./05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness) requires a named physical connector; each such naming is carried by the profile's own decision record.

## 7. Module Hub

A Module is usable on its own. It is also expected to appear on a bench alongside many others that must be discovered, configured, loaded, armed and monitored together, and whose events must reach one another — and connecting each one individually to a host, and each one to every peer it reacts to, stops scaling well before the bench does.

The **AURIORA Module Hub** is the Platform's optional answer: an active-star infrastructure device presenting one **Module Port** per connected Module. It is a composite of three roles that stay separate inside it:

| Role | What it does | Timing posture |
|---|---|---|
| MCL concentrator | Carries [MCI](./05-interfaces-and-versioning.md#5-module-control-interface) between the host and each Module over that Module's `MCL` link; tracks port presence and link state; reports faults. | Managed; bursty, queued, latency-tolerant. |
| AEL router | Receives [AEL](./05-interfaces-and-versioning.md#4-auriora-event-link) event frames on Module Ports and Hub-to-Hub AEL links, validates each completely, and forwards it by ingress port and event identifier onto the outputs selected by a committed route table ([AES-AEL-005](./05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)). Knows ports, identifiers and routes; never what an identifier means. | Bounded real-time subsystem with a published timing contract: forwarding latency, jitter, fan-out skew, queue capacity, overflow behavior. |
| AEL event source (optional) | Originates an AEL event — a host-requested `T0`, a scheduled marker — through its own event source bindings. | Generates the frame; the frame then enters the router like any other. |

The separation is the design. Management traffic is bursty and tolerant of latency; an event frame carries only a type, and its information is *when* it arrives. Both now pass through firmware, so the rule is no longer "no processor in the event path" but "the event path is a real-time subsystem whose figures are measured and published, and which management traffic cannot starve". A Hub whose forwarding latency depends on how many Assets are being transferred at the time does not meet [AES-AEL-005](./05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior).

```text
                              HOST
                               |
                    (host-facing interface)
                               |
                    +----------------------+
                    |     MODULE HUB       |
                    |  MCL concentrator    |  managed
                    |  AEL router          |  (port, event_id) → outputs, committed route table
                    |  AEL source (opt.)   |
                    +----+------------+----+
                         |            |
          +--------------+---+        +── Hub-to-Hub AEL link ──► another Module Hub
          |              |   |
     Module Port 1  Module Port 2 ... Module Port N
          |              |            |
       Module         Module       Module
```

An active star is chosen over a shared multidrop bus for the same reason AEL links are point-to-point: each port has its own driver, receiver and termination, so its behavior does not depend on how many other Modules happen to be connected, and a fault on one port does not take the bench down.

A Module Hub is a communication device. It does not supply the operating power of the Modules on its Module Ports — each Module has its own [Module Power Interface](./interfaces/module-power.md) input — and it is itself powered through its own power input, for which a Module Power Interface input is the preferred form ([AES-MOD-005](#aes-mod-005-external-interfaces-and-power-separation)). A device that distributes power to several Modules is a separate, currently unspecified product, not a Hub role.

The host reaches the Hub through its **host-facing interface** — a connection that is neither a Module Port nor a Hub-to-Hub AEL link, and that carries the Hub's own management together with the MCI of every Module behind it. It is an MCI transport binding, intended to be the same direct local transport a Module uses on a cable, so that AURIORA Studio speaks one protocol whether it faces a Module or a Hub; USB is its first realization, and on USB the Hub is the *device* and the computer the *host* — the everyday phrase "USB host port" would describe the opposite and is not used. No AEL frame travels on it: the host is not in the timing path ([AES-MCI-004](./05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary)), and it learns of events from logs and counters. Bulk traffic — objects loaded into Modules and stored objects read back ([AES-MCI-008](./05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval)) — crosses the Hub as ordinary MCI in bounded chunks, and the Hub understands none of it ([AES-HUB-003](#aes-hub-003-host-facing-interface-and-traffic-separation)).

A Module Hub holds no Session and no experiment state of its own. Its active route table is not reinstated after a Hub reset unless the host has set an explicit **route recovery policy** ([AES-AEL-005](./05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)): under *none*, the default, the router comes back idle and the host re-commits; under *reinstate*, the router restores the last committed table after verifying its content identity, records and reports that it did so, and an unattended deployment whose events must cross a Hub survives a Hub power loss the way a Module survives its own under [AES-MCI-007](./05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance). That policy is the Hub's one piece of deployment policy. Modules wired directly to one another, or a single Module on its own, carry no such dependency.

Scaling has two parts on one cable. **AEL scales through Hub-to-Hub AEL links**: a router output driving another router's input, carrying the unchanged frame, in an acyclic topology ([`docs/interfaces/ael.md`](./interfaces/ael.md) Section 8.6). **`MCL` scales by cascading** ([AES-HUB-005](#aes-hub-005-cascading-and-path-addressing)): a downstream Hub's Hub-to-Hub link port is cabled to an upstream Hub's Module Port, the upstream Hub polls it as it polls a Module, and every device is addressed by the path of port indices from the root Hub. An installation therefore has one **root Hub** on the host's host-facing interface and a tree of Hubs below it, and the host learns the whole tree by discovery. A host MAY still reach several root Hubs at once ([AES-HUB-002](#aes-hub-002-port-independence-and-scale-interoperability)); a Link Cable between two link ports then carries AEL only. Stored object retrieval ([AES-MCI-008](./05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval)) is specified end-to-end between host and Module, and every intermediate Hub forwards it as MCI it does not interpret.

### AES-HUB-001: Module Hub Scope

**Requirement:** A Module Hub SHALL act as MCI transport infrastructure, AEL routing and, where provided, AEL event origination only. It SHALL NOT own, interpret or depend on Module-specific configuration, Session or experiment semantics — an AEL route is a mapping of ports and identifiers, never a rule about what an event means; it SHALL NOT be the source of a Module's identity ([AES-MCI-002](./05-interfaces-and-versioning.md#aes-mci-002-module-identity)); it SHALL NOT discover, configure, address or power Units, which remain the responsibility of their parent Module; and it SHALL NOT be required to supply, and a Module Port SHALL NOT carry, a Module's primary operating power ([AES-MOD-005](#aes-mod-005-external-interfaces-and-power-separation)). A Module SHALL remain fully serviceable — commissioning, configuration, firmware update, diagnostics and recovery — through its direct local MCI transport without a Module Hub, and two Modules SHALL remain able to exchange AEL events directly without one; a Module Hub SHALL NOT be a prerequisite for any of those.

**Rationale:** A Hub that must understand each Module type has to be revised whenever a Module is added or its firmware changes, and it becomes the component that blocks the bench. Keeping module-specific meaning in host software and Module firmware — where it already lives — is what lets one Hub design serve Modules and experiments that do not exist yet; a route table of numbers is the most a Hub may know. Reaching Units through a Hub would breach the containment that makes a Module a product contract rather than a wiring point ([EDR-001](./edr/EDR-001-controller-module-separation.md)): a Unit is discovered, validated and powered by its Module under [AES-UNIT-007](#aes-unit-007-deterministic-discovery-and-activation-sequence), and a second authority over that sequence is a safety problem, not a convenience. Recovery and direct AEL are called out separately because infrastructure fails: if the only path to a Module with corrupt firmware, or the only path between two Modules, runs through a Hub, a Hub fault turns a recoverable bench into a returned one. Keeping Module power off the Hub keeps its port count a communication decision rather than a power budget: eight Modules at half an ampere each would already ask a centrally powered Hub for four amperes before the first higher-power Module, start-up peak or cable loss is counted — a motivation, not a limit.

### AES-HUB-002: Port Independence and Scale Interoperability

**Requirement:** Each Module Port of a Module Hub SHALL be independently managed: independent link state, independent communication timeout and independent fault handling, such that a fault, disconnection, timeout or unpowered Module on one port does not disturb MCI traffic or AEL routing on another. The number of Module Ports and of Hub-to-Hub AEL links SHALL NOT be encoded in MCI, in an MCI transport binding, in the AEL frame or in the Module Port contract, and the same Module Port contract SHALL apply regardless of a Hub's port count, so that Hubs of different sizes and Modules from different designs remain interoperable. A host SHALL support more than one Module Hub concurrently, and Hubs SHALL be distinguishable from one another.

**Rationale:** Fault containment is the main thing an active star buys over a passive bus, and it is only real if it is a requirement rather than an implementation side effect — one Module with a damaged cable should cost one port, not a run. Leaving port count out of the contracts is what keeps a four-port and a sixteen-port Hub from becoming two incompatible products: a practical reference implementation may settle on eight Module Ports and a couple of Hub-to-Hub links, but those are product decisions, never a protocol limit. Multi-Hub support follows from the same place: a bench outgrows one Hub long before it outgrows the architecture, and a host that assumes a single Hub has to be rewritten rather than reconfigured.

### AES-HUB-003: Host-Facing Interface and Traffic Separation

**Requirement:** A Module Hub SHALL provide a **host-facing interface** through which the system host reaches the Hub's own management contract and, through the `MCL` concentrator, the MCI of every Module on its Module Ports. The host-facing interface SHALL be distinct from the Module Ports and from Hub-to-Hub AEL links and SHALL consume neither; it SHALL be an MCI transport binding, so that a Module reached through a Hub is operated with the same MCI semantics as on a local cable ([AES-MCI-001](./05-interfaces-and-versioning.md#aes-mci-001-transport-independence)); and it SHALL NOT carry AEL frames to or from the host. Where it is realized as USB, the Module Hub SHALL be the USB device and the system host the USB host. A Module Hub SHALL forward MCI between the host and a Module without interpreting it ([AES-HUB-001](#aes-hub-001-module-hub-scope)), stored object retrieval ([AES-MCI-008](./05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval)) included, and SHALL buffer no more than the responses to requests the host has outstanding, so that a host that reads slowly cannot overflow the Hub or a Module. A control operation issued to any Module Port while a bulk transfer is in progress on the same or another port SHALL be served within the time of one chunk plus the binding's overhead, and a bulk transfer SHALL NOT occupy the host-facing interface or an `MCL` link for longer than one chunk at a time. The AEL router's documented timing contract ([AES-AEL-005](./05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)) SHALL hold while MCI traffic, bulk transfer included, passes through the Hub. The host-facing interface SHALL NOT be the source of the power a Hub's AEL router needs to meet its timing contract, and Module Ports carry no Module power that it could source ([AES-HUB-001](#aes-hub-001-module-hub-scope)); whether the Hub itself may be powered from it is a product decision documented with the resulting limits.

**Rationale:** The interface is named for its role because the USB roles invert the everyday reading — the Hub is the device, the computer is the host — and a name that got that wrong would be read as a requirement. Reaching a Hub with the same binding a Module uses on a cable is what keeps Studio to one protocol stack and a Module's behavior independent of the path to it; the binding, not MCI, absorbs the addressing a concentrator needs. Keeping AEL frames off the host link is the host-not-in-the-timing-path rule seen from the Hub. The buffering and chunk rules close the two places where bulk traffic could otherwise defeat the architecture: a Hub that forwards unsolicited data must hold it for a host that may not be reading, and a link occupied by a whole object makes an abort wait behind a download. Events need no such protection because they are not on the same wires — the Module Port keeps `MCL` and AEL electrically independent and no AEL frame ever becomes an `MCL` message ([§7.1](#71-the-module-port)) — which is why two traffic classes suffice where a general quality-of-service scheme would otherwise have been invented; the one place bulk and events meet is inside the router's controller, and there the timing contract already had to hold under management load. Power is separated because a bench of Modules is not a USB peripheral, and a router whose timing depends on how much current a laptop port supplies does not have a timing contract.

### AES-HUB-004: Hub Identity and Capability Discovery

**Requirement:** A Module Hub SHALL expose through its host-facing interface, before any route table is staged or any port is configured, a persistent **identity** and a declared set of **capabilities**. The identity SHALL convey at minimum the Hub's Product Family and Product, its Product Revision, its firmware version, its manufacturing instance ([AES-ID-008](./04-naming-and-identity.md#aes-id-008-serial-numbers)) and the AEL specification version and MCI transport bindings it implements; a Released Hub SHALL additionally expose its AOID ([AES-ID-006](./04-naming-and-identity.md#aes-id-006-aoid-assignment)); and it SHALL NOT depend on the host device path through which the Hub is reached, as [AES-MCI-002](./05-interfaces-and-versioning.md#aes-mci-002-module-identity) requires of a Module. The capabilities SHALL convey at minimum the **number of Module Ports** and the **number of Hub-to-Hub AEL links** the Hub provides; a **stable index** for each, by which the host names it in route configuration and observability and by which the Hub reports it; the **link state** of each Module Port and Hub-to-Hub link ([`docs/interfaces/ael.md`](./interfaces/ael.md) Section 8.5); whether the Hub originates AEL events and, if so, its source-binding limit; and the router's declared figures — route table capacity, queue depth per output, forwarding latency envelope and fan-out skew ([AES-AEL-005](./05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior)). Where a Hub's Module Ports or Hub-to-Hub links are not all of the same capability, the capability of each SHALL be declared per index. A host SHALL determine a Hub's port count, link count and router figures from these declarations and SHALL NOT infer them from Product Family, Product number, firmware version or device type; a Hub SHALL refuse a configuration that names a port or link it does not have with a defined error. This requirement fixes *what* the Hub's management contract exposes; the form in which it is exposed belongs to that contract, which remains open ([`docs/interfaces/ael.md`](./interfaces/ael.md) Section 10.2). Nothing in this requirement identifies the device at the far end of an AEL-only Hub-to-Hub link; a downstream Hub is discovered over cascaded `MCL` ([AES-HUB-005](#aes-hub-005-cascading-and-path-addressing)).

**Rationale:** [AES-HUB-002](#aes-hub-002-port-independence-and-scale-interoperability) keeps the port count out of MCI, the bindings, the AEL frame and the Module Port contract so that Hubs of different sizes interoperate; that freedom is only usable if the host can learn each Hub's size at run time, otherwise the knowledge moves into a product table in host software, which is the failure [AES-MCI-003](./05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery) refuses for Modules. A stable index is what a route table, a counter and the topology metadata that [AES-MCI-002](./05-interfaces-and-versioning.md#aes-mci-002-module-identity) keeps separate from identity all refer to; without one, a port number means whatever the last enumeration made it mean. The identity mirrors the Module's because a Hub moved to another host port is the same Hub, and the recabling argument applies unchanged. The far end of a Hub-to-Hub link is excluded deliberately: a cascaded neighbour is found by walking the tree ([AES-HUB-005](#aes-hub-005-cascading-and-path-addressing)) and an AEL-only neighbour is not identified by anything on the link, and a Hub that reports only its own ports and links needs no knowledge of its neighbours to be correct.

### AES-HUB-005: Cascading and Path Addressing

**Requirement:** On a Module Hub, the `MCL` end of every Module Port SHALL be the polling master and the `MCL` end of every Hub-to-Hub link port SHALL be a responder. A Module Hub SHALL be operable as a **downstream Hub**: one Link Cable from one of its Hub-to-Hub link ports to a Module Port of an **upstream Hub**, over which the upstream Hub reaches the downstream Hub's management contract and, through it, every device on the downstream Hub's Module Ports, while the AEL pairs of the same cable form a Hub-to-Hub AEL link as before. A Hub SHALL accept MCI from at most one upstream at a time — its host-facing interface or one Hub-to-Hub link port — and SHALL refuse and report a second; the management contract reached through either upstream SHALL be the same. A device behind one or more Hubs SHALL be addressed by the **path** of port indices ([AES-HUB-004](#aes-hub-004-hub-identity-and-capability-discovery)) from the root Hub, and a Hub SHALL forward an MCI exchange to the port its own path element names without interpreting the remainder ([AES-HUB-001](#aes-hub-001-module-hub-scope)). A Link Cable between two Hub-to-Hub link ports carries AEL only, its `MCL` pair joining two responder ends; a Link Cable between two Hubs' Module Ports is a cabling fault that each port SHALL detect and report without damage ([Module Port specification](./interfaces/module-port.md)). The `MCL` binding SHALL correlate requests and responses by identifier so that a response may arrive in a later exchange than its request, and SHALL NOT assume lock-step request-response on a link. A Module SHALL NOT act as an `MCL` master: on a direct 1:1 Module-to-Module link the `MCL` pair is idle and each Module is managed over its own direct local transport. Path element width, maximum depth and the MCI latency budget per hop are the binding's; AEL timing across Hubs is unchanged ([`docs/interfaces/ael.md`](./interfaces/ael.md) Section 8.6).

**Rationale:** Roles fixed by port kind keep the half-duplex pair free of arbitration: two ends of the same kind meeting on a cable are either two responders, which is silence, or two masters, which is a detectable fault — never a negotiation, and never an election in firmware. Cascading through a Module Port rather than through a new port type means an upstream Hub polls a downstream Hub exactly as it polls a Module, so a Hub needs to know nothing about what hangs on a port to forward to it, and every port is the same transceiver with its role in firmware; the product decides how many ports it labels for Modules and how many for Hubs. One upstream per Hub makes the management topology a tree by construction, so a cycle cannot even be addressed, and the host learns the whole installation by walking the tree from the identity and capability declarations that already exist. Path addressing is the addressing a tree needs and nothing more: no allocation protocol, no tables, and stable under recabling because identity stays separate from path ([AES-MCI-002](./05-interfaces-and-versioning.md#aes-mci-002-module-identity)). Distance decides that cascading is needed at all: the host-facing interface is a few metres of USB, the Link Cable an RS-485-class run, and a bench spread across a room or a greenhouse cannot be one USB cable per Hub. Tagged correlation is required here because a response from behind a downstream Hub cannot be bounded by the response time of a Module; cascading is what turns it from a binding preference into a requirement. A Module is kept out of the master role because a Module that polls a peer is a Hub with fewer ports, and the Module's own service connection already covers the two-Module case.

### 7.1 The Module Port

A Module that takes part in a multi-Module installation has one **Module Port**: a single M8 8-position connector carrying that Module's `MCL` link together with its AEL IN and AEL OUT links, connected by one **AURIORA Link Cable** to a Module Hub or directly to one peer Module. It is the Module's only communication connector for those links: there is no separate AEL connector, and a Module that provides `MCL`, AEL IN or AEL OUT at all provides exactly one Module Port ([AES-MOD-005](#aes-mod-005-external-interfaces-and-power-separation)). The connector, the contact roles and the cable are specified in [`docs/interfaces/module-port.md`](./interfaces/module-port.md).

Settled about it ([EDR-011](./edr/EDR-011-module-external-interfaces-and-power.md)):

- **The links stay electrically independent inside it.** Sharing a connector is packaging. `MCL` and the two AEL directions remain separate differential links with their own drivers, receivers and terminations; none of them is a channel multiplexed onto another, and an AEL event never becomes a message on `MCL`.
- **One connector, one contact assignment, one cable.** The Module Port is female on every device — Module, Hub Module Port, Hub-to-Hub link port — with the same contact assignment everywhere. The Link Cable crosses AEL OUT to AEL IN, so one non-oriented cable type connects a Module to a Hub, a Module to a Module and a Hub to a Hub; a generic straight-through cable is not compatible, and every port survives one.
- **`MCL` is half duplex on one pair**, RS-485-class, with the Hub as the polling master; that fixes the contact budget at three pairs, a reference and one reserved contact ([Interfaces and Versioning §5.1](./05-interfaces-and-versioning.md#51-transport-bindings)).
- **Hub-less operation is the direct 1:1 link.** Two Modules on one Link Cable exchange AEL events without infrastructure, each managed over its own direct local transport. Three or more Modules in one event exchange use a Module Hub; a chain of Modules is not a Platform topology ([AES-AEL-002](./05-interfaces-and-versioning.md#aes-ael-002-point-to-point-links-direct-and-routed-operation)). The `MCL` pair is idle on that cable by decision, not by omission: a Module is never an `MCL` master ([AES-HUB-005](#aes-hub-005-cascading-and-path-addressing)). This is what preserves direct Module-to-Module operation, test fixtures and adapters to laboratory equipment without a second connector.
- **It carries no power.** No contact of the Module Port carries a Module's primary operating power ([AES-HUB-001](#aes-hub-001-module-hub-scope)).
- **Live insertion is normal.** A Module is connected and disconnected on a running bench: doing so disturbs no other port ([AES-HUB-002](#aes-hub-002-port-independence-and-scale-interoperability)) and produces no valid AEL frame on any link, which the logical idle rule already achieves ([`docs/interfaces/ael.md`](./interfaces/ael.md) Section 4).

Still **open**, and not fixed by this version of AES:

- the **position numbering** of the eight contacts, assigned in the Module Port specification together with the `MCL` binding's electrical profile;
- the **`MCL` binding** — electrical profile, framing, request correlation, flow control, bit rate, turnaround, termination, fail-safe — including the path element width and depth that cascading ([AES-HUB-005](#aes-hub-005-cascading-and-path-addressing)) requires of it;
- the **Link Cable's impedance, conductor size, shield construction and maximum validated length**, and the **crosstalk** limit between the `MCL` pair and the AEL pairs. This last is a requirement of the cable specification, not a detail: `MCL` carries continuous switching traffic while an AEL frame is judged on the timing of its reference instant and on arriving intact, and the two share a cable. Because AEL frames are integrity-protected, crosstalk manifests as counted invalid frames rather than as silent false events — but a lost event is still a lost event, and the isolation needed to keep `MCL` activity out of AEL is characterized and specified before the Module Port reaches `1.0`.

These are resolved together with the `MCL` binding specification, from the bring-up of the first Hub, a Hub-connected Module and a Link Cable. Until then the Module Port is a Draft specification an implementer may build against, and no Module or Hub claims Released conformance to it.

## 8. Guidance (non-normative)

- **Dependency direction.** Units and reusable Controllers should depend on declared interfaces, not on private Module internals. A Unit that needs one Module's undocumented boot timing is not reusable.
- **Keying.** Prefer mechanical, electrical or metadata keying so incompatible installation is impossible or detectable. Users will try invalid combinations.
- **Local extensions.** A Module may define a local, documented, non-portable extension (a debug connector, a temporary protocol). It becomes a Platform interface only when declared and versioned as one — copying an undocumented convention between projects is how accidental pseudo-standards form.
- **Role changes.** If a board changes architectural role (a Controller reused as a standalone Module), update its README and interface declarations to match the new role.
