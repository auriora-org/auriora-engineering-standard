# Changelog

All notable changes to the AURIORA Engineering Standard (AES) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). AES releases use semantic versioning as required by [AES-VER-001](./docs/05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts): `MAJOR` for incompatible normative change, `MINOR` for backward-compatible normative addition, `PATCH` for clarification or defect correction. Entries record normative changes with their requirement identifiers; editorial changes are either omitted or explicitly marked as editorial, per [AES-GOV-011](./docs/08-decisions-and-governance.md#aes-gov-011-standard-change-record).

## [1.4.0] - 2026-09-10

### Added

- EEPROM optional TLV fields **Startup Peak Duration** and **Nominal Operating Current** (`AES-EEPROM-008`). Both are informational: they let a host that wants to estimate energy, log consumption, size a battery or budget inrush work from better data than a worst-case figure, and a host `SHALL NOT` substitute either for a worst-case field in a decision that enforces a limit or authorizes power. The same paragraph fixes the units of the power records — currents in milliamperes, durations in milliseconds. Additive per `AES-EEPROM-003`; the schema major version is unchanged and existing readers are unaffected.
- Terminology supporting term **Unit Interface Host**: whatever implements the host side of a Unit Interface port — normally a Module, but also an adapter, test fixture or third-party host. Interfaces and Versioning §3.1 states the consequence: where AES writes a Unit Interface obligation on "the Module", it binds whatever implements the port, which is what makes a Unit reusable outside the Module it was designed with. Product-level safety policy is not transferred by implementing a port and stays with the Module (`AES-MOD-004`).

### Changed

- `AES-UNIT-007`: the discovery domain `SHALL` — not `MAY` — remain powered and readable from `UIF_PWR_VIN` while `UIF_PWR_EN` is LOW. The sequence already validates a Unit before enabling it, so discovery power was never optional, and the companion AHDG §6.1 already required it as a `MUST`; AES was the weaker of the two on the same fact.
- `AES-UNIT-007`: the wait for `UIF_READY` is now bounded. On expiry the host de-asserts `UIF_PWR_EN` and treats the Unit as failed rather than transacting with it. The bound is a profile or product property, not a Platform constant. This was previously stated only by `UIF-MI2C-8`, leaving the profile-independent sequence with one unbounded step.
- `AES-MOD-003`: a Released Module that accepts Units now states, alongside its supported profiles and versions, how many ports of each profile it provides, what one port supplies, and any restriction on operating those ports simultaneously. A Unit is already required to declare what it needs with numbers (`AES-UNIT-004`, `AES-EEPROM-008`); this is the other side of the same contract. Port count is explicitly not a power promise.
- [`UIF-MI2C-8`](./docs/interfaces/uif-mi2c-8.md) draft clarification: the `UIF_READY` timeout rule is referenced from `AES-UNIT-007` rather than restated, and the timeout value is added to the profile's open electrical items.

### Compatibility

No breaking change. The two EEPROM fields are optional TLV records; the Unit Interface Host term is a supporting term, not frozen core vocabulary (`AES-TERM-003`); the two `AES-UNIT-007` changes tighten a sequence no Released artifact yet implements, and the `AES-MOD-003` extension binds Released Modules, of which there are none. All three Unit Interface Profiles keep their signal sets, connectors and `0.1` Draft versions. No decision record is triggered: the change set touches no frozen vocabulary, no AOID taxonomy, no Released interface and no EEPROM schema major version (`AES-EDR-001`).

## [1.3.0] - 2026-09-10

### Added

- Unit Interface Profile **`AURIORA UIF-MI2C-8`** ([`docs/interfaces/uif-mi2c-8.md`](./docs/interfaces/uif-mi2c-8.md), version `0.1`, Draft): the default Unit Interface for **low-bandwidth Managed Units**. Eight-position 1.00 mm JST SH-family connector — `UIF-I2C-6` pins 1–6 unchanged in signal and order, plus `UIF_IRQ_N` on pin 7 as a generic open-drain event notification with the host owning the pull-up, and a second `GND` on pin 8. The two grounds sit at opposite ends of the connector: pin 2 closes a tight supply loop with pin 1, pin 8 returns the far end of the signal group, roughly halving cable ground impedance for field-wired Units and keeping every signal within three positions of a reference; both SHALL be populated end to end, cable included. All eight contacts are mandatory; only the *use* of `UIF_IRQ_N` is optional and is declared in capability metadata, so one profile serves both event-driven and polling-only Units. No `UIF_RESET_N`: the Unit controller sits inside the `UIF_PWR_EN`-switched domain, so a power cycle is the stronger recovery and firmware update is a Unit API operation. The profile also fixes the Managed-I²C clock-stretch contract, bus-recovery obligation and power-sequencing detail. Electrical and mechanical limits are open, so the profile stays Draft.
- `AES-IF-009` (Unit Interface I2C address allocation): the discovery EEPROM block `0x50`–`0x57` is reserved Platform-wide with `0x50` as default; a Unit's functional address lies outside it and outside the I²C reserved addresses; a Managed Unit declares its Unit API address in EEPROM and a host never infers or hard-codes it; a host sharing one bus across Unit ports resolves collisions and leaves `UIF_PWR_EN` LOW for a colliding Unit.
- `AES-IF-010` (Unit Interface Profile selection): a Managed Unit `SHOULD` use `UIF-MI2C-8` by default and `UIF-MSPI-14` where throughput, latency, deterministic transfer timing or continuous streaming makes I²C unsuitable; a Passive or simple Unit `SHOULD` use `UIF-I2C-6`. Accompanied by a criteria table (determinism, streaming, latency, payload and update rate, event frequency, transaction count, power, connector and cabling, reset need) — no arbitrary byte-rate threshold.
- Interfaces and Versioning §3.2 *Profile Family and Selection*: the management-model × transport matrix making explicit that **Managed does not imply SPI**, and the profile identifier pattern `UIF-[M]<transport>-<positions>` (§3.1).
- EEPROM optional TLV field **Unit API Transport Address**, mandatory for a Managed Unit whose Unit API shares an addressed transport with discovery (`AES-EEPROM-008`). Additive per `AES-EEPROM-003`; existing readers are unaffected.
- Informative worked example [Choosing a Unit Interface Profile](./examples/worked-example-unit-interface-profile-selection.md) (`AES-EXAMPLE-UIF-SELECTION`): AEU, ASU, the Soil Unit and the Communication & Timing Unit assessed against `AES-IF-010`, with ASU worked end to end. Indexed in `STANDARD.md` and the Document Index.
- [EDR-005: A Low-Bandwidth Managed Unit Interface Profile](./docs/edr/EDR-005-low-bandwidth-managed-unit-interface.md), recording the decision and the alternatives weighed — reusing `UIF-MSPI-14`, widening `UIF-I2C-6` unchanged, split polling/interrupt profiles, a 7-position variant with a single ground, the chosen 8-position profile, an 8-position variant spending the contact on `UIF_RESET_N` instead, and mandatory versus optional event signalling — with AEU, ASU, the Soil Unit and the Communication & Timing Unit as validation cases. Indexed in `STANDARD.md`.

### Changed

- Architecture §5.1 renamed *Execution Models and Transport* and extended: the execution model fixes the host contract, the transport fixes the Unit Interface Profile, and the two are independent. `AES-UNIT-006` rationale extended accordingly. Terminology entries for *Managed Unit* and *Unit Interface Profile* state the same separation.
- Interfaces and Versioning §3.1: `UIF_SPI_*` described as a transport rather than as the Managed-Unit bus, and `UIF_IRQ_N` / `UIF_RESET_N` split into separate entries with their profile-independent meanings.
- [`UIF-I2C-6`](./docs/interfaces/uif-i2c-6.md) scope clarified as management-model-based, directing Managed Units to `UIF-MI2C-8` or `UIF-MSPI-14`; functional I²C addressing bound to `AES-IF-009`. Its "first hardware realization" section is replaced: **AEU-01 is reworked as a Managed Unit and now realizes `UIF-MI2C-8`**, so `UIF-I2C-6` currently has no committed realization. The +3V3 nominal `UIF_PWR_VIN` working assumption is retained across UIF profiles and remains non-normative.
- **The Managed SPI profile is renamed `UIF-MSPI-14`** and its specification moved from `docs/interfaces/managed-spi.md` to [`docs/interfaces/uif-mspi-14.md`](./docs/interfaces/uif-mspi-14.md). This confirms the provisional identifier `UIF-MSPI`, which the profile and EDR-003 both listed as an open item, and brings all three profiles onto the `UIF-[M]<transport>-<positions>` pattern. Its purpose is also narrowed: explicitly **not** the default Managed profile, selected on throughput, latency, determinism, streaming or a need for reset independent of power; I²C address allocation bound to `AES-IF-009`. Signal set, semantics, connector and the EDR-003 pinout are unchanged — the change is naming and intent only, in a Draft profile no artifact yet realizes.
- [EDR-003](./docs/edr/EDR-003-uif-mspi-connector-and-pin-assignment.md) Status annotated: its connector and pin assignment stand; its AEU-01 consequence is superseded by EDR-005 and its open identifier item is resolved to `UIF-MSPI-14`. The record itself is not rewritten (`AES-EDR-002`) — it keeps the identifier in force when it was written, with only link targets repointed to the renamed file.
- Document Index: `UIF-MI2C-8` added to the profile table; the AEU-01 AOID row now records it as a Managed Unit realizing `UIF-MI2C-8`.
- Architecture §6 now says AES names vendor *controller* platforms in one place, and points at the Unit Interface Profile specifications as the other admitted vendor naming (the connector family, required by `AES-IF-006`). EDR-005 records that carve-out as `EDR-004` requires for any vendor-specific content beyond §6.
- *Editorial:* the Unit Interface Profiles row of the Canonical Documents table in `STANDARD.md` now names the profile-selection matrix.

### Compatibility

No breaking change. All additions are new documents, new requirements and an optional TLV record; no existing requirement, signal, pinout or schema field changed meaning. `UIF-I2C-6` and `UIF-MSPI-14` keep their signal sets, connectors and versions; the Managed SPI rename touches a Draft profile with no realization, so nothing depends on the old identifier. The AEU-01 profile change is a project-level consequence of a Pre-Release Unit whose profile was itself still Draft, not an interface compatibility break.

## [1.2.0] - 2026-09-07

### Added

- Default controller platform strategy (Architecture §6): two workload profiles — *bounded low-power function* and *local processing* — each with a default MCU platform. New requirement `AES-ARCH-001` (default controller platform): a low-power STM32-class MCU (STM32U0 / STM32L0) for a bounded low-power sensing, actuation or interface function; an RP2040-class MCU where higher local processing, buffering, DSP or parallel real-time workloads justify it. `SHOULD` strength — another platform MAY be used where technical requirements warrant it, with reasons stated in the project's design notes or an ADR. Selection is keyed to the workload profile, not to the Unit/Module role.
- [EDR-004: Default Controller Platforms](./docs/edr/EDR-004-default-controller-platforms.md), recording the platform-wide decision, the alternatives (no default, single platform, role-keyed selection, mandatory strength) and its consequences — including that Architecture §6 is the one place AES names vendor platforms, and that the companion guides remain technology-neutral.
- [EDR-003: UIF-MSPI Connector and Pin Assignment](./docs/edr/EDR-003-uif-mspi-connector-and-pin-assignment.md) fixing the Managed SPI profile's connector and pinout, indexed in `STANDARD.md`. The profile remains Draft: the remaining electrical limits are still open.

### Changed

- *Editorial:* the Architecture row of the Canonical Documents table in `STANDARD.md` now names the default controller platform strategy.

## [1.1.0] - 2026-07-14

### Added

- Unit execution models: `Passive Unit` and `Managed Unit` defined as execution models of a Unit (not new top-level objects), with `Unit API` and `Unit Interface Profile` as supporting terms (Terminology §3). New requirements `AES-UNIT-006` (declared execution model, discoverable capabilities/API version) and `AES-UNIT-007` (deterministic discovery→validate→`UIF_PWR_EN`→wait `UIF_READY`→communicate sequence) in Architecture §5.
- Unit Interface signal and profile model (Interfaces and Versioning §3.1): the `UIF_` prefix defined as *AURIORA Unit Interface*, the standard `UIF_` signal set, active-HIGH `UIF_READY` semantics, and a prohibition on any Unit-presence pin (`UIF_PRESENT`/`UIF_PRESENT_N`) — presence is EEPROM discovery. New requirement `AES-IF-008` (named, independently versioned Unit Interface Profiles; hosts reject unsupported profiles/versions).
- EEPROM optional TLV fields for execution model, Unit Interface Profile identifier/version, Unit API identifier/version, capability flags and power characteristics (required voltage, startup/operating/discovery-state current), via new requirement `AES-EEPROM-008` layered on the existing TLV extension mechanism (`AES-EEPROM-003`) — no fixed-header expansion.
- Versioned Unit Interface Profile specifications under `docs/interfaces/`: `AURIORA UIF-I2C-6` (Draft, six-signal profile for Passive/simple-I²C Units) and the `AURIORA Managed SPI Profile` (Draft). Both define the signal set and semantics; connector, pin count and electrical/mechanical limits are left as explicit open hardware decisions, so both remain Draft until finalized. Indexed from `STANDARD.md` and the Document Index.
- `UIF-I2C-6` §3 records the first hardware realization (AEU-01, `AOID:PUB:UNIT:ENV:AEU:001`) seeding the electrical layer with a nominal `UIF_PWR_VIN` of +3V3; these values are AEU-01-specific and not yet profile-normative. The AOID is registered provisionally in the Document Index AOID table.

## [1.0.0] - 2026-07-13

First release of the AURIORA Engineering Standard.

### Added

- `STANDARD.md`: scope, requirement language (MUST/SHOULD/MAY scaled by applicability and maturity), the three-level maturity model (Experimental, Active Development, Released), conformance, the primary architecture diagram and reuse decision tree, and the foundation governance rules `AES-GOV-001`–`AES-GOV-003`.
- Nine canonical chapters: Principles, Terminology, Architecture (Platform, Module, Controller, Unit design), Naming and Identity (family identifiers, product numbers, revisions, serials, AOIDs, document IDs), Interfaces and Versioning, EEPROM Metadata, Maturity and Release, Decisions and Governance, Review Checklists.
- Fixed historical decisions `AES-HIST-001`–`AES-HIST-006` preserving platform-first architecture, Controller/Module separation, replaceable Units, interface contracts, documentation-as-product and stable family identity.
- Architectural Decision Records (`ADR-001`–`ADR-003`) and Engineering Decision Records (`EDR-001`–`EDR-002`).
- Document index and worked Module lifecycle example.
- Two review checklists (general engineering and release); domain-specific checklists delegated to the companion guides.
- CC BY-SA 4.0 license and contributing policy.
- Companion standards and guides linked from the handbook: [AURIORA Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) (`AHDG`), [AURIORA Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) (`AFSG`), [AURIORA Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) (`ASSG`) and [AURIORA Documentation Standard](https://github.com/auriora-org/auriora-documentation-standard) (`ADS`).
