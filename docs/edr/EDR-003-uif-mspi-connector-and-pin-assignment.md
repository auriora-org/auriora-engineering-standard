# EDR-003: UIF-MSPI Connector and Pin Assignment

## Status

Proposed

*Self-authored draft pending maintainer acceptance per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Managed Unit relies on this pinout.*

## Context

The Managed SPI Unit Interface Profile ([`UIF-MSPI`](../interfaces/managed-spi.md), Draft) fixes the Managed-Unit signal set — the six-signal discovery/power/ready core shared with [`UIF-I2C-6`](../interfaces/uif-i2c-6.md), plus `UIF_SPI_SCK`, `UIF_SPI_MOSI`, `UIF_SPI_MISO`, `UIF_SPI_CS_N`, `UIF_IRQ_N`, `UIF_RESET_N` — but leaves its physical layer OPEN (managed-spi.md §4): connector family/part, final pin count and pin ordering, the number and definition of any synchronization/auxiliary signal(s), and the per-signal electrical attributes. That section states these are Platform interface decisions and requires an EDR before the profile can reach `1.0` ([AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger)).

The realization forcing the decision is the AURIORA Environmental Sensor Unit (`AOID:PUB:UNIT:ENV:AEU:001`, AEU-01), being reworked from a Passive Unit (`UIF-I2C-6`) into a Managed Unit built around an STM32U031C8U6 controller. AEU-01 needs a committed connector and pinout to enter PCB layout, and — as the **first `UIF-MSPI` realization** — its pinout will in practice become the profile's reference physical layer, exactly as AEU-01's power decisions became the first `UIF-I2C-6` realization.

A pinout chosen only for this one low-bandwidth sensor Unit would under-provision return paths for the higher-bandwidth Managed Units the profile is explicitly meant to serve (radio, GNSS, compute-bearing Units). Because a Unit Interface is a versioned platform contract, the reference pinout is expensive to change after any Released Managed Unit exists ([AES-IF-005](../05-interfaces-and-versioning.md#aes-if-005-backward-compatibility-within-a-major-version)); return-path headroom is therefore provisioned now.

This EDR fixes the connector's physical/pinout layer and the two per-signal electrical attributes inseparable from it (reset and interrupt drive/idle). It does not resolve the remaining electrical limits.

## Alternatives Considered

The signal set is fixed by the profile (6 shared core + 6 Managed). The open decision is pin count, ordering and ground allocation.

| Alternative | Assessment |
|---|---|
| 12 positions, single GND (signal set only) | Minimal. One GND at the power end leaves the SPI group without a local return; adequate only for very low SPI clocks. Under-provisions the profile for higher-speed Managed Units. |
| 13 positions, 2 GND (power return + one SPI-side GND) | Good for AEU-01: tight power loop plus a return adjacent to `SCK`. Sufficient to ~8–10 MHz, but the SPI block is guarded on one side only. |
| **14 positions, 3 GND — power return + SPI block guarded both sides** | **Chosen.** Power loop closed at the VIN end; the `SCK`/`MOSI`/`MISO`/`CS_N` block is flanked by GND on both sides, so every high-speed line is ≤2 positions from a return. Costs one contact and ~1 mm of board edge; provides SI headroom to ~20–30 MHz for future realizations. |
| Add a reserved aux/sync position "for the future" | Rejected. An undefined reserved contact is speculative complexity — a spare pin is explicitly not a justification. A future hardware-sync need is a versioned profile addition, not a blank pin. |
| Add a second power/GND pair | Rejected. JST SH is rated ~1 A/contact; the profile's functional load (AEU-01 worst case ~0.21 A) is far below one contact's rating, so parallel power pins earn nothing. |
| Reuse the `UIF-I2C-6` 6-position connector/keying | Rejected on safety: a Managed host/unit must not mismate with a Passive one. A distinct position count makes cross-profile mating physically impossible. |

## Decision

The `UIF-MSPI` physical layer is a **14-position, 1.00 mm-pitch connector in the JST SH family** — the same family as the AEU-01 `UIF-I2C-6` realization (assembly/tooling continuity), but with a distinct position count that inherently prevents cross-profile mismating, and intrinsically polarized against reverse insertion. The exact sub-series and part number are confirmed at BOM time.

Pin assignment (pin 1 marked; direction is host-view):

| Pin | Signal | Direction | Notes |
|---:|---|---|---|
| 1 | `UIF_PWR_VIN` | Host → Unit | Unit input power |
| 2 | `GND` | — | Power return; closes a tight loop with pin 1 |
| 3 | `UIF_PWR_EN` | Host → Unit | Functional power-domain enable |
| 4 | `UIF_READY` | Unit → Host | Active-HIGH; Unit-controller driven |
| 5 | `UIF_RESET_N` | Host → Unit | Active-LOW; open-drain; pull-up host side |
| 6 | `UIF_IRQ_N` | Unit → Host | Active-LOW; open-drain; pull-up host side |
| 7 | `UIF_I2C_SCL` | Host → Unit | Discovery/identity I²C clock |
| 8 | `UIF_I2C_SDA` | Bidirectional | Discovery/identity I²C data |
| 9 | `GND` | — | SPI return (lower guard), adjacent to `SCK`; also the low-speed group's upper return |
| 10 | `UIF_SPI_SCK` | Host → Unit | SPI clock |
| 11 | `UIF_SPI_MOSI` | Host → Unit | SPI data, host → unit |
| 12 | `UIF_SPI_MISO` | Unit → Host | SPI data, unit → host |
| 13 | `UIF_SPI_CS_N` | Host → Unit | Active-LOW chip select |
| 14 | `GND` | — | SPI return (upper guard) |

The low-speed signals (`UIF_PWR_EN`, `UIF_READY`, `UIF_RESET_N`, `UIF_IRQ_N`, `UIF_I2C_SCL`, `UIF_I2C_SDA`) are kept contiguous on pins 3–8 and the SPI block contiguous on pins 10–13. Each group therefore maps onto a single ESD-protection array with no isolated line — in particular `UIF_IRQ_N` sits with the other low-speed signals rather than alone beyond the SPI guard, which would otherwise force an extra array or a long protection stub.

Per-signal electrical attributes fixed here because they are inseparable from the pinout:

- **`UIF_RESET_N`** — active-LOW, **open-drain with the pull-up on the host side**. This matches the bidirectional open-drain reset semantics of typical Unit controllers (e.g. STM32 `NRST`) and avoids drive contention and hot-plug back-drive into an unpowered Unit.
- **`UIF_IRQ_N`** — active-LOW, **open-drain, pull-up on the host side**. The host (the persistent side) owns the de-asserted (HIGH) idle state, so the line is defined when the Unit is absent, unpowered or disabled, and there is no per-Unit pull-up variation. Event semantics remain per managed-spi.md §3 (general event notification; the host queries the Unit API for the cause).
- **No synchronization/auxiliary signal** is defined in this pinout.

## Rationale

A Unit Interface is a versioned platform contract, not a single-board convenience. Because the first realization's pinout becomes the de-facto reference, provisioning return paths now for the profile's stated higher-bandwidth use cases avoids a later breaking change; changing the reference pinout after a Released Managed Unit exists would be an AES-IF-005 compatibility break.

The three-GND guard is the minimum that earns its place: a power-loop return (supply drop/EMI) plus a both-sided SPI guard (clock return and crosstalk), each tied to a concrete failure mode. Everything beyond it — a reserved aux pin, a second power pair — fails the complexity-admission test and is rejected above.

Differentiating the connector by position count enforces the "connector fit is not compatibility" discipline physically: a Passive host cannot energize or mis-drive a Managed Unit, and vice versa. Host-side ownership of the `UIF_RESET_N` and `UIF_IRQ_N` idle states mirrors the existing UIF rule that absent, disabled or starting Units must still present defined states to the host.

## Consequences

- AEU-01 adopts this pinout for its Managed rework; its 6-position `UIF-I2C-6` connector is replaced, superseding the connector portion of the in-progress passive layout.
- Every `UIF-MSPI` host SHALL provide the `UIF_RESET_N` and `UIF_IRQ_N` pull-ups and mate a 14-position SH connector.
- The profile gains a reference physical layer but remains **Draft**: no Released conformance may be claimed until `UIF-MSPI` reaches `1.x` with its electrical layer fixed (see below).
- AEU-01 becomes the first `UIF-MSPI` realization; its bring-up measurements feed the electrical-layer finalization, as its `UIF-I2C-6` power numbers did.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

Explicitly **not** resolved here — these belong to the `UIF-MSPI` electrical-layer finalization before `1.0`, informed by AEU-01 bring-up:

- `UIF_PWR_VIN` tolerance band and per-rail current limits.
- SPI maximum clock rate, mode (CPOL/CPHA) and timing.
- Logic thresholds and levels.
- ESD protection levels and hot-plug behavior/limits.
- `UIF_RESET_N` / `UIF_IRQ_N` pull-up values and thresholds (ownership is fixed here; the values are open).
- Confirmation or replacement of the provisional identifier `UIF-MSPI`.

## Affected Requirements / Documents

- [managed-spi.md §4](../interfaces/managed-spi.md) — resolves the connector, pin-ordering and aux-signal OPEN items; the remaining §4 electrical items stay open.
- [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger) — platform interface decision requiring an EDR.
- [AES-IF-006](../05-interfaces-and-versioning.md#aes-if-006-unit-interface-completeness) / [AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles) — interface completeness and profile versioning.
- [document-index.md](../document-index.md) — `UIF-MSPI` status remains Draft until the electrical layer is fixed and the profile reaches `1.0`.

## Future Review Criteria

Revisit if a Managed Unit requires SPI beyond this guarded pinout's SI headroom, a functional load beyond one SH contact's rating, or a hardware synchronization signal — each of which is a versioned profile change that SHALL link back to this EDR.
