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

### Host Interface

The standard developer and integration interface exposed by Modules. A Host Interface is used by computers, scripts, test systems, data acquisition workflows or developer tools.

### Unit Interface

The standard interface connecting Units to a Module. A Unit Interface includes physical connection, electrical behavior, communication, identity, compatibility and replacement rules.

### Product Family

A durable AURIORA engineering family identified by a stable family identifier such as `AAM`, `AAC`, `APEM` or `APBM`. A Product Family defines engineering identity, design scope, ownership, lifecycle and compatibility expectations across Products, revisions and manufacturing instances.

## 3. Supporting Terms

| Term | Definition |
|---|---|
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
