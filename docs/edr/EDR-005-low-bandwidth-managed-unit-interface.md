# EDR-005: A Low-Bandwidth Managed Unit Interface Profile

## Status

Proposed

*Self-authored draft pending maintainer acceptance per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Unit relies on this profile.*

Supersedes the AEU-01 consequence of [EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md) and resolves its open identifier item. EDR-003's connector and pin assignment stand unchanged.

## Context

AES 1.1.0 introduced two Unit execution models (Passive, Managed) and two Unit Interface Profiles: [`UIF-I2C-6`](../interfaces/uif-i2c-6.md), a six-signal profile described as being for "Passive Units and simple I²C-based Units", and [`UIF-MSPI-14`](../interfaces/uif-mspi-14.md), a twelve-signal, fourteen-position profile for "Managed Units requiring a high-level SPI API".

In practice the two profiles were read as *Passive ⇒ I²C, Managed ⇒ SPI*. Nothing in the normative text says that — [AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles) treats profiles as an open set — but the two available profiles left no third choice, and `UIF-MSPI-14` became the default landing place for any Unit with a controller behind it. [EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md) records exactly this: AEU-01, an environmental sensor Unit producing tens of bytes at sub-hertz rates, was moved from `UIF-I2C-6` to a 14-position SPI profile solely because it gained an STM32 controller and a high-level API.

The expected AURIORA Unit portfolio makes this the common case rather than the exception. AEU (environmental), ASU (spectral, STM32U031 + TCS34488 + TMP112), the Soil Unit (STM32 bridging an RS-485/Modbus sensor) and further sensing Units all share one shape: an own controller, a high-level API that hides internal peripherals, small payloads, low update rates, no hard deadlines, and priorities of low power, small PCB area and simple field cabling. For all of them the SPI transport, `UIF_RESET_N` and the guarded 14-position connector are pure cost.

Two axes were being conflated:

|  | Low bandwidth | High bandwidth |
|---|---|---|
| **Passive / Simple** | `UIF-I2C-6` | normally not applicable |
| **Managed** | *missing* | `UIF-MSPI-14` |

The management model describes whether the host drives Unit peripherals directly or through a versioned Unit API. The transport describes what throughput, latency and timing determinism the interface must deliver. They are independent, and the missing cell is the one most of the portfolio falls into.

This is a Platform interface decision — a new named Unit Interface Profile, new normative interface requirements and a new EEPROM TLV field — and therefore requires an EDR under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger).

## Alternatives Considered

### Which interface

| Alternative | Assessment |
|---|---|
| **Use `UIF-MSPI-14` for low-bandwidth Managed Units** (status quo) | Rejected. Fourteen contacts, two buses and two extra host signals to move ~100 bytes at ~1 Hz. Costs PCB area on Units explicitly optimized for size, a second host peripheral per port, more cable conductors in field wiring, and a wider ESD and hot-plug surface. Also drags `UIF_RESET_N` into designs whose controller is entirely inside the `UIF_PWR_EN` domain, where it adds nothing. |
| **Widen `UIF-I2C-6` to cover Managed Units unchanged** (6-pin, polling only) | Rejected, though closest to viable. Cheapest option and needs no new connector, but two independent problems: (a) an identical connector and pinout on two profiles with fundamentally different host contracts means a Passive host and a Managed Unit mate freely, leaving discovery as the only guard — the Platform already rejected that reasoning for `UIF-MSPI-14` in EDR-003; (b) no asynchronous event path at all, forcing every Managed Unit and its host awake on a polling cadence, against the low-power goal, and closing the door on Units such as the Communication & Timing Unit whose events are genuinely asynchronous. |
| **A separate polling-only Managed I²C profile *and* an interrupt-bearing one** | Rejected. Two connector variants, two host port variants and two sets of test fixtures to save one 1 mm contact. A Unit that later gains an event source would need a profile change, which is a compatibility event. Explicitly against the "no more profiles than necessary" goal. |
| **7-position: `UIF-I2C-6` pins 1–6 + generic `UIF_IRQ_N`** | Rejected as the final form, though it is the chosen option minus one contact. It buys the asynchronous event path, but leaves the profile with a single ground at the power end — the same one-contact, one-conductor return that carries both supply current and every signal down a field cable, with the far end of the signal group five positions from a reference. |
| **8-position: pins 1–6 + `UIF_IRQ_N` + a second `GND` at pin 8** | **Chosen.** Adds the event path *and* a return at the opposite end of the connector, roughly halving cable ground impedance and putting every signal within three positions of a reference. Pins 1–6 keep the `UIF-I2C-6` order, so PCB layout, ESD-array grouping and host pin mapping carry over. A distinct position count prevents cross-profile mating mechanically. |
| **8-position: pins 1–6 + `UIF_IRQ_N` + `UIF_RESET_N`** | Rejected — the same contact spent on reset instead of ground. The Unit controller sits wholly inside the `UIF_PWR_EN`-switched domain, so a power cycle is a *stronger* reset than a controller reset pin: it also clears peripherals, latched I/O and external devices such as an RS-485 transceiver, which `NRST` does not. Firmware update is a Unit API operation in the Managed model. A reset pin would add a host pull-up and a hot-plug back-drive path into an unpowered Unit for no capability gained, whereas the second ground addresses a failure mode the profile actually has. |

### Whether the event pin is mandatory

| Alternative | Assessment |
|---|---|
| Mandatory contact, mandatory use | Rejected. Forces an unused signal and a host interrupt input on Units such as AEU that have nothing asynchronous to report. |
| Optional contact (a variant with and a variant without the event pin) | Rejected — the two-profile problem above in a different form. |
| **Mandatory contact, optional use, declared in capability metadata** | **Chosen.** One connector, one host port design. A Unit with no asynchronous events leaves the line undriven; the host pull-up defines it; the host polls. A Unit with events declares the capability and the host may serve it by interrupt. Every event remains observable by polling, so the signal is a latency and power optimization and never the sole path to an event. |

### Naming

`Managed I2C` reads as prose, not as a profile identifier. The existing identifiers were `UIF-I2C-6` (transport + position count) and the provisional `UIF-MSPI` (`M` for Managed + transport) — two half-patterns. **`UIF-MI2C-8`** satisfies both at once and states the position count, which is the profile's safety-relevant discriminator.

The Platform pattern is therefore recorded as `UIF-[M]<transport>-<positions>`: the `UIF-` prefix marking a Unit Interface Profile, an optional `M` for a Managed-Unit profile, the transport, and the connector position count.

Introducing a third profile is the moment to make the family consistent rather than to add a second exception to it. `UIF-MSPI` was explicitly provisional, with confirmation or replacement listed as an open item of that profile and of EDR-003, and no artifact yet realizes it — so the cost of aligning it is a rename in Draft documents, and the cost of not aligning it is a permanent oddity in the one place the Platform names its interfaces. Alternatives weighed: leave `UIF-MSPI` alone (rejected — the pattern would be broken from the day it was written); drop position counts from all identifiers (rejected — the position count is what makes cross-profile mating impossible and belongs in the name); defer the rename to the profile's `1.0` (rejected — it costs the same then and misleads until then).

## Decision

1. A third Unit Interface Profile, **`AURIORA UIF-MI2C-8`** (`docs/interfaces/uif-mi2c-8.md`, version `0.1`, Draft), is the default Unit Interface for low-bandwidth Managed Units.

2. Its physical layer is an **8-position, 1.00 mm-pitch JST SH-family connector**, pins 1–6 identical in signal and order to `UIF-I2C-6`:

   | Pin | Signal | Direction | Mandatory |
   |---:|---|---|---|
   | 1 | `UIF_PWR_VIN` | Host → Unit | Yes |
   | 2 | `GND` | — | Yes |
   | 3 | `UIF_I2C_SCL` | Host → Unit | Yes |
   | 4 | `UIF_I2C_SDA` | Bidirectional | Yes |
   | 5 | `UIF_PWR_EN` | Host → Unit | Yes |
   | 6 | `UIF_READY` | Unit → Host | Yes |
   | 7 | `UIF_IRQ_N` | Unit → Host, open-drain, host pull-up | Contact yes, use optional |
   | 8 | `GND` | — | Yes |

   The two grounds sit at opposite ends of the connector: pin 2 closes a tight supply loop with pin 1, pin 8 returns the far end of the signal group. Both SHALL be populated on the host, on the Unit and through the full length of any cable.

3. **No `UIF_RESET_N`.** Recovery is `UIF_PWR_EN` de-assertion for a declared minimum off-time followed by re-activation. Firmware update is a Unit API operation.

4. `UIF_IRQ_N` is a **generic event notification** with the same semantics as on `UIF-MSPI-14`: it never encodes the cause, and the host queries the Unit API. Unit-specific signals such as `DATA_READY`, `FAULT`, `RX_READY` or `SPECTRUM_READY` remain prohibited.

5. Discovery is unchanged across all profiles — same EEPROM, same layout, same validation order. Two supporting rules are added because a Managed Unit's controller now shares the discovery bus:
   - **[AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation)**: the discovery EEPROM block `0x50`–`0x57` is reserved Platform-wide; a Unit's functional I²C address lies outside it and outside the I²C reserved addresses, is declared in EEPROM, and is never inferred by the host; a host sharing one bus across Unit ports resolves collisions and refuses to power a colliding Unit.
   - A **Unit API Transport Address** TLV field in [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata), mandatory for a Managed Unit on an addressed shared transport.

6. **[AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection)** states the selection rule: management model selects the host contract, transport selects the profile. `UIF-MI2C-8` is the default for low-bandwidth Managed Units; `UIF-MSPI-14` is used where throughput, latency, deterministic transfer timing or continuous streaming makes I²C unsuitable. No arbitrary byte-rate threshold is fixed.

7. The Platform profile identifier pattern is **`UIF-[M]<transport>-<positions>`**, and all profiles follow it. The provisional identifier `UIF-MSPI` is confirmed as **`UIF-MSPI-14`** — resolving that profile's open identifier item and EDR-003's — and its specification moves to `docs/interfaces/uif-mspi-14.md`. Signal set, semantics, connector and pinout are unchanged; this is a naming change in a Draft profile that no artifact yet realizes.

8. **AEU-01 adopts `UIF-MI2C-8`**, superseding EDR-003's consequence that it becomes the first `UIF-MSPI-14` realization. ASU is the second planned realization. EDR-003's connector and pinout are unaffected and remain the reference physical layer for that profile.

## Rationale

The decision separates two things that were accidentally welded together. Making *transport* an axis independent of *management model* costs one profile document and two contacts over the Passive baseline, and it removes a systematic over-provisioning across most of the expected Unit portfolio.

Sizing checks the choice rather than assuming it. ASU moves on the order of a hundred bytes per acquisition at well under 1 Hz; a 400 kHz I²C bus carries that with roughly four orders of magnitude of margin. The Soil Unit's latency is dominated by an external Modbus transaction measured in hundreds of milliseconds, which no host-side transport can improve. Even the Communication & Timing Unit's command and data plane fits comfortably — GNSS fixes at ~1 Hz, LoRa payloads ≤ 256 B. What would push that Unit out of the profile is not bandwidth but a PPS-class hardware time reference, which no generic event pin can carry on *either* existing profile. That the boundary case fails on determinism and not on throughput is direct evidence that the two axes are the right ones.

Eight positions rather than six is the one place the decision spends something, and each of the two added contacts is tied to a concrete failure mode.

`UIF_IRQ_N` buys three things: mechanical prevention of cross-profile mating, which EDR-003 already established as the Platform's discipline; an asynchronous event path, without which the low-power goal fights the polling cadence; and pinout stability, because a Unit that gains an event source later does not force a compatibility event.

The second ground answers the risk this profile actually carries. `UIF-MI2C-8` is for field-wired sensing Units, so its worst case is not a board-to-board jumper but metres of thin cable in which one 1.00 mm contact and one conductor return the supply current *and* every signal. Supply transients from the Unit's own switching then land as ground shift on the I²C receiver thresholds. Two returns roughly halve that impedance, and placing them at opposite ends of the connector lets a cable assembly reference both sides of the signal bundle rather than running `UIF_I2C_SCL`/`UIF_I2C_SDA` unreferenced down the middle. This is the same reasoning EDR-003 applied to the `UIF-MSPI-14` ground allocation, and it applies here for cable length rather than for clock rate. Retaining the `UIF-I2C-6` order on pins 1–6 means both added contacts cost a connector line item, not a redesign.

Excluding `UIF_RESET_N` follows from where the controller sits. A Unit whose controller is entirely inside the switched functional domain gets a more complete reset from `UIF_PWR_EN` than from `NRST`, because the power cycle also clears peripherals and external devices. Adding the pin would create a hot-plug back-drive path into an unpowered Unit — a real hazard — in exchange for a weaker recovery.

Address allocation is made normative now because this profile is the first to put a Unit controller and the discovery EEPROM on the same bus. Leaving it to convention would produce collisions that only appear when a second Unit type ships, at which point the fix is a field-visible incompatibility.

## Consequences

- The Platform has three Unit Interface Profiles with distinct position counts — 6, 8 and 14 — so no two can mate. The count is deliberately capped: `UIF-MI2C-8` covers a cell that was empty, it does not fragment an occupied one.
- AEU-01's Managed rework targets `UIF-MI2C-8`; its 14-position `UIF-MSPI-14` connector selection from EDR-003 is withdrawn for this Unit. Its bring-up measurements now seed the `UIF-MI2C-8` electrical layer.
- ASU is designed against `UIF-MI2C-8` from the start and is the profile's second validation case.
- Every `UIF-MI2C-8` host SHALL provide the I²C and `UIF_IRQ_N` pull-ups, SHALL support polling operation, and SHALL tolerate bounded Unit clock stretching.
- Cable assemblies for this profile SHALL populate both ground conductors end to end; a single-ground cable is not conformant and is a continuity-test item at bring-up.
- Every Managed Unit on an addressed shared transport SHALL declare its Unit API address in EEPROM; hosts SHALL NOT hard-code it. This is an additive TLV field, so existing readers are unaffected ([AES-EEPROM-003](../06-eeprom-metadata.md#aes-eeprom-003-forward-compatible-extensions)).
- `UIF-MSPI-14` is narrowed in intent and renamed, not respecified: it remains the Managed profile for throughput-, latency- or determinism-bound Units, and its signal set, semantics and EDR-003 pinout are unchanged. All three profile identifiers now read the same way, so a Unit's declared profile states its transport and its position count without a lookup.
- EDR-003 is annotated, not rewritten ([AES-EDR-002](../08-decisions-and-governance.md#aes-edr-002-decision-record-structure-and-immutability)): it continues to use the identifier in force when it was written, with a Status note recording the confirmed name.
- **Vendor naming is extended, deliberately and narrowly.** [EDR-004](./EDR-004-default-controller-platforms.md) records that AES names vendor platforms in exactly one place and that any further vendor-specific content requires its own decision; this EDR is that decision for the connector. `UIF-MI2C-8` names the **JST SH** family because [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness) requires a Unit Interface to specify a named physical connector, and because the cross-profile mating argument only holds within one family and pitch — a generic "1.00 mm 8-position connector" would not guarantee that a `UIF-I2C-6` plug cannot enter a `UIF-MI2C-8` receptacle. The naming is bounded to the connector family and pitch; the sub-series and part number stay open to BOM-time judgment, and no other component is named. [Architecture §6](../03-architecture.md#6-default-controller-platform-strategy) is amended to say *controller* platforms, so it stops reading as a claim this profile contradicts.
- The profile is **Draft**: no Released conformance may be claimed until its electrical layer is fixed and it reaches `1.x`.
- A distributed hardware time reference (PPS) is recorded as an unmet need on both Managed profiles, to be answered by a versioned profile addition rather than by a Unit-specific signal.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

Not resolved here; these belong to the `UIF-MI2C-8` electrical-layer finalization before `1.0`, informed by AEU-01 and ASU bring-up:

- JST SH sub-series and part number; cable construction and the arrangement of the two ground conductors within the bundle.
- `UIF_PWR_VIN` tolerance band and per-rail current limits.
- I²C bus speed, pull-up values and total bus capacitance budget; maximum cable length.
- Maximum clock-stretch time and the minimum `UIF_PWR_EN` off-time for recovery.
- `UIF_IRQ_N` pull-up value and thresholds; logic thresholds generally.
- ESD protection level and hot-plug behavior.

## Affected Requirements / Documents

- [`docs/interfaces/uif-mi2c-8.md`](../interfaces/uif-mi2c-8.md) — the new profile (new).
- [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-unit-interface-i2c-address-allocation), [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection) — new requirements.
- [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata) — Unit API Transport Address field added.
- [Architecture §5.1](../03-architecture.md#51-execution-models-and-transport), [AES-UNIT-006](../03-architecture.md#aes-unit-006-declared-execution-model) — execution model is independent of transport.
- [`docs/interfaces/uif-i2c-6.md`](../interfaces/uif-i2c-6.md) — scope clarified to Passive/simple Units; AEU-01 realization note updated.
- [`docs/interfaces/uif-mspi-14.md`](../interfaces/uif-mspi-14.md) — purpose narrowed to bandwidth/latency/determinism-bound Managed Units; identifier confirmed as `UIF-MSPI-14` and file renamed from `managed-spi.md`.
- [EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md) — its AEU-01 consequence is superseded; its pinout decision stands.
- [document-index.md](../document-index.md) — profile table and AOID note.

## Future Review Criteria

Revisit if: a low-bandwidth Managed Unit needs a host-controlled reset independent of power; the portfolio produces Managed Units clustering just above I²C's practical throughput, suggesting a middle transport; a distributed hardware time reference becomes a Platform requirement; or shared-bus address allocation proves insufficient for the number of Unit ports a Module carries.
