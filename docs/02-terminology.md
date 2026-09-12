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
| Module Synchronization Interface (SYNC) | A Module-level interface that conveys the *timing* of an event between Modules and nothing else: a point-to-point, RS-422-compatible differential link carrying a single-meaning event edge, with no command, address, payload or identifier. Not part of the Unit Interface. Defined in [Interfaces and Versioning §4](./05-interfaces-and-versioning.md#4-module-synchronization-interface) and the [SYNC specification](./interfaces/sync.md). |
| SYNC event | The rising edge on a SYNC link, meaning only "an external synchronization event occurred now". Its consequence is defined by the receiving Module's configuration and state, never by the pulse. |
| SYNC Hub | An active, controller-less fan-out device that regenerates one SYNC event onto several independent point-to-point SYNC outputs without altering or interpreting it. |
| SYNC Source | A device role that *originates* a SYNC event rather than regenerating a received one. A Module's SYNC OUT is a SYNC Source; a Module Hub MAY act as one in addition to its fan-out role. The two roles are distinct: a SYNC Hub never originates an event. |
| SYNC IN action | The Module-configured action executed when a valid SYNC event arrives while the Module is armed for it — for example start a protocol or insert a marker. AES defines the mechanism; the supported set is Module-specific. |
| SYNC OUT source | The Module-configured internal event whose occurrence generates a SYNC OUT pulse — for example protocol start or acquisition start. The pulse's meaning exists in the configuration and the event log, not on the wire. |
| Module Control Interface (MCI) | The Platform's transport-independent Module control contract: the identity, capability, lifecycle, configuration, asset and session semantics a host uses to manage a Module. MCI is the AURIORA realization of the Host Interface. It defines *meaning* — never framing, timing or electrical behavior — and is carried by one or more MCI transport bindings. Defined in [Interfaces and Versioning §5](./05-interfaces-and-versioning.md#5-module-control-interface). |
| MCI transport binding | A versioned specification of how MCI is carried over one transport: framing, request correlation, error signaling, flow control and, where the transport is a physical link, its electrical layer. A binding defines carriage only; it SHALL NOT change the meaning of an MCI operation. A direct local transport such as USB and the Module Control Link are bindings of the same MCI. |
| Module Control Link (MCL) | The AURIORA wired differential MCI transport binding between a Module and a Module Hub: point-to-point, one link per Module Port. Its duplex model, electrical layer, connector and framing are not fixed in this version of AES. |
| Module Port | The Module-side connector through which a Module Hub reaches one Module, carrying that Module's MCL together with its SYNC IN and SYNC OUT links in one cable. Connector, pinout, pair count and cable are open items. A Module Port does not replace a Module's standalone SYNC ports. |
| Module Hub | Optional Platform infrastructure: an active-star device presenting one Module Port per connected Module. It combines a managed MCL concentrator with a SYNC Hub function and, optionally, a SYNC Source. It carries MCI without interpreting Module-specific experiment semantics, and it does not reach Units. |
| Module Lifecycle State | The Module-level state a host observes and advances over MCI: `IDLE → CONFIGURED → ARMED → RUNNING → COMPLETE`. `ARMED` is the boundary between preparation over MCI and deterministic execution on SYNC. Firmware MAY use its own state names; the states and the boundary are what the contract fixes. |
| Asset | A reusable content object held by a Module and referenced by its configuration or its sessions — waveform data, lookup tables, calibration resources, stimulus patterns. An Asset is identified and verified by its content, so a host can determine whether a transfer is needed at all. |
| Session | A named, executable Module configuration — a protocol, experiment definition or stimulus/acquisition program — that a host transfers, selects and arms. Session support is a declared Module capability, not a Platform-wide obligation: not every Module needs one. |
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
