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

### AES-MOD-003: Unit Compatibility Matrix

**Requirement:** A Released Module that accepts Units SHALL publish a compatibility matrix listing supported Unit Interface versions, compatible Unit classes, electrical limits and calibration requirements. During Active Development a running list in the design notes is sufficient.

**Rationale:** Replaceable Units are useful only when compatibility can be determined before installation.

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

### AES-UNIT-001: Electronic Identity

**Requirement:** A Released replaceable Unit whose replacement affects electrical behavior, data interpretation, safety, calibration or compatibility SHALL provide electronic identity using the [AES EEPROM metadata specification](./06-eeprom-metadata.md) or a documented equivalent. Experimental and passive Units are exempt; Active Development Units SHOULD design the identity in early, because it is hard to retrofit.

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

## 6. Guidance (non-normative)

- **Dependency direction.** Units and reusable Controllers should depend on declared interfaces, not on private Module internals. A Unit that needs one Module's undocumented boot timing is not reusable.
- **Keying.** Prefer mechanical, electrical or metadata keying so incompatible installation is impossible or detectable. Users will try invalid combinations.
- **Local extensions.** A Module may define a local, documented, non-portable extension (a debug connector, a temporary protocol). It becomes a Platform interface only when declared and versioned as one — copying an undocumented convention between projects is how accidental pseudo-standards form.
- **Role changes.** If a board changes architectural role (a Controller reused as a standalone Module), update its README and interface declarations to match the new role.
