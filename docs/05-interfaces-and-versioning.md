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
- `UIF_SPI_SCK`, `UIF_SPI_MOSI`, `UIF_SPI_MISO`, `UIF_SPI_CS_N` — Managed Unit SPI transport
- `UIF_IRQ_N`, `UIF_RESET_N` — interrupt and reset
- profile-defined synchronization or auxiliary signals

Physical presence is determined through successful EEPROM discovery, not through a dedicated presence pin. A Unit-presence signal (`UIF_PRESENT`, `UIF_PRESENT_N` or equivalent) SHALL NOT be defined; the connector SHALL NOT require separate discovery and functional power pins — the Unit locally switches or enables the power of its functional circuitry from `UIF_PWR_EN`.

`UIF_READY` is an **active-HIGH** functional-readiness signal:

- **LOW:** the Unit is disabled, starting, not initialized, faulty, or otherwise unavailable.
- **HIGH:** the Unit is powered, initialized, and its functional interface is ready for use.

For a Passive Unit, `UIF_READY` MAY be generated from the switched functional power domain (hardware pull-up or equivalent). For a Managed Unit, `UIF_READY` SHOULD be controlled by the Unit controller and asserted only after successful firmware initialization, and deasserted before shutdown or on entering an unrecoverable fault. The host MUST provide a defined LOW state when no Unit is connected or the Unit functional domain is disabled. `UIF_READY` is a readiness signal, not a physical-presence signal.

A Unit Interface is realized through one or more versioned **Unit Interface Profiles**. Rather than forcing every Unit onto one universal connector, the Platform supports multiple profiles (for example a small I²C profile for Passive Units and a larger profile for Managed Units), each versioned independently. Concrete connector pinouts, electrical limits and timing live in the versioned profile specifications under [`docs/interfaces/`](./interfaces/); this chapter defines only the profile-independent rules.

### AES-IF-008: Versioned Unit Interface Profiles

**Requirement:** A standardized Unit Interface SHALL be defined as one or more named, independently versioned Unit Interface Profiles, each specifying its connector, pinout, `UIF_` signal set, electrical limits and timing in a versioned profile specification. A Released Unit and its host SHALL declare the profile identifier and profile version they implement (see [EEPROM Metadata](./06-eeprom-metadata.md)), and a host SHALL reject a Unit whose profile or profile version it does not support, leaving `UIF_PWR_EN` LOW. Profiles version per the semantic rules of this chapter; changing a profile's defined signals is a breaking change unless it resolves a documented electrical conflict without altering existing signal meaning.

**Rationale:** Different Unit classes have genuinely different connector needs; one universal connector either over-provisions simple Units or under-serves complex ones. Independent versioning lets each profile evolve without forcing a Platform-wide connector change, while explicit profile declaration keeps incompatible Units from being powered.

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
