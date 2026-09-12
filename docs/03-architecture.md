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

A Module's control surface is the [Module Control Interface](./05-interfaces-and-versioning.md#5-module-control-interface) (MCI): the Platform's transport-independent contract for identity, capabilities, lifecycle, configuration, Assets and Sessions. A Module that exposes a Host Interface SHOULD expose it as MCI rather than as a private command set, so that host software, test fixtures and a Module Hub reach every Module the same way. This remains a SHOULD in this version because no MCI transport binding is specified yet ([Interfaces and Versioning §5.1](./05-interfaces-and-versioning.md#51-transport-bindings)); [AES-MOD-002](#aes-mod-002-host-interface-for-released-modules) continues to require only a documented Host Interface. A Module intended for use with a [Module Hub](#7-module-hub) additionally reaches it through a Module Port (§7.1), which does not replace the Module's own local service transport or its standalone SYNC ports.

A Module MAY provide Module Synchronization Interface ports (SYNC IN, SYNC OUT) for deterministic event timing with other Modules. If it does, it follows [Interfaces and Versioning §4](./05-interfaces-and-versioning.md#4-module-synchronization-interface) and the [SYNC specification](./interfaces/sync.md), and its README or design notes list the SYNC IN actions and SYNC OUT sources it supports. SYNC is a Module responsibility: it is never delegated to a Unit or carried on a Unit Interface.

### AES-MOD-003: Unit Compatibility Matrix

**Requirement:** A Released Module that accepts Units SHALL publish a compatibility matrix listing supported Unit Interface Profiles and versions, compatible Unit classes, calibration requirements, and the Module's own Unit-facing electrical limits: how many ports of each profile it provides, what one port supplies, and any restriction on operating those ports simultaneously. During Active Development a running list in the design notes is sufficient.

**Rationale:** Replaceable Units are useful only when compatibility can be determined before installation. A Unit is required to declare what it needs, with numbers ([AES-UNIT-004](#aes-unit-004-declared-limits), [AES-EEPROM-008](./06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)); the matrix is where the other side of that contract is stated. Port count is not a power promise: a Module may expose more ports than it can drive at once, which is a compatibility fact its users need before installation rather than a defect to hide.

### AES-MOD-004: Safety Policy Ownership

**Requirement:** The Module SHALL own safety policy for its complete externally visible function, including Unit behavior, Controller behavior, power limits and Host commands. This applies at every maturity level: even an Experimental Module states its hazards and enforces its own limits.

**Rationale:** Safety emerges from the integrated product, not from any single board. A replaceable Unit's self-declared capability is never a safety authorization (see [AES-EEPROM-007](./06-eeprom-metadata.md#aes-eeprom-007-metadata-trust-model)).

### AES-MOD-002: Host Interface for Released Modules

**Requirement:** Every Released Module with firmware SHALL expose at least one documented Host Interface, unless the Module is purely passive.

**Rationale:** Host Interfaces enable testing, calibration, automation and reproducibility. An undocumented debug UART is not an interface others can build on.

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

A Module is usable on its own. It is also expected to appear on a bench alongside many others that must be discovered, configured, loaded, armed and monitored together — and connecting each one individually to a host stops scaling well before the bench does.

The **AURIORA Module Hub** is the Platform's optional answer: an active-star infrastructure device presenting one **Module Port** per connected Module. It is a composite of three roles that stay separate inside it:

| Role | What it does | Firmware in the path? |
|---|---|---|
| MCL concentrator | Carries [MCI](./05-interfaces-and-versioning.md#5-module-control-interface) between the host and each Module over that Module's `MCL` link; tracks port presence and link state; reports faults. | Yes — managed, with per-port state. |
| SYNC Hub function | Distributes SYNC events to and from the Module Ports, under the SYNC Hub rules ([AES-SYNC-002](./05-interfaces-and-versioning.md#aes-sync-002-point-to-point-links-and-active-fan-out)). | **No.** Static pre-ARM configuration only. |
| SYNC Source (optional) | Originates a SYNC event — on host request, on an upstream input, or on a schedule. | Yes, in *generating* the event; never in distributing it. |

The separation is the design. Management traffic is bursty, queued and tolerant of latency; a SYNC event is a timestamp. Putting the second behind the first's processor would make the Hub's propagation delay a function of its load, which is precisely the property SYNC exists to avoid. That a host-requested event is generated by firmware is not a contradiction: what matters is that every Module receives the resulting edge at the same instant, not how long the request took to arrive.

```text
                              HOST
                               |
                     (host-facing transport)
                               |
                    +----------------------+
                    |     MODULE HUB       |
                    |  MCL concentrator    |  managed
                    |  SYNC Hub function   |  firmware-free event path
                    |  SYNC Source (opt.)  |
                    +----------+-----------+
                               |
          +--------------------+--------------------+
          |                    |                    |
     Module Port 1        Module Port 2        Module Port N
          |                    |                    |
       Module               Module               Module
```

An active star is chosen over a shared multidrop bus for the same reason SYNC links are point-to-point: each port has its own driver, receiver and termination, so its behavior does not depend on how many other Modules happen to be connected, and a fault on one port does not take the bench down.

### AES-HUB-001: Module Hub Scope

**Requirement:** A Module Hub SHALL act as MCI transport infrastructure and SYNC distribution only. It SHALL NOT own, interpret or depend on Module-specific configuration, Session or experiment semantics; it SHALL NOT be the source of a Module's identity ([AES-MCI-002](./05-interfaces-and-versioning.md#aes-mci-002-module-identity)); and it SHALL NOT discover, configure, address or power Units, which remain the responsibility of their parent Module. A Module SHALL remain fully serviceable — commissioning, configuration, firmware update, diagnostics and recovery — through its direct local MCI transport without a Module Hub, and a Module Hub SHALL NOT be a prerequisite for any of those.

**Rationale:** A Hub that must understand each Module type has to be revised whenever a Module is added or its firmware changes, and it becomes the component that blocks the bench. Keeping module-specific meaning in host software and Module firmware — where it already lives — is what lets one Hub design serve Modules that do not exist yet. Reaching Units through a Hub would breach the containment that makes a Module a product contract rather than a wiring point ([EDR-001](./edr/EDR-001-controller-module-separation.md)): a Unit is discovered, validated and powered by its Module under [AES-UNIT-007](#aes-unit-007-deterministic-discovery-and-activation-sequence), and a second authority over that sequence is a safety problem, not a convenience. Recovery is called out separately because infrastructure fails: if the only path to a Module with corrupt firmware runs through a Hub, a Hub fault turns a recoverable Module into a returned one.

### AES-HUB-002: Port Independence and Scale Interoperability

**Requirement:** Each Module Port of a Module Hub SHALL be independently managed: independent link state, independent communication timeout and independent fault handling, such that a fault, disconnection, timeout or unpowered Module on one port does not disturb traffic or SYNC distribution on another. The number of ports SHALL NOT be encoded in MCI, in an MCI transport binding or in the Module Port contract, and the same Module Port contract SHALL apply regardless of a Hub's port count, so that Hubs of different sizes and Modules from different designs remain interoperable. A host SHALL support more than one Module Hub concurrently, and Hubs SHALL be distinguishable from one another.

**Rationale:** Fault containment is the main thing an active star buys over a passive bus, and it is only real if it is a requirement rather than an implementation side effect — one Module with a damaged cable should cost one port, not a run. Leaving port count out of the contracts is what keeps a four-port and a sixteen-port Hub from becoming two incompatible products: a practical reference implementation may settle on eight ports, but eight is a product decision, never a protocol limit. Multi-Hub support follows from the same place: a bench outgrows one Hub long before it outgrows the architecture, and a host that assumes a single Hub has to be rewritten rather than reconfigured.

### 7.1 The Module Port

A Module that is used with a Module Hub reaches it through one **Module Port**: a single connector and cable carrying that Module's `MCL` link together with its SYNC IN and SYNC OUT links. One cable per Module is the preferred physical packaging — it is less to wire, less to mislabel and impossible to cross-connect.

Two things are settled about it:

- **The links stay electrically independent inside it.** Sharing a connector is packaging. `MCL` and the two SYNC directions remain separate differential links with their own drivers, receivers and terminations; none of them is a channel multiplexed onto another, and SYNC never becomes a message on `MCL`.
- **It does not replace the standalone SYNC ports.** A Module keeps its own SYNC IN and SYNC OUT connectors as specified in [`docs/interfaces/sync.md`](./interfaces/sync.md). That is what preserves direct Module-to-Module synchronization without infrastructure, and interoperability with laboratory equipment that consumes the same edge.

Everything physical about it is deliberately **open**, and is not fixed by this version of AES:

- the `MCL` duplex model — one differential pair with direction control, or two pairs with simultaneous transmit and receive — which determines the pair count before anything else can be decided;
- the resulting conductor and contact count, connector family, gender, keying and pinout;
- the cable construction, characteristic impedance and maximum length;
- the reference and shield strategy across the combined cable;
- **crosstalk between the `MCL` pairs and the SYNC pairs.** This is a requirement of the cable specification, not a detail: `MCL` carries continuous switching traffic while a SYNC edge is judged on its timing fidelity, and the two share a cable. The isolation needed to keep `MCL` activity out of SYNC edge timing is characterized and specified before the Module Port is fixed.

These are resolved together with the `MCL` binding specification, from the requirements of the first Hub and a Hub-connected Module — not in advance. Until then a Module Port is an architectural intent, and no Module or Hub claims conformance to one.

## 8. Guidance (non-normative)

- **Dependency direction.** Units and reusable Controllers should depend on declared interfaces, not on private Module internals. A Unit that needs one Module's undocumented boot timing is not reusable.
- **Keying.** Prefer mechanical, electrical or metadata keying so incompatible installation is impossible or detectable. Users will try invalid combinations.
- **Local extensions.** A Module may define a local, documented, non-portable extension (a debug connector, a temporary protocol). It becomes a Platform interface only when declared and versioned as one — copying an undocumented convention between projects is how accidental pseudo-standards form.
- **Role changes.** If a board changes architectural role (a Controller reused as a standalone Module), update its README and interface declarations to match the new role.
