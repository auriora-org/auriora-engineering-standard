# AURIORA Module Power Interface

**Interface Identifier:** `MPI`
**Version:** `0.2`
**Status:** Draft
**Depends On:** [Architecture](../03-architecture.md), [Interfaces and Versioning](../05-interfaces-and-versioning.md)

This is the versioned specification of the **Module Power Interface**: the primary external power input of an AURIORA Module and of a Module Hub. The architectural rules — that primary power and communication are on separate connectors, that a Module Hub does not power Modules, that USB is not the deployed power distribution, that the M8 3-position male form is reserved for this input — live in [AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation), [AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation) and [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope) and are not repeated here. Regulator, protection and layout practice is the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §6.

While this specification is Draft, it is not release-binding: no Module, Hub, power source or cable may claim Released conformance until the open items in Section 9 are resolved and the specification is versioned to a `1.x` release. The electrical figures of Section 5 are fixed by [EDR-015](../edr/EDR-015-module-power-interface-limits-and-connector-reservation.md); an implementer builds against them.

Throughout, *device* means a Module or a Module Hub, and *input* means the device's Module Power Interface input.

## 1. Purpose

Every device generates its own internal rails. What it needs from outside is one standard, safe, unambiguous DC input that a bench supply, a field power source or a future Platform power distributor can provide with one connector and one cable, independent of how many devices share the installation and independent of whether a Module Hub is present. The Module Power Interface is that input. It is not the Unit Interface's managed power (`UIF_PWR_VIN`, `UIF_PWR_EN`), which is a Module-to-Unit contract inside a Module; it is not USB power, which is an optional service convenience; and it is not carried on the [Module Port](./module-port.md).

The Platform standardizes the DC interface, not the supply behind it. What produces the 12 V — a mains adapter, a laboratory supply, a battery, a solar charge controller, a power distributor — is outside this specification; a source conforms by what it presents at its output (Section 6).

## 2. Topology

```text
External power source (mains adapter, bench supply, battery, solar controller, power distributor)
    M8 3-position FEMALE / socket-contact output
        │
        │  AURIORA Power Cable: male → female, straight
        │
    M8 3-position MALE / pin-contact input
Module or Module Hub
```

- One source output powers **one** device input over one cable. Passive splitting of a power cable is outside this specification; a device that powers several devices provides several outputs.
- Every Module and every Module Hub has its own input. A Module Hub does not power Modules; an installation does not depend on one central supply, and a source may sit next to the device it feeds rather than at the Hub ([AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation), [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope)).
- A future **power distribution device** providing several outputs is architecturally allowed. Its port count, total power, switching, sensing, enable, detection, protocol and fault behavior are not specified in this version; its own supply input is not required to use this interface where its total exceeds Section 5.

## 3. Connector

- **Form.** M8, 3-position, A-coded circular connector, IEC 61076-2-104 form.
- **Contact type and gender — the safety rule.** The device's input is a **panel-mounted male connector with pin contacts**. A source's output is a **female connector with socket contacts**. The power cable is **male / pin-contact at the source end, female / socket-contact at the device end**. Consequently a cable that is connected to a live source and disconnected from the device presents a **female** end with no exposed live contact, and the only male contacts in the system — device inputs and the source end of a cable — are energized by nothing but the source they are plugged into (Section 5). Because supplier vocabulary for "plug", "receptacle" and "socket" is not uniform, documentation names the contact type beside the gender: *male / pin-contact*, *female / socket-contact*.
- **Positions.** The M8 3-position A-coded insert populates positions **1, 3 and 4**; position 2 does not exist. This specification uses the insert's own numbering and the connector family's field-sensor convention (pin 1 supply, pin 3 return, pin 4 signal), so that a standard three-conductor M8 sensor cable wired 1-1, 3-3, 4-4 is a valid power cable.
- **Reservation.** The M8 3-position male / pin-contact panel form is reserved on every Platform device for this input and for nothing else ([AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation), [External Connector Register](../document-index.md#external-connector-register)). The female / socket-contact form is a source output and, otherwise, a measurement-side port only (Section 8).
- **Rating.** The connector family's rating for this insert — **3 A per contact, 60 V** — is the ceiling of this interface in every version. The two figures are independent: operating at 12 V does not raise the permitted current.
- **Labeling.** A device's input is labeled `POWER IN` with `12 V DC` and the DC symbol; a source's output is labeled `POWER OUT 12 V DC`. Labeling is in addition to the mechanical rule, never a substitute for it.

## 4. Contacts

| Position | Contact | Net on the device | Function |
|---:|---|---|---|
| 1 | `MPI_VIN` | `MPI_VIN` | Supply, **+12 V DC nominal** |
| 3 | `MPI_RTN` | `MPI_RTN` → device ground | Power return, 0 V |
| 4 | `RESERVED` | — | **Not connected** on any device and on any source: no pull, no ground, no sense, no enable, no identification, no signal. Wired through in the cable. Its function, if any, is defined only by a new version of this specification and never by a device, source or distributor design |

- **Return and ground.** `MPI_RTN` is the power return and is connected to the device's ground; how it meets the signal ground of the Module Port and the shield is a design decision recorded per the Hardware Design Guide. It is not a protective earth: the interface is SELV and defines no protective conductor.
- **Reserved contact.** Not to be used as protective earth, signal ground, sense, enable, identification or communication because it is available. A device SHALL tolerate any voltage between `MPI_RTN` and `MPI_VIN` on it without effect, since a future source may drive it.

## 5. Electrical

### 5.1 Voltage

| Figure | Value | Meaning |
|---|---|---|
| Nominal | **12.0 V DC** | The value a source is designed to provide and a device's regulators are designed around |
| Operating range at the device input | **10.0 V to 15.0 V** | The device meets its full specification anywhere in this range, including start-up |
| No-damage range | **0 V to 18 V**, and reverse polarity to **−18 V** | Indefinitely, without damage; operation is not required outside the operating range |
| Protection target | above 18 V | Transients beyond the no-damage range are clamped or survived per the Hardware Design Guide §6; the device's own protection, not the source, is the barrier |

The operating range is chosen so that a regulated 12 V source reaches the device through a real cable (Section 7), and so that a 12 V battery — under load, at rest, and under charge from a charger or a solar controller — is a conformant source without adaptation.

- **Brownout.** Below 10.0 V a device MAY cease to operate but SHALL do so in a defined way: no damage, no undefined output on any interface, no valid AEL frame, and automatic recovery when the input returns to the operating range, under the reset and recovery rules of [AES-MCI-007](../05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance). The threshold at which the device stops, and its hysteresis, are the device's and are documented.
- **Start-up.** A device starts at any voltage within the operating range, with the source's output already present (hot-plug) or rising.

### 5.2 Current

| Figure | Value | Meaning |
|---|---|---|
| Continuous | **2 A** per input, any 1 s average | The most a device draws in any operating state, anywhere in the operating range |
| Start-up | **3 A** per input, any 10 ms average | Regulator start-up and load steps; not the capacitive hot-plug inrush |
| Connector ceiling | 3 A per contact | Never exceeded by any figure of this interface |

- The limit is a current, not a power. A device whose load is constant-power draws its highest current at 10.0 V; it conforms if it stays under 2 A there, which places the practical device power under this profile at about 20 W. A device class that needs more is the case for a second, larger power profile ([EDR-015](../edr/EDR-015-module-power-interface-limits-and-connector-reservation.md)), never for a higher figure on this connector.
- **Hot-plug inrush.** Hot-plug into a live source is a normal operation. A device limits the charge its input capacitance draws on connection, declares its effective input capacitance at the connector, and a source declares the inrush its output tolerates without tripping; the Platform figure that reconciles the two is open (Section 9).

### 5.3 Device-side rules

- **Local regulation.** A device generates every internal rail from `MPI_VIN` with its own regulators; no rail of a device is provided by the source, and no device rail appears on the connector.
- **Protection at the input.** The input carries, per the Hardware Design Guide §6: reverse-polarity protection to the no-damage figure; overcurrent protection rated so that a device fault cannot ignite the device or the source's cable; transient protection at power entry sized for the field sources of Section 6 — battery and charger faults, load dump, ESD; input filtering so that the device meets its EMC obligations on a long unshielded power cable; and the inrush behavior above.
- **No energized male contacts — no back-feed onto the input.** A device that is powered from any other source — USB, an internal battery, a product-specific input — SHALL NOT present voltage on `MPI_VIN` when no source is connected to its input. The input path is unidirectional toward the device (an ideal-diode or equivalent power-path element, not a plain wire), so that the exposed male contacts are never energized by the device itself.
- **No back-feed onto USB or any other source.** Neither `MPI_VIN` nor any device rail SHALL back-drive a host's USB `VBUS` or any other external source connected to the device at the same time ([AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation)). A device that accepts both the Module Power Interface and USB power implements power-path protection in both directions and documents which source wins.

## 6. Power Source

A power source is anything that presents a conformant output. The Platform does not specify what produces the power: a mains adapter, a laboratory supply, a commercial 12 V supply whose output cable is re-terminated, a battery pack, a solar charge controller's load output or a Platform power distributor are all sources if their outputs meet this section. No source product is prescribed, and this specification does not bind the Platform to a supplier or to a mechanical form of supply.

- **Output.** One M8 3-position A-coded **female / socket-contact** connector per output, positions per Section 4, `RESERVED` open. One output feeds one device.
- **Voltage.** Within **11.4 V to 15.0 V** at the output across the output's rated load, from no load to 2 A continuous. A regulated supply is set to 12.0 V; a battery-backed source may move within the band as its state of charge and its charger dictate. A source whose output can exceed 15.0 V in normal operation — an unregulated adapter, a charger with an equalization mode on the load terminals — is not a conformant source until regulated into the band.
- **Current and protection.** Each output supplies 2 A continuous and 3 A for start-up, and protects itself against overcurrent and short circuit independently of the device and of any other output; a device's protection is the second barrier, not the first. What an output does after a fault — latch, retry, report — is a source product decision in this version; that it does not take other outputs with it is not.
- **Hot-plug.** An output tolerates the connection of a device presenting the declared input capacitance without tripping (Section 5.2).
- **Marking.** `POWER OUT 12 V DC` at each output.

## 7. AURIORA Power Cable

- **Connectors.** M8 3-position A-coded **male / pin-contact** at the source end, **female / socket-contact** at the device end. The same cable extends an installation: its female end is also what a source presents, so cables are chained at the cost of their summed drop.
- **Wiring.** Straight: 1-1, 3-3, 4-4. Three conductors; position 4 wired through so that a future Platform-defined function needs no new cable.
- **Conductors and length.** Conductor cross-section **at least 0.25 mm²**, cable rated **3 A**. A cable states its length. The length is chosen so that the device's input stays at or above 10.0 V at the device's maximum continuous current from the source's minimum output voltage; the Hardware Design Guide §6.2 gives the figures for common conductor sizes.
- **Marking.** `AURIORA POWER 12 V DC`.
- **Not a Link Cable.** A power cable and a Link Cable cannot be confused at the connector — different inserts — and are marked differently.
- **Never male-to-male.** No Platform cable carries an M8 3-position male / pin-contact connector at both ends; such a cable would be the only way to join a source output to a female measurement port (Section 8).

## 8. Mis-mating

The M8 3-position A-coded form is also the common sensor and electrode connector, and a product may carry it on measurement-side ports under [AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation) — in the **female / socket-contact** form only. The gender rule makes every physically possible mis-mating harmless:

| Mis-mating | Result |
|---|---|
| Power cable female (live) end → female measurement port | Does not mate |
| Power cable male end → female measurement port | Mates. The male end is live only when its other end is in a source output, in which case it is not free; otherwise it is an unenergized device input or nothing. Harmless |
| Measurement cable female end → device power input | Mates. The input is unenergized from inside (Section 5.3) and protected; the measurement cable sees a reverse-blocked, protected input. Harmless provided the measurement port's own voltage is within the input's no-damage range, which SELV measurement ports are |
| Any 3-position plug → Module Port, Link Cable → power input | Do not mate ([Module Port](./module-port.md)) |

A product that carries M8 3-position female measurement ports records this table for its own ports — in particular that nothing those ports can present exceeds the input's no-damage range — and labels them with their function and never with a power symbol.

## 9. Compatibility, Settled and Open Items

### 9.1 Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | M8 3-position A-coded; male / pin-contact input on the device, female / socket-contact output on the source; positions 1/3/4 as Section 4; power cable male-to-female, straight, ≥ 0.25 mm²; no other male / pin-contact 3-position connector on the product. | Fit check of the power plug into every other M8 connector of the product; mis-mating table of Section 8 recorded where any female 3-position port exists. |
| Electrical | 12.0 V nominal; full function over 10.0–15.0 V; no damage over 0–18 V and to −18 V; ≤ 2 A continuous and ≤ 3 A start-up; defined brownout; local regulation of every rail; reverse-polarity, overcurrent, transient and hot-plug protection; no voltage on `MPI_VIN` when the input is unconnected and the device is otherwise powered; no back-feed onto USB or any other source; `RESERVED` open on the device. Source output within 11.4–15.0 V, per-output protection. | Full function at 10.0 V and 15.0 V; 18 V and −18 V applied for one hour with no damage; current at 10.0 V measured ≤ 2 A over 1 s and ≤ 3 A over 10 ms at start-up; input lowered through brownout and restored with defined behavior and recovery; short-circuit and overcurrent on the input contained; hot-plug into a live source 100 cycles without a protection trip or a reset of the source's other outputs; `MPI_VIN` measured at 0 V with the device running from USB; `VBUS` measured undriven with the device running from `MPI_VIN`; `RESERVED` measured open and swept between 0 V and `MPI_VIN` without effect. |
| Behavioral | The device operates fully from the Module Power Interface alone; USB powering, where offered, is declared with its limits; the device documents typical, maximum and start-up current and its input capacitance. | Full-function test on `MPI_VIN` only; declared USB-power modes exercised and refused modes verified as refused. |

### 9.2 Settled

Decided by [EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md) and [EDR-015](../edr/EDR-015-module-power-interface-limits-and-connector-reservation.md):

- M8 3-position A-coded; male / pin-contact input on every device, female / socket-contact output on every source; male-to-female straight power cable, never male-to-male.
- Positions 1 `MPI_VIN`, 3 `MPI_RTN`, 4 `RESERVED`, following the insert's numbering and the connector family's convention; `RESERVED` not connected on any device, wired through in the cable, Platform-owned.
- 12.0 V nominal; 10.0–15.0 V operating; 0–18 V and −18 V no-damage; 2 A continuous, 3 A start-up; 3 A / 60 V connector ceiling; source output 11.4–15.0 V; cable ≥ 0.25 mm² rated 3 A, length by the voltage rule.
- Every rail regulated locally; defined brownout; no energized male contacts; no back-feed in either direction.
- Primary power never on the Module Port; a Hub powered through this input and never obliged to power Modules; a power distributor allowed and unspecified; the supply behind a source unspecified.
- The male / pin-contact 3-position form reserved for this input; the female form a source output or a measurement-side port with a recorded mis-mating analysis.

### 9.3 Open

Decided before this specification reaches `1.0`:

- **Inrush figure** — the input capacitance a device may present and the inrush an output tolerates, from the first source and device measured together.
- **Measured cable validation** — the computed length figures confirmed on built cables at 2 A.
- **Function of the reserved contact**, if any.
- **Source fault behavior** as a Platform rule, if the first power distributor shows one is needed.
- **Environmental rating** (IP class, temperature) of connector and cable, as a Platform minimum or a product statement.

## 10. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.2 (Draft) | Figures fixed ([EDR-015](../edr/EDR-015-module-power-interface-limits-and-connector-reservation.md)): 10.0–15.0 V operating, 0–18 V and −18 V no-damage, 2 A continuous and 3 A start-up, 3 A / 60 V connector ceiling; source output 11.4–15.0 V with per-output protection; cable ≥ 0.25 mm², rated 3 A, length by the voltage rule, never male-to-male; defined brownout; a Module Hub is a device of this interface; pin-contact / socket-contact terminology; male 3-position form reserved, mis-mating table for female measurement ports; power sources unspecified as products. | Not release-binding. Tightening of a Draft: a `0.1` device that declared figures inside the new ones conforms unchanged |
| 0.1 (Draft) | Initial draft ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)): M8 3-position A-coded male input at 12 V DC nominal with positions 1 `MPI_VIN`, 3 `MPI_RTN`, 4 `RESERVED`; female source output and male-to-female straight power cable as the exposed-contact safety rule; local regulation; no back-feed in either direction; reserved contact Platform-owned. Input-voltage range, current limit, cable size and length left open. | Not release-binding; first version |
