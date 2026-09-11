# 05 Interfaces and Versioning

**Document ID:** AES-IF
**Status:** Normative
**Depends On:** [Architecture](./03-architecture.md), [Naming and Identity](./04-naming-and-identity.md)
**Supersedes:** AES-VER (Versioning Standard), AES-EVO (Platform Evolution Strategy)

## 1. Purpose

This chapter defines Host Interface and Unit Interface rules, the Module Synchronization Interface, versioning and compatibility evolution.

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
- profile-defined synchronization or auxiliary signals — Unit-to-host signals within one Module; the Module-to-Module SYNC interface of Section 4 is not a `UIF_` signal

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

## 4. Module Synchronization Interface

The **AURIORA Module Synchronization Interface (SYNC)** provides deterministic event synchronization between Modules. SYNC carries no command, address, payload or event identifier. It represents a precisely timed external event. The receiving Module determines the action associated with that event from its local configuration and current state.

The dividing line in one sentence: **control interfaces define *what* a Module does; SYNC defines *when* the configured action or event occurs.** Its complement on the output side: **SYNC OUT reports *when* a configured internal Module event occurred; the meaning of the pulse lives in the Module configuration and event log, not in the electrical signal.**

SYNC is a **Module-level** interface. It connects Modules to Modules, or a Module to external laboratory equipment that consumes the same edge. It is not part of the Unit Interface: Units are internal building blocks of a Module and neither expose nor receive Module SYNC. The profile-defined synchronization signals a Unit Interface Profile may carry (§3.1) are Unit-to-host signals inside one Module and are unrelated to SYNC. SYNC does not replace, extend or forward to any `UIF_` signal.

SYNC is deliberately not a communication protocol. It has no baud rate, framing, addressing, command codes, checksum or message structure; it is a digital event pulse. Its physical layer uses RS-422-compatible differential signaling, but SYNC is not an RS-422 protocol, and it is not described as a "SYNC protocol", a "SYNC command" or a "trigger bus". The physical, electrical and timing specification is the versioned [SYNC interface specification](./interfaces/sync.md); this section defines the interface-independent rules.

### 4.1 Topology

The normal SYNC link is one **SYNC OUT** driving one **SYNC IN**: a point-to-point differential link.

```text
Module A SYNC OUT ──────────────► Module B SYNC IN
```

Where one source must synchronize several Modules, an active **SYNC Hub** regenerates one input event onto several independent outputs, each a separate point-to-point link:

```text
                         ┌──► Module #1 SYNC IN
                         ├──► Module #2 SYNC IN
SYNC SOURCE ─► SYNC HUB ─┼──► Module #3 SYNC IN
                         └──► Module #4 SYNC IN
```

The Hub is transparent: it does not encode information, decide the meaning of the event or act as a timing master. It introduces a finite, characterized delay. Hubs may be cascaded; delays accumulate and each stage remains point-to-point.

### AES-SYNC-001: SYNC Is a Module-Level Event Interface

**Requirement:** A Module that provides event synchronization with other Modules SHALL do so through the Module Synchronization Interface as specified in [`docs/interfaces/sync.md`](./interfaces/sync.md). A SYNC signal SHALL carry only the occurrence and timing of an event: no command, address, parameter, event type, payload or identifier. Meaning SHALL NOT be assigned to pulse width, pulse count, pulse spacing or polarity beyond the single defined event edge; a Module that needs to convey commands or data SHALL use a Host Interface or another declared control interface. SYNC SHALL NOT be part of any Unit Interface Profile, and a Unit SHALL NOT expose or consume Module SYNC.

**Rationale:** A single-meaning event edge is the only thing that stays unambiguous when pulses are lost, when receivers are in different states, and when the line is observed by an instrument that knows nothing about the sender. The moment width or count carries meaning, SYNC becomes an undocumented protocol with the failure modes of one and none of the framing. Keeping it out of the Unit Interface keeps the Module the single owner of its external timing behavior ([AES-MOD-004](./03-architecture.md#aes-mod-004-safety-policy-ownership)).

### AES-SYNC-002: Point-to-Point Links and Active Fan-Out

**Requirement:** A SYNC link SHALL connect exactly one SYNC OUT to exactly one SYNC IN over a differential pair. Passive multidrop wiring, passive splitters and daisy-chaining through a Module SHALL NOT be the means of reaching several receivers; fan-out SHALL be performed by an active SYNC Hub that regenerates the event onto independent outputs. A SYNC Hub SHALL NOT alter, filter, interpret or add information to the event, and SHALL document its input-to-output propagation delay and channel-to-channel skew. A receiving Module SHALL terminate its own SYNC IN; a Module or Hub output SHALL NOT be terminated as a receiver.

**Rationale:** A point-to-point link has one driver, one receiver and one termination, so its timing is predictable and a fault on one link cannot disturb another. A Hub built from the same transceiver class as the Modules keeps the whole system on one electrical contract. Delay is documented rather than denied: a Hub is not zero-delay, and a high-precision experiment needs the number.

### AES-SYNC-003: Event Binding, Arming and Default Behavior

**Requirement:** A Module with a SYNC IN SHALL define a configurable **SYNC IN action** — the action executed when a valid SYNC event arrives — and SHALL execute it only when the Module is **armed** for it and the action is valid in the Module's current state. A SYNC event that arrives while the Module is not armed, or while a triggered run is still in progress, SHALL NOT execute, restart, stop, advance or queue the configured action unless the Module has been explicitly configured to do so; the default is to ignore the event and record it. Post-completion behavior — return to idle, or re-arm — SHALL be an explicit, visible configuration, not an implicit default. A Module with a SYNC OUT SHALL generate its pulse from a configured **SYNC OUT source**, a defined internal event such as the start or end of a protocol or acquisition, and SHALL NOT forward SYNC IN to SYNC OUT unless that forwarding is itself the configured source. Where a Module supports more than one SYNC OUT source at the same time, the active binding SHALL be explicit in its configuration and documented as an advanced feature, since a receiver cannot distinguish the pulses. A configurable, deterministic delay between the SYNC event and the action MAY be provided; the delay is Module configuration, not information carried by SYNC. The actions and sources a Module supports are Module-specific and are documented with the Module; this requirement defines the mechanism, not the list.

**Rationale:** A Module that reacts to any pulse on its input is a Module whose experiment can be started by a stray edge. Arming makes the trigger a two-step act — configure, then wait — which is what makes experiments reproducible and lets an ignored pulse be a logged fact rather than a mystery. Binding SYNC OUT to the actual internal event, rather than to reception of the trigger or receipt of a command, is what makes the output pulse a usable timestamp of what physically happened.

### AES-SYNC-004: SYNC Observability

**Requirement:** A Module with firmware and a Host Interface that provides SYNC SHALL record SYNC events in its event log: at minimum received, transmitted and ignored events, each with a local timestamp, the Module state at the time, the reason when ignored, the related run or protocol identifier where one exists, and a local per-direction event counter. Counters are local to the Module, are not transmitted over SYNC, and SHALL NOT be presented as synchronized between Modules. The active SYNC IN action, SYNC OUT source, delay and post-completion mode SHALL be readable through the Host Interface. During Experimental work a reduced log is acceptable; a Released Module SHALL provide the full set.

**Rationale:** Two Modules' logs are the only place where the meaning of a pulse train can be reconstructed: the sender's log says which internal event produced each pulse, the receiver's log says what it did with it. Comparing local counters across a run is the cheapest way to detect a lost event on one path. Without configuration readback an experiment cannot be reproduced from its records.

### 4.2 Guidance (non-normative)

- **Baseline behavioral model.** `IDLE → CONFIGURED → ARMED → RUNNING → COMPLETE`, with `COMPLETE → IDLE` (one-shot) or `COMPLETE → ARMED` (repeat-armed) as the two post-completion modes. Firmware may use its own state names; what matters is that the armed gate and the completion choice exist and are visible.
- **Two usage modes.** *Trigger*: Module A's `SYNC OUT source = PROTOCOL_START` drives Module B's `SYNC IN action = START_PROTOCOL`. *Marker*: a continuously recording Module binds `SYNC IN action = INSERT_MARKER` and stamps each event into its acquisition timeline; the sender's log later says which marker was which.
- **Timing budget.** Distinguish cable propagation, transceiver delay, Hub delay, firmware reaction latency and the latency of the physical action. Capture the event edge as close to hardware as practical and characterize the rest. Implementation guidance is in the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §5.1 and the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) §14.2.
- A worked trigger-and-marker example is [Worked Example: Module Synchronization](../examples/worked-example-module-synchronization.md).

## 5. Compatibility

Compatibility claims about Released artifacts name what they cover — electrical, mechanical, firmware, protocol, documentation, manufacturing — and the version range: `Electrical and protocol compatible with UIF 1.1; mechanical incompatible without adapter`, not "compatible with APEM". Unqualified "compatible" is a support case waiting to happen. For prototypes, a compatibility note in the design notes suffices.

## 6. Evolution

### AES-EVO-002: Prefer Additive Evolution

**Requirement:** Interface, EEPROM and API evolution SHOULD prefer additive optional fields, capability flags and minor versions before breaking changes. When a break is necessary, it SHALL be versioned as a major change with migration guidance (adapter, dual support or explicit incompatibility).

**Rationale:** Installed hardware and published open designs cannot be updated like software libraries.

### AES-EVO-003: Deprecation With Migration

**Requirement:** Deprecating a Released interface, schema or artifact SHALL include reason, replacement path (or an explicit statement that none is feasible), affected versions and known risks. Retired contracts SHALL remain documented — reachable through tags or archives — with final supported version and reason for retirement.

**Rationale:** Old hardware still exists; deprecation without migration turns Platform artifacts into traps, and deleting interface history makes safety review impossible.

Breaking changes to Released interfaces additionally require a decision record — see [Decisions and Governance](./08-decisions-and-governance.md).

## 7. Guidance (non-normative)

- Test fixtures or procedures that verify identity discovery, error behavior and compatibility decisions are strongly recommended for Released Unit Interfaces — interface documents without tests drift from implementations.
- Documentation-only changes (typo, clarified example) are PATCH; manufacturing-only changes (approved substitution, process change) update the manufacturing package version and rerun affected tests; interface changes update the interface version even when the implementation diff is small.
