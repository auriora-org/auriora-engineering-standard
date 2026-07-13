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
