# 02 Terminology

**Document ID:** AES-TERM
**Status:** Normative
**Depends On:** [STANDARD](../STANDARD.md)

## 1. Purpose

This document defines the canonical vocabulary of AURIORA. Canonical definitions appear only here; other documents reference these terms instead of redefining them.

## 2. Canonical Terms

### Platform

The entire AURIORA ecosystem, including engineering standards, Modules, Controllers, Units, interfaces, documentation, manufacturing knowledge, firmware, tooling and release governance.

### Module

A standalone product in the Platform. A Module provides a coherent externally usable function and may contain one or more Controllers, Unit Interfaces and Host Interfaces.

### Controller

A dedicated controller designed for a Module. A Controller implements control, sequencing, safety, acquisition, communication or coordination responsibilities for the Module, but it is not itself the whole Module unless the design explicitly has no separable enclosure, mechanical or replaceable Unit responsibility.

### Unit

A replaceable functional building block connected to a Module. A Unit may provide sensing, stimulation, optical, acoustic, environmental, mechanical, electrical or identity functionality. A Unit SHALL be identifiable electronically when replaceability or compatibility matters (see [Architecture](./03-architecture.md) for the scope of this rule).

A Unit is realized as one of two *execution models* — Passive Unit or Managed Unit (defined in Section 3). These are implementation models of a Unit, not separate top-level objects: both remain Units and use the same vocabulary, identity and interface rules.

### Host Interface

The standard developer and integration interface exposed by Modules. A Host Interface is used by computers, scripts, test systems, data acquisition workflows or developer tools.

### Unit Interface

The standard interface connecting Units to a Module. A Unit Interface includes physical connection, electrical behavior, communication, identity, compatibility and replacement rules. A Unit Interface is realized through one or more versioned Unit Interface Profiles (defined in Section 3); externally visible Unit Interface signals use the `UIF_` prefix ([Interfaces and Versioning](./05-interfaces-and-versioning.md)).

### Product Family

A durable AURIORA engineering family identified by a stable family identifier such as `AAM`, `AAC`, `APEM` or `APBM`. A Product Family defines engineering identity, design scope, ownership, lifecycle and compatibility expectations across Products, revisions and manufacturing instances.

## 3. Supporting Terms

| Term | Definition |
|---|---|
| Passive Unit | A Unit execution model in which the Unit has no independently executing application firmware; the host Module drives the Unit's sensors, actuators, converters or other functional circuits directly through the Unit Interface. A Passive Unit is not required to contain a microcontroller. |
| Managed Unit | A Unit execution model in which the Unit contains one or more programmable controllers and exposes a versioned, high-level Unit API. The host Module operates the Unit through that API and is not required to know or control the Unit's internal components, register-level interfaces or radio/GNSS/sensor configuration. The model does not imply a transport: a Managed Unit may use an I²C or an SPI Unit Interface Profile. |
| Unit API | The versioned, high-level application interface a Managed Unit exposes to its host Module: capabilities, operations, status and errors — not internal component types or register-level protocols. |
| Unit Interface Host | Whatever implements the host side of a Unit Interface port. Normally a Module, but also an adapter, test fixture or third-party host that implements the published profile and Unit API. Unit Interface obligations bind the Unit Interface Host; product-level safety policy remains a Module responsibility. |
| AURIORA Event Link (AEL) | The Module-level interface that carries deterministic *typed events* between Modules: a point-to-point differential link carrying a small, fixed four-byte, integrity-protected event frame whose only semantic content is a numeric event identifier — no command, address, payload or timestamp. Works directly Module-to-Module or through an AEL router. Not part of the Unit Interface. Defined in [Interfaces and Versioning §4](./05-interfaces-and-versioning.md#4-auriora-event-link) and [`docs/interfaces/ael.md`](./interfaces/ael.md). |
| AEL event | One AEL event frame: "configured event *N* occurred now", where *N* is the event identifier. Its consequence is defined by the receiving Module's receive bindings and state, and its meaning to the experiment by the deployment record — never by the frame beyond the identifier. |
| AEL event identifier | The 16-bit unsigned value carried in an AEL event frame. Allocated by the host per deployment, unique per logical event source within the active AEL routing domain, decoded through the deployment record; `0x0000` is reserved as invalid/unbound. AES assigns no Platform-wide meaning to any value. |
| AEL routing domain | The set of AEL endpoints — Module ports and router ports — interconnected by active AEL links and routes during one deployment. The scope within which event identifiers are unique. |
| AEL router | The event-routing function of a Module Hub, or a standalone AEL Hub: receives a complete frame, validates it, and forwards it unchanged onto the outputs selected by a committed route table keyed by ingress port and event identifier. Knows ports, identifiers and routes; never what an identifier means. Store-and-forward, with a published timing contract. |
| AEL event source | A device role that *originates* an AEL event from one of its event source bindings rather than forwarding a received one. A Module's AEL OUT is an event source; a Module Hub MAY act as one — for a host-requested `T0` or a scheduled marker — in addition to routing. Origination and routing are distinct roles. |
| AEL receive binding | Module configuration mapping an event identifier to a configured action — for example start a Session, insert a marker, change phase — together with the Module Lifecycle States in which the binding is enabled. AES defines the mechanism; the supported actions are Module-specific. |
| AEL event source binding | Module configuration mapping a defined internal event — the actual occurrence, such as a detector crossing or a protocol phase start — to the event identifier emitted on AEL OUT. The identifier's meaning exists in the bindings and the deployment record, not on the wire. |
| Hub-to-Hub AEL link | An AEL link between two AEL routers, carrying the unchanged event frame so events can be routed across more than one Module Hub. The topology formed by these links is acyclic in this version. Independent of `MCL` cascading, which remains open. |
| Module Control Interface (MCI) | The Platform's transport-independent Module control contract: the identity, capability, lifecycle, configuration, asset and session semantics a host uses to manage a Module. MCI is the AURIORA realization of the Host Interface. It defines *meaning* — never framing, timing or electrical behavior — and is carried by one or more MCI transport bindings. Defined in [Interfaces and Versioning §5](./05-interfaces-and-versioning.md#5-module-control-interface). |
| MCI transport binding | A versioned specification of how MCI is carried over one transport: framing, request correlation, error signaling, flow control and, where the transport is a physical link, its electrical layer. A binding defines carriage only; it SHALL NOT change the meaning of an MCI operation. A direct local transport such as USB and the Module Control Link are bindings of the same MCI. |
| Module Control Link (MCL) | The AURIORA wired differential MCI transport binding between a Module and a Module Hub: point-to-point, one link per Module Port. Its duplex model, electrical layer, connector and framing are not fixed in this version of AES. |
| Module Port | The Module-side connector through which a Module Hub reaches one Module, carrying that Module's MCL together with its AEL IN and AEL OUT links in one cable. Connector, pinout, pair count and cable are open items. A Module Port does not replace a Module's standalone AEL ports. |
| Module Hub | Optional Platform infrastructure: an active-star device presenting one Module Port per connected Module. It combines a managed MCL concentrator with an AEL router and, optionally, an AEL event source. It carries MCI and routes AEL events without interpreting Module-specific experiment semantics, and it does not reach Units. |
| Module Lifecycle State | The Module-level state a host observes and advances over MCI: `IDLE → CONFIGURED → ARMED → RUNNING → COMPLETE`. `ARMED` is the boundary between preparation over MCI and deterministic execution on AEL; which AEL receive bindings are enabled in `ARMED` and in `RUNNING` is per-binding configuration. A reset always begins in `IDLE`; execution is re-entered afterwards only through the validated recovery procedure of [AES-MCI-007](./05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance), never by restoring a remembered state. Firmware MAY use its own state names; the states and the boundary are what the contract fixes. |
| Asset | A reusable content object held by a Module and referenced by its configuration or its sessions — waveform data, lookup tables, calibration resources, stimulus patterns. An Asset is identified and verified by its content, so a host can determine whether a transfer is needed at all. |
| Session | A named, executable Module configuration — a protocol, experiment definition or stimulus/acquisition program — that a host transfers, selects and arms. Session support is a declared Module capability, not a Platform-wide obligation: not every Module needs one. A Session defines *what* the Module executes; how it is operated in a particular installation — on host loss, after a reset, when storage is exhausted — is the deployment policy, not part of the Session. |
| Autonomous continuation | A declared Module capability: the Module continues an `ARMED` or `RUNNING` Session to its defined end — its local schedule, its bound actions, its Units and its data handling — without a connected host or Module Hub, and preserves the outcome for later readout. Whether it does so in a given installation is set by the deployment policy. Defined in [Interfaces and Versioning §5](./05-interfaces-and-versioning.md#5-module-control-interface) ([AES-MCI-006](./05-interfaces-and-versioning.md#aes-mci-006-autonomous-continuation-and-deployment-policy)). |
| Deployment policy | The explicitly configured, Module-held behavior that governs how a prepared Session is operated in one installation rather than what the Session does: what the Module does on host loss, after a reset, and when its storage is exhausted. Configured over MCI only from the behaviors the Module declares, read back, and recorded in the host's deployment record. Distinct from Module configuration and from the Session. |
| Persistent deployment state | The integrity-protected non-volatile record a Module holds of its active deployment — the identities and integrity values of its configuration, selected Session, required Assets and bindings, the deployment policy, run and run segment identity, recovery count and last lifecycle state — which is validated after a reset before it may authorize any recovery ([AES-MCI-007](./05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance)). Its format is an implementation detail; its content is a contract. |
| Run segment | One contiguous, physically uninterrupted part of a run — one execution of a Session. A run begins with segment 0; each authorized recovery after a reset begins a new segment. A segment boundary, its cause and its time discontinuity are recorded, so that a reset is never hidden in the experiment record. |
| Unit Interface Profile | A versioned realization of the Unit Interface with a defined connector, pinout, signal set and electrical/timing behavior (for example `UIF-I2C-6`, `UIF-MI2C-8`, `UIF-MSPI-14`). Multiple profiles may exist concurrently; each is versioned independently. The profile is selected by transport requirements and is independent of the Unit's execution model. |
| Artifact | Any designed object governed by AES, including hardware, firmware, documents, tools and release packages. |
| Family Identifier | A short stable AURIORA architectural identifier assigned to a Product Family and used across documents, PCB markings, firmware, repositories and manufacturing. |
| Product | A released or release-intended realization within a Product Family. |
| Product Revision | A controlled design revision of a Product, such as a hardware, firmware, mechanical or documentation revision. |
| Manufacturing Instance | One physical produced item identified by serial number and production records. |
| Object Identifier (AOID) | A stable machine-readable AES identifier assigned to a design family, interface family or document family. |
| Requirement Identifier | A stable identifier assigned to a normative AES rule (`AES-<AREA>-<NNN>`). |
| Compatibility Class | A declared promise about electrical, mechanical, firmware, protocol, documentation or manufacturing interoperability. |
| Calibration Record | Traceable data linking a physical artifact to measured correction, tolerance or characterization information. |
| Manufacturing Package | Immutable release set required to reproduce a hardware artifact. |
| Maturity Level | The declared state of an artifact: Experimental, Active Development, Released, Deprecated or Retired (see [STANDARD](../STANDARD.md#3-maturity-model)). |

## 4. Normative Requirements

### AES-TERM-001: Vocabulary Preservation

**Requirement:** AES documents and conformant engineering artifacts SHALL use `Platform`, `Module`, `Controller`, `Unit`, `Host Interface`, `Unit Interface` and `Product Family` with the meanings defined in this document. Aliases MAY exist for user-facing material but SHALL be marked non-canonical.

**Rationale:** Renaming foundational objects fragments the ecosystem and makes old and new documents harder to reconcile.

### AES-TERM-003: Frozen Core Vocabulary

**Requirement:** The terms in Section 2 are frozen core vocabulary. Changes to their meaning, spelling or canonical status SHALL require an Engineering Decision Record.

**Rationale:** These terms define the mental model used in every AURIORA design discussion. Changing them casually would make earlier documents and manufacturing evidence harder to interpret.
