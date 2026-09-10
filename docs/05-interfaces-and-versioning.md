# 05 Interfaces and Versioning

**Document ID:** AES-IF
**Status:** Normative
**Depends On:** [Architecture](./03-architecture.md), [Naming and Identity](./04-naming-and-identity.md)
**Supersedes:** AES-VER (Versioning Standard), AES-EVO (Platform Evolution Strategy)

## 1. Purpose

This chapter defines Host Interface and Unit Interface rules, versioning and compatibility evolution.

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
- profile-defined synchronization or auxiliary signals

Physical presence is determined through successful EEPROM discovery, not through a dedicated presence pin. A Unit-presence signal (`UIF_PRESENT`, `UIF_PRESENT_N` or equivalent) SHALL NOT be defined; the connector SHALL NOT require separate discovery and functional power pins — the Unit locally switches or enables the power of its functional circuitry from `UIF_PWR_EN`.

`UIF_READY` is an **active-HIGH** functional-readiness signal:

- **LOW:** the Unit is disabled, starting, not initialized, faulty, or otherwise unavailable.
- **HIGH:** the Unit is powered, initialized, and its functional interface is ready for use.

For a Passive Unit, `UIF_READY` MAY be generated from the switched functional power domain (hardware pull-up or equivalent). For a Managed Unit, `UIF_READY` SHOULD be controlled by the Unit controller and asserted only after successful firmware initialization, and deasserted before shutdown or on entering an unrecoverable fault. The host MUST provide a defined LOW state when no Unit is connected or the Unit functional domain is disabled. `UIF_READY` is a readiness signal, not a physical-presence signal.

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

## 4. Compatibility

Compatibility claims about Released artifacts name what they cover — electrical, mechanical, firmware, protocol, documentation, manufacturing — and the version range: `Electrical and protocol compatible with UIF 1.1; mechanical incompatible without adapter`, not "compatible with APEM". Unqualified "compatible" is a support case waiting to happen. For prototypes, a compatibility note in the design notes suffices.

## 5. Evolution

### AES-EVO-002: Prefer Additive Evolution

**Requirement:** Interface, EEPROM and API evolution SHOULD prefer additive optional fields, capability flags and minor versions before breaking changes. When a break is necessary, it SHALL be versioned as a major change with migration guidance (adapter, dual support or explicit incompatibility).

**Rationale:** Installed hardware and published open designs cannot be updated like software libraries.

### AES-EVO-003: Deprecation With Migration

**Requirement:** Deprecating a Released interface, schema or artifact SHALL include reason, replacement path (or an explicit statement that none is feasible), affected versions and known risks. Retired contracts SHALL remain documented — reachable through tags or archives — with final supported version and reason for retirement.

**Rationale:** Old hardware still exists; deprecation without migration turns Platform artifacts into traps, and deleting interface history makes safety review impossible.

Breaking changes to Released interfaces additionally require a decision record — see [Decisions and Governance](./08-decisions-and-governance.md).

## 6. Guidance (non-normative)

- Test fixtures or procedures that verify identity discovery, error behavior and compatibility decisions are strongly recommended for Released Unit Interfaces — interface documents without tests drift from implementations.
- Documentation-only changes (typo, clarified example) are PATCH; manufacturing-only changes (approved substitution, process change) update the manufacturing package version and rerun affected tests; interface changes update the interface version even when the implementation diff is small.
