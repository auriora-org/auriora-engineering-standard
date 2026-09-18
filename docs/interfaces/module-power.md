# AURIORA Module Power Interface

**Interface Identifier:** `MPI`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Architecture](../03-architecture.md), [Interfaces and Versioning](../05-interfaces-and-versioning.md)

This is the versioned specification of the **Module Power Interface**: the primary external power input of an AURIORA Module. The architectural rules — that primary power and communication are on separate connectors, that a Module Hub does not power Modules, that USB is not the deployed power distribution — live in [AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation) and [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope) and are not repeated here. Regulator, protection and layout practice is the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §6.

While this specification is Draft, it is not release-binding: no Module, power source or cable may claim Released conformance until the open items in Section 8 are resolved and the specification is versioned to a `1.x` release. Two of those items — the accepted input-voltage range and the current limit — are deliberately not numbers yet.

## 1. Purpose

Every Module generates its own internal rails. What it needs from outside is one standard, safe, unambiguous DC input that a bench supply, a field power source or a future Platform power distributor can provide with one connector and one cable, independent of how many Modules share the installation and independent of whether a Module Hub is present. The Module Power Interface is that input. It is not the Unit Interface's managed power (`UIF_PWR_VIN`, `UIF_PWR_EN`), which is a Module-to-Unit contract inside a Module; it is not USB power, which is an optional service convenience; and it is not carried on the [Module Port](./module-port.md).

## 2. Topology

```text
Power source (bench supply, field source, future power distributor)
    M8 3-position FEMALE output
        │
        │  AURIORA Power Cable: male → female, straight
        │
    M8 3-position MALE input
Module
```

- One power source output powers **one** Module input over one cable. Passive splitting of a power cable is outside this specification; a device that powers several Modules provides several outputs.
- A Module Hub is powered through its own power input and does not power Modules; a Module Power Interface input is the preferred form of a Hub's power input ([Architecture §7](../03-architecture.md#7-module-hub)).
- A future **power distribution device** providing several outputs is architecturally allowed. Its port count, total power, per-port limit, switching, sensing, enable, detection, protocol and fault behavior are not specified in this version and are not implied by anything here.

## 3. Connector

- **Form.** M8, 3-position, A-coded circular connector, IEC 61076-2-104 form.
- **Gender — the safety rule.** The Module's input is **male** (panel-mounted). A power source's output is **female**. The power cable is **male at the source end, female at the Module end**. Consequently a cable that is connected to a live source and disconnected from the Module presents a **female** end with no exposed live contact, and the only male contacts in the system — the Module's input — are energized by nothing but the cable that is plugged into them (Section 5).
- **Positions.** The M8 3-position A-coded insert populates positions **1, 3 and 4**; position 2 does not exist. This specification uses the insert's own numbering and the connector family's field-sensor convention (pin 1 supply, pin 3 return, pin 4 signal), so that a standard three-conductor M8 sensor cable wired 1-1, 3-3, 4-4 is a valid power cable.
- **Cross-mating.** The M8 3-position insert does not enter a [Module Port](./module-port.md) (8-position). A product family that uses the M8 3-position A-coded form for any *other* port — a sensor or electrode input — SHALL make mis-mating with the power input mechanically impossible or electrically harmless in both directions and record the analysis; the preferred answer is not to use that form for anything else on a Module. The connector family's rating (typically 3 A / 60 V for this insert) is a **ceiling** on what this interface may ever carry, never the interface's own limit (Section 8).
- **Labeling.** The Module's input is labeled `POWER` with the nominal voltage (`12 V DC`) and the DC symbol; a source's output is labeled `POWER OUT 12 V DC`.

## 4. Contacts

| Position | Contact | Net on the Module | Function |
|---:|---|---|---|
| 1 | `MPI_VIN` | `MPI_VIN` | Supply, **+12 V DC nominal** |
| 3 | `MPI_RTN` | `MPI_RTN` → device ground | Power return, 0 V |
| 4 | `RESERVED` | — | **Not connected** on any Module and on any source: no pull, no ground, no sense, no enable, no identification, no signal. Wired through in the cable. Its function, if any, is defined only by a new version of this specification and never by a Module, source or distributor design |

- **Return and ground.** `MPI_RTN` is the power return and is connected to the Module's ground; how it meets the signal ground of the Module Port and the shield is a design decision recorded per the Hardware Design Guide. It is not a protective earth: the interface is SELV and defines no protective conductor.
- **Reserved contact.** Not to be used as protective earth, signal ground, sense, enable, identification or communication because it is available. A Module SHALL tolerate any voltage between `MPI_RTN` and `MPI_VIN` on it without effect, since a future source may drive it.

## 5. Electrical

- **Nominal voltage.** **12 V DC.** This is the value a source provides at its output under its rated load and the value a Module's regulators are designed around.
- **Accepted input-voltage range — OPEN.** How far above and below nominal a Module SHALL operate, and what it SHALL survive without damage, are derived from realistic sources (regulated supplies, battery packs, a distributor's output regulation), regulator input ranges, cable losses at the current limit and the protection behavior of the first Modules — not fixed here (Section 8). Until it is, a Module documents the range it was designed to, and a source documents the range it delivers.
- **Current — OPEN.** The Platform continuous and start-up current limits per input are derived from actual Module and cable requirements, not from the connector rating (Section 8). Until they are fixed, a Module documents its typical, maximum and start-up current at nominal voltage in its power tree, and a source documents what it provides per output.
- **Local regulation.** A Module generates every internal rail from `MPI_VIN` with its own regulators; no rail of a Module is provided by the source, and no Module rail appears on the connector.
- **Protection at the input.** The input carries, per the Hardware Design Guide §6: reverse-polarity protection; overcurrent protection rated so that a Module fault cannot ignite the Module or the source's cable; transient protection at power entry; and an inrush behavior compatible with hot-plugging into a live source. Hot-plug is a normal operation.
- **No energized male contacts — no back-feed onto the input.** A Module that is powered from any other source — USB, an internal battery, a product-specific input — SHALL NOT present voltage on `MPI_VIN` when no source is connected to its power input. The input path is unidirectional toward the Module (an ideal-diode or equivalent power-path element, not a plain wire), so that the exposed male contacts are never energized by the Module itself.
- **No back-feed onto USB or any other source.** Neither `MPI_VIN` nor any Module rail SHALL back-drive a host's USB `VBUS` or any other external source connected to the Module at the same time ([AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation)). A Module that accepts both the Module Power Interface and USB power implements power-path protection in both directions and documents which source wins.
- **Source behavior on fault.** A source protects each output against overcurrent and short circuit independently of the Module; a Module's protection is the second barrier, not the first. What a source does after a fault — latch, retry, report — is a source product decision in this version.

## 6. AURIORA Power Cable

- **Connectors.** M8 3-position A-coded **male** at the source end, **female** at the Module end.
- **Wiring.** Straight: 1-1, 3-3, 4-4. Three conductors; position 4 wired through so that a future Platform-defined function needs no new cable.
- **Conductor size and maximum length — OPEN.** Both follow from the current limit and the accepted voltage range once fixed (the cable drop at the limit must leave the Module inside its range). Until then a cable states the current and length it was built for.
- **Marking.** `AURIORA POWER 12 V DC`.
- **Not a Link Cable.** A power cable and a Link Cable cannot be confused at the connector — different inserts — and are marked differently.

## 7. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | M8 3-position A-coded; male input on the Module, female output on the source; positions 1/3/4 as Section 4; power cable male-to-female, straight. | Fit check of the power plug into every other M8 connector of the product family; mis-mate harmlessness where any other 3-position port exists. |
| Electrical | 12 V DC nominal; local regulation of every rail; reverse-polarity, overcurrent, transient and hot-plug protection at the input; no voltage on `MPI_VIN` when the input is unconnected and the Module is otherwise powered; no back-feed onto USB or any other source; `RESERVED` open on the device. | Reverse-polarity applied with no damage; short-circuit and overcurrent on the input contained; hot-plug into a live source 100 cycles without a protection trip or a reset of the source's other outputs; `MPI_VIN` measured at 0 V with the Module running from USB; `VBUS` measured undriven with the Module running from `MPI_VIN`; `RESERVED` measured open and swept between 0 V and `MPI_VIN` without effect. |
| Behavioral | The Module operates fully from the Module Power Interface alone; USB powering, where offered, is declared with its limits; the Module documents typical, maximum and start-up current and its designed voltage range until the Platform fixes them. | Full-function test on `MPI_VIN` only; declared USB-power modes exercised and refused modes verified as refused. |

## 8. Settled and Open Items

### 8.1 Settled in this Draft

Decided by [EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md); an implementer may build against these:

- M8 3-position A-coded; male input on the Module, female output on a source; male-to-female straight power cable.
- Positions 1 `MPI_VIN`, 3 `MPI_RTN`, 4 `RESERVED`, following the insert's numbering and the connector family's convention.
- 12 V DC nominal; every rail regulated locally on the Module.
- `RESERVED` not connected on any device, wired through in the cable, Platform-owned.
- No energized male contacts: no back-feed onto the input from any other source; no back-feed onto USB or any other source from the input.
- The connector family's rating is a ceiling, not the Platform limit; primary power never on the Module Port; a Hub never obliged to power Modules; a power distributor allowed and unspecified.

### 8.2 Open

Decided before this specification reaches `1.0`, from the requirements of the first Modules and sources rather than assumed:

- **Accepted input-voltage range** — operating range and survivable range around 12 V nominal, from realistic sources, regulator input ranges, cable losses and protection behavior.
- **Platform current limit** per input — continuous and start-up — from actual Module and cable requirements; with it, the **power cable conductor size and maximum length**.
- **Function of the reserved contact**, if any.
- **Source fault behavior** as a Platform rule, if the first power distributor shows one is needed.
- **Environmental rating** (IP class, temperature) of connector and cable, as a Platform minimum or a product statement.

## 9. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)): M8 3-position A-coded male input at 12 V DC nominal with positions 1 `MPI_VIN`, 3 `MPI_RTN`, 4 `RESERVED`; female source output and male-to-female straight power cable as the exposed-contact safety rule; local regulation; no back-feed in either direction; reserved contact Platform-owned. Input-voltage range, current limit, cable size and length left open. | Not release-binding; first version |
