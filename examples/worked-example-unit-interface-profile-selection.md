# Worked Example: Choosing a Unit Interface Profile

**Document ID:** AES-EXAMPLE-UIF-SELECTION
**Status:** Informative
**Depends On:** [Interfaces and Versioning](../docs/05-interfaces-and-versioning.md), [Unit Interface Profiles](../docs/interfaces/README.md)

This example applies the profile-selection rule ([AES-IF-010](../docs/05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-selection)) to four planned AURIORA Units. It creates no obligations; it exists to show where the boundary between the Managed profiles actually falls, and why it is not where one would first guess.

## Four assessments

| Unit | Data and timing profile | Profile |
|---|---|---|
| **AEU** — Environmental Unit (STM32 + several internal sensors) | A few tens of bytes per sample, sub-hertz to a few hertz, no deadline. | `UIF-MI2C-8`. Event notification optional; polling is sufficient. |
| **ASU** — Spectral Unit (STM32U031 + TCS34488 + TMP112) | A spectrum of a few tens of bytes per acquisition; integration time in the tens to hundreds of milliseconds; no hard deadline. | `UIF-MI2C-8`. The canonical case, worked through below. |
| **Soil Unit** (STM32 bridging an RS-485/Modbus sensor) | A handful of registers per poll; the external Modbus transaction dominates latency at 0.1–1 s. | `UIF-MI2C-8`. The Unit controller absorbs the slow external bus; the host sees a bounded high-level API and never the Modbus register map. Event notification is useful to signal transaction completion. |
| **Communication & Timing Unit** (STM32U031 + GNSS + LoRa) | Command and data plane is small: position fixes at ~1 Hz, LoRa payloads ≤ 256 B. Asynchronous downlink reception with a bounded service window. | `UIF-MI2C-8` for the command and data plane, with `UIF_IRQ_N` used in earnest for LoRa receive. A hardware time reference does not fit either Managed profile — see below. |

## The boundary case

The Communication & Timing Unit is the instructive one: what would push it towards a larger profile is not bandwidth but **determinism**. Its payloads fit an I²C transport several times over. A PPS-class time reference, however, is a sub-microsecond hardware edge, and no generic event pin whose cause is resolved by an API query can carry it — not on [`UIF-MI2C-8`](../docs/interfaces/uif-mi2c-8.md) and not on [`UIF-MSPI-14`](../docs/interfaces/uif-mspi-14.md) as currently specified, which defines no synchronization signal ([EDR-003](../docs/edr/EDR-003-uif-mspi-connector-and-pin-assignment.md)). A Unit needing a distributed hardware time reference requires a versioned profile addition, not a Unit-specific pin on an existing profile.

That the boundary falls on timing rather than on throughput is the practical evidence for treating management model and transport as independent axes ([Interfaces and Versioning §3.2](../docs/05-interfaces-and-versioning.md#32-profile-family-and-selection)).

## ASU end to end

```text
Host (Module)
     │  UIF-MI2C-8   (VIN, GND, SCL, SDA, PWR_EN, READY, IRQ_N, GND)
STM32U031            ← the Unit controller: implements the Unit API
     │  internal sensor interfaces (not visible to the host)
TCS34488, TMP112
```

The host operates the Unit through high-level operations only — `GET_STATUS`, `START_MEASUREMENT`, `GET_MEASUREMENT`, `SET_INTEGRATION_TIME`, `GET_SPECTRUM`, `GET_TEMPERATURE`, `GET_PENDING_EVENTS` — and never touches a TCS34488 or TMP112 register. Replacing either internal sensor with a different part is a Unit-internal change that does not alter the host contract, which is what the Managed execution model is for.

Interrupt-driven flow:

```text
host: START_MEASUREMENT        →  unit acquires, processes
                                  UIF_IRQ_N asserted
host: GET_PENDING_EVENTS       →  MEASUREMENT_COMPLETE
host: GET_SPECTRUM             →  UIF_IRQ_N de-asserted after acknowledgement
```

Polling flow, on a host without an interrupt input, or a Unit not declaring the event capability:

```text
host: START_MEASUREMENT
host: GET_STATUS  (repeat)     →  BUSY … BUSY … COMPLETE
host: GET_SPECTRUM
```

Both are valid and produce the same result, because every event reachable through `UIF_IRQ_N` is also observable by polling.

## Why not Managed SPI

ASU moves on the order of a hundred bytes per acquisition at well under 1 Hz — roughly four orders of magnitude below what a 400 kHz I²C bus sustains. `UIF-MSPI-14` would add six contacts, a second bus and two host signals to carry it. The same arithmetic applies to AEU and the Soil Unit, which is why the Platform has a low-bandwidth Managed profile at all ([EDR-005](../docs/edr/EDR-005-low-bandwidth-managed-unit-interface.md)).
