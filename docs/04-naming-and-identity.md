# 04 Naming and Identity

**Document ID:** AES-NAME
**Status:** Normative
**Depends On:** [Terminology](./02-terminology.md)
**Supersedes:** AES-ID (Identifier Standard), AES-DOCID (Document Identifier Standard)

## 1. Purpose

This chapter defines AURIORA naming and identity: family identifiers, public names, product numbers, revisions, serial numbers, object identifiers (AOIDs) and document IDs.

The core idea: names communicate to humans; identifiers provide durable machine-readable identity; the two are kept separate; and identity becomes stable exactly when other artifacts start depending on it.

## 2. Identity Levels

| Level | Identifies | Example | Changes when |
|---|---|---|---|
| Product Family | Durable engineering family | `APEM` | A new architectural family is created. |
| Product | A release-intended product within a family | `APEM-01` | A distinct product contract is created. |
| Product Revision | A controlled design revision | `APEM-01 Rev B`, firmware `1.3.0` | Design changes under the same product contract. |
| Manufacturing Instance | One physical produced item | `ASER-APEM-2026-A03-00042` | Each physical item is produced. |

### AES-ID-001: Identity Level Separation

**Requirement:** AURIORA artifacts SHALL keep Product Family, Product, Product Revision and Manufacturing Instance identity separate. A lower-level identifier SHALL NOT substitute for a higher-level identity (no `APEMB` family because Rev B exists; no serial number as product identity).

**Rationale:** These levels answer different engineering questions; mixing them breaks traceability and compatibility review.

## 3. Family Identifiers

Family identifiers such as `AAM`, `AAC`, `APEM` and `APBM` are architectural identities, not casual abbreviations. They appear on PCB markings, in firmware, documentation, repositories and manufacturing records.

### AES-NAME-001: Family Identifier Stability

**Requirement:** Every Product Family SHALL have a family identifier of 3–6 uppercase ASCII letters that encodes durable architectural meaning — never revision, supplier, chip, color, engineer or batch. Public AURIORA families SHOULD begin with `A`. Before Release a family identifier MAY change; after any artifact of the family is Released it SHALL NOT change, and a deprecated or retired family identifier SHALL NOT be reused, except through a formal migration recorded in an EDR.

**Rationale:** Old hardware, manuals and calibration records cannot be renamed. Encoding transient details creates false identity changes.

Guidance: derive new identifiers from 2–4 durable words (`AURIORA` + `Plant` + `Electrophysiology` + `Module` → `APEM`), check the [Document Index](./document-index.md) and existing repositories for collisions, and note the derivation in the family's README. The prefixes `AX`, `AT`, `AR`, `AD` and `AZ` remain informally reserved for experimental, tooling, archival, deprecated-bridge and future governance use.

## 4. Public Names

### AES-NAME-009: Public Name Semantics

**Requirement:** Public descriptive names of Released artifacts SHALL use the AURIORA brand and the canonical role word (`AURIORA <Durable Function> Module | Controller | Unit`; interfaces end in `Host Interface` or `Unit Interface`), and SHALL NOT encode revision, supplier, chip, enclosure generation or temporary project codes.

**Rationale:** Public names enter documentation, labels and search; transient details in names become false after normal evolution. Working titles during Experimental and Active Development are unrestricted.

Repository names are lowercase kebab-case and should include the family identifier when family-specific (`auriora-apem`, `auriora-apem-firmware`).

## 5. Product Numbers and Revisions

- Products within a family use `<FAMILY-ID>-<NN>` (`APEM-01`), assigned by the maintainer when a product contract becomes real — typically at the start of Active Development toward release. Product numbers never encode revision, firmware version, batch or serial.
- Hardware revisions use `Rev <LETTER>`. Firmware, interfaces, documents and manufacturing packages version per [Interfaces and Versioning](./05-interfaces-and-versioning.md).

### AES-ID-008: Serial Numbers

**Requirement:** Physical Released artifacts SHALL carry a serial number formatted `ASER-<FAMILY-ID>-<YYYY>-<BATCH>-<NNNNN>` or a documented equivalent preserving family, year, batch and sequence. Prototypes MAY use any honest marking (including a handwritten number) as long as it cannot be mistaken for a production serial.

**Rationale:** Serial numbers identify physical instances for manufacturing and calibration traceability.

## 6. Object Identifiers (AOIDs)

AOIDs give machine-readable identity to design families where tooling, EEPROM metadata or manifests need it:

```text
AOID:<NAMESPACE>:<CLASS>:<DOMAIN>:<FAMILY>:<SERIES>
```

- **Namespace:** `PUB` (public), `INT` (internal), `EXP` (experimental), `DEP`/`RET` (deprecated/retired), `TST` (test fixtures).
- **Class:** `FAM`, `PROD`, `MOD`, `CTRL`, `UNIT`, `HIF`, `UIF`, `DOC`, `TOOL`, `PKG` and similar.
- **Domain:** broad codes such as `GEN`, `MEAS`, `STIM`, `CTRL`, `ENV`, `BIO`, `OPT`, `ACOU`, `MECH`, `DATA`, `MFG`.
- **Family:** the registered family identifier. **Series:** three-digit sequence.

Example: `AOID:PUB:UNIT:MEAS:AAC:001`.

### AES-ID-006: AOID Assignment

**Requirement:** Every Released artifact that participates in machine-readable identity — a Unit carrying EEPROM metadata, a versioned Host or Unit Interface contract, a manufacturing package referenced by records — SHALL have an AOID, frozen at Release, using `PUB` namespace unless deprecated or retired. Experimental and internal artifacts do not need AOIDs; when they use one anyway, they SHALL NOT use the `PUB` namespace.

**Rationale:** Names and repositories move; identity baked into EEPROMs, calibration records and manifests must not. Requiring AOIDs only where machines consume them keeps the mechanism useful without turning it into paperwork.

AOID bookkeeping is a simple list in the [Document Index](./document-index.md) (or a family repository's README) — enough to prevent collisions. New taxonomy values (a new class or domain code) need an EDR, because they become uninterpretable if invented ad hoc.

A machine-readable object manifest (`auriora-object.yaml` with family ID, AOID, name, maturity, supported interfaces) MAY be provided for Released artifacts where tooling consumes it; it is not mandatory.

## 7. Document IDs

Document IDs (`AES-INDEX`, `AES-TERM`, `AHDG`, `ADS`) identify the *standards documents themselves* and other documents that external records cite.

### AES-DOCID-001: Document Identifiers for Standards

**Requirement:** AES chapters and companion standards SHALL carry stable document IDs in the form `<SCOPE>-<TOPIC>` (uppercase ASCII letters, digits, hyphens). Once a document ID has appeared in a released artifact or record, it SHALL NOT be reused for a different document family; superseded IDs remain reserved and are listed with their replacement in the [Document Index](./document-index.md).

**Rationale:** Stable document identity keeps old reviews, releases and citations interpretable after reorganizations.

Ordinary project documentation — READMEs, design notes, test notes — does **not** need document IDs or register entries. Assign an ID only when an external artifact (a release record, a calibration record, another standard) needs to cite the document durably.

## 8. Name Mapping

For each Released Product Family, keep the naming surfaces consistent and record them once (README or manifest): family identifier, public name, AOID, repository name, PCB marking prefix, firmware identifier and EEPROM identity fields. This is a SHOULD — the cost is one small table; the benefit is that support and manufacturing records stay reconcilable.
