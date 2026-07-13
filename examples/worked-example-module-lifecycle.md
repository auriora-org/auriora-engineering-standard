# Worked Example: From Breadboard to Release

**Document ID:** AES-EXAMPLE-MODULE-LIFECYCLE
**Status:** Informative
**Depends On:** [STANDARD](../STANDARD.md), [Maturity and Release](../docs/07-maturity-and-release.md)

This example shows a hypothetical AURIORA Module moving through the three maturity levels. It is illustrative and reserves no real identifiers.

## 1. Experimental

An engineer wants to know whether a front-end topology can acquire clean signals from replaceable measurement heads. They breadboard it, then spin a quick two-layer test PCB.

The repository contains, in total:

- KiCad sources
- `README.md`: *"Experimental. Feasibility test for a switched acquisition front-end. Input range ±200 mV. Hazard: none (SELV, battery powered). J2 pinout: 1 GND, 2 VBAT, 3 SIG+, 4 SIG−. Op-amp X chosen over Y for bias current — see measurements below."*
- `LICENSE`

That is the entire AES obligation. No changelog, no ADR, no register entry, no checklist evidence, no document ID. The safety rules still applied — outputs were safe at power-up and the hazard statement is honest ("none").

## 2. Active Development

The approach works. The project becomes a real Module candidate in an existing family: product `AAM-01`, working toward release. The repository now grows only what helps engineering:

- a useful README (purpose, status **Active Development**, build/flash instructions)
- schematic and PCB sources, hardware `Rev A` then `Rev B`
- BOM
- connector and interface information as it currently is
- one living document, `docs/design-notes.md`, holding: significant decisions (MCU selection and why), open questions, bring-up observations per revision, known issues, a temporary deviation note (*"Rev B has no input protection yet — MUST for release, tracked here"*), future work

The Unit Interface the Module will expose is designed early against the [interface contract template](./templates/interface-contract-template.md), because Unit identity ([AES-UNIT-001](../docs/03-architecture.md#aes-unit-001-electronic-identity)) is hard to retrofit. No formal gate sequence and no traceability matrix — the maintainer walks the [general checklist](../docs/09-review-checklists.md) before each board order.

## 3. Released

`AAM-01 Rev C` is ready for others to build. Now — and only now — the release obligations attach ([AES-REL-001](../docs/07-maturity-and-release.md#aes-rel-001-release-completeness)):

- family/product identity fixed: `AAM`, `AAM-01`; Unit Interface contract versioned `1.0` with AOID `AOID:PUB:UIF:MEAS:AAM:001`
- release tag containing sources, regenerated Gerbers, final BOM, firmware source + binary with build hash
- documented Host Interface; Unit compatibility matrix
- test evidence for critical functions and safety behavior (including a corrupted-EEPROM negative test)
- calibration method and record linkage (measurement product)
- known limitations, release notes, licenses
- release checklist walked; independent review sought for the analog front-end safety limits (self-review noted where none was available)

Later, when `UIF 1.x` needs an incompatible pin change, *that* is the moment for an EDR ([AES-EDR-001](../docs/08-decisions-and-governance.md#aes-edr-001-edr-trigger)) and a major version — because installed hardware now depends on the promise.
