# AURIORA Module Port

**Interface Identifier:** `MPORT`
**Version:** `0.1`
**Status:** Draft
**Depends On:** [Architecture](../03-architecture.md), [Interfaces and Versioning](../05-interfaces-and-versioning.md), [AEL specification](./ael.md)

This is the versioned specification of the **Module Port**: the one connector through which a Module communicates with a Module Hub or directly with a peer Module, and of the **AURIORA Link Cable** that connects Module Ports. The architectural rules — what the port carries, that its links stay electrically independent, that it carries no primary Module power, that hub-less operation is the direct 1:1 link — live in [Architecture §7.1](../03-architecture.md#71-the-module-port) and [AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation) and are not repeated here. The electrical layer, frame and timing of the AEL links are the [AEL specification](./ael.md); the electrical layer and framing of `MCL` are the `MCL` binding specification when written. This file defines the connector, the contact roles, the cable and the mechanical and protection rules that are shared because the three links share one connector.

While this specification is Draft, it is not release-binding: no Module, Hub or cable may claim Released conformance until the open items in Section 8 are resolved and the specification is versioned to a `1.x` release. Section 8 separates what this Draft has **settled** from what is still **open**.

## 1. Purpose

A Module that takes part in a multi-Module installation needs a management link to a Hub and two event links — one in, one out — to its peers. The Module Port packages the three as electrically independent links in one connector and one cable, so that a Module is connected with one plug, cannot be cross-connected between its own links, and uses the same plug whether the other end is a Hub or a peer Module. It carries nothing else: no primary power ([Module Power Interface](./module-power.md)), no service connection (the direct local transport), no Unit signal.

## 2. Topology

```text
Module ── Link Cable ── Module Hub, Module Port n        (managed; MCL + AEL IN + AEL OUT in use)
Module ── Link Cable ── Module                           (direct 1:1; AEL IN + AEL OUT in use, MCL idle)
Hub, Hub-to-Hub link port ── Link Cable ── Hub, Hub-to-Hub link port   (AEL only; MCL idle or MCL cascading, open)
```

- A Module provides **exactly one** Module Port where it provides `MCL`, AEL IN or AEL OUT at all. A Module that provides none — a USB-only Module — has no Module Port and is conformant.
- A Module Hub provides one Module Port per Module it can connect and, where it provides Hub-to-Hub AEL links, one Module Port connector per link, labeled as such. Port counts are product decisions ([AES-HUB-002](../03-architecture.md#aes-hub-002-port-independence-and-scale-interoperability)).
- **Hub-less operation is the direct 1:1 link.** Two Modules joined by one Link Cable exchange AEL events in both directions with no infrastructure; each is managed over its own direct local transport, and the `MCL` pair joins two idle responder ends — a Module is never an `MCL` master ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)). Three or more Modules in one event exchange use a Module Hub. A chain of Modules without a Hub is not a Platform topology ([AES-AEL-002](../05-interfaces-and-versioning.md#aes-ael-002-point-to-point-links-direct-and-routed-operation)).
- The **same connector, contact assignment and cable** apply to every Module Port on every device. A Hub-side port is not the mirror image of a Module-side port; the crossover lives in the cable (Section 5).

## 3. Connector

- **Form.** M8, 8-position, A-coded circular connector, IEC 61076-2-104 form, panel-mounted on the device.
- **Gender.** **Female** on every device — Module, Hub Module Port, Hub-to-Hub link port. No device carries a male Module Port connector; every cable end is male.
- **Rating.** The connector family's contact rating is comfortably above anything three differential links need, and AES fixes no current or voltage figure for the Module Port: it carries signals only. A design that wants to exploit the family's rating for anything else is outside this specification.
- **Cross-mating.** The M8 8-position insert is not intermateable with the M8 3- and 4-position inserts; in particular a [Module Power Interface](./module-power.md) plug does not enter a Module Port and a Link Cable does not enter a power input. A product that carries any *other* M8 8-position connector verifies harmlessness in both directions per the Hardware Design Guide and records it; the preferred answer is not to.
- **Labeling.** On a Module the connector is labeled `MODULE PORT`. On a Hub, Module-facing ports are labeled `MODULE PORT` with their port number and Hub-to-Hub link ports `HUB LINK` with theirs. The labels `AEL IN`, `AEL OUT` and `MCL` name links, not connectors, and do not appear on an enclosure.

## 4. Contacts

Eight contacts carry three differential links, one reference and one reserved contact:

| Contact role | Net on the device | Link | Notes |
|---|---|---|---|
| `MCL_P` | `MCL_P` | `MCL` | Half-duplex differential pair, non-inverting; one pair per Module Port ([Interfaces and Versioning §5.1](../05-interfaces-and-versioning.md#51-transport-bindings)) |
| `MCL_N` | `MCL_N` | `MCL` | Inverting |
| `AEL_IN_P` | `AEL_IN_P` | AEL IN | Received pair, non-inverting; terminated at this device ([AEL §4](./ael.md#4-electrical-layer)) |
| `AEL_IN_N` | `AEL_IN_N` | AEL IN | Inverting |
| `AEL_OUT_P` | `AEL_OUT_P` | AEL OUT | Driven pair, non-inverting; not terminated at this device |
| `AEL_OUT_N` | `AEL_OUT_N` | AEL OUT | Inverting |
| `GND` | `GND` | reference | Signal reference of all three links, connected to the device's ground. Not a power return: no current is intentionally carried on it |
| `RESERVED` | — | — | **Not connected** on any device: no pull, no ground, no sense, no signal. Wired through in the cable. Its function, if any, is defined only by a new version of this specification, never by a Module or Hub design |

- **Why three pairs and not two.** AEL is two simplex links, not one bidirectional one: one driver per pair, no arbitration, no retransmission, and a frame whose start *is* the event's timestamp. Folding AEL IN and AEL OUT onto one half-duplex pair would let two legitimate events collide with no recovery, or would require a medium-access rule that makes a Module's event latency depend on its peer's traffic; both were rejected in [EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md). `MCL`, a polled request/response link, is half duplex on one pair for the same reason in reverse: it has a natural master and nothing to gain from a second pair.
- **Polarity naming.** `P` is the non-inverting and `N` the inverting side of each pair, as in the AEL specification; the RS-485 letters `A`/`B` are not used, because their polarity meaning differs between vendors.
- **One assignment everywhere.** The mapping of contact roles to the eight positions is identical on a Module, on a Hub's Module Ports and on its Hub-to-Hub link ports. The Hub's `MCL` end is the polling master and its AEL ports are router ports, but that is a difference in what drives each pair, not in where the pair sits.
- **Position numbering — OPEN.** Which of the eight positions carries which contact is assigned in the first `1.x` release of this specification, together with the `MCL` binding's electrical profile, under three constraints: the two contacts of each pair sit on **adjacent positions**; `GND` sits where it best serves all three pairs; and the assignment allows the Link Cable's crossover (Section 5) to be built with one twisted pair per link. Until then the contact roles, their nets and the cable wiring by role are settled; only the numbers are not.
- **Shield.** The connector shell is the cable shield's termination and bonds to the device's chassis or shield ground at the point of entry per the Hardware Design Guide; the `GND` contact is the signal reference, the shell is the shield, and they are not the same conductor in the cable.

## 5. AURIORA Link Cable

The **AURIORA Link Cable** is the only cable for a Module Port. It is a straight-through cable for `MCL`, `GND`, `RESERVED` and the shield, and a **crossover** for the two AEL links: what leaves one end as AEL OUT arrives at the other as AEL IN.

| End X contact | ↔ | End Y contact |
|---|:-:|---|
| `AEL_OUT_P` | ↔ | `AEL_IN_P` |
| `AEL_OUT_N` | ↔ | `AEL_IN_N` |
| `AEL_IN_P` | ↔ | `AEL_OUT_P` |
| `AEL_IN_N` | ↔ | `AEL_OUT_N` |
| `MCL_P` | ↔ | `MCL_P` |
| `MCL_N` | ↔ | `MCL_N` |
| `GND` | ↔ | `GND` |
| `RESERVED` | ↔ | `RESERVED` |
| shell (shield) | ↔ | shell (shield) |

- **Non-oriented.** The mapping is its own inverse, so the two ends are identical and the cable has no direction. Either end goes into either port.
- **Polarity preserved.** `P` connects to `P` and `N` to `N` on every pair; the crossover exchanges *links*, never the two sides of a pair.
- **One twisted pair per link.** `MCL_P`/`MCL_N`, `AEL_OUT_P`/`AEL_OUT_N` and `AEL_IN_P`/`AEL_IN_N` are each one twisted (or otherwise coupled) pair of the cable; `GND` and `RESERVED` are the remaining conductors. A pair is never split across two physical pairs of the cable.
- **Shielded.** An overall shield terminated 360° to the connector shell at both ends. The shield is not `GND`.
- **Connectors.** M8 8-position A-coded **male** at both ends, matching Section 3.
- **Impedance, conductor size and length — OPEN.** The pair impedance follows the receiver-side termination the AEL and `MCL` specifications fix (120 Ω is the AEL reference assumption), and the maximum length is validated at the AEL and `MCL` bit rates with real cable before `1.x` (Section 8). Until then a cable states the assumption it was built to.
- **Crosstalk.** Continuous `MCL` traffic shares the cable with AEL frames judged on the timing of their reference instant. The isolation the cable must provide between the `MCL` pair and the AEL pairs is a requirement of this specification, characterized and fixed before `1.x` ([Architecture §7.1](../03-architecture.md#71-the-module-port)).
- **Marking.** A Link Cable is marked `AURIORA LINK` so that it is distinguishable from a generic M8 8-position cable at a glance.

### 5.1 Generic cables are not Link Cables

A generic **straight-through** M8 8-position cable connects `AEL_OUT` to `AEL_OUT` and `AEL_IN` to `AEL_IN`: two drivers on one pair, two terminated receivers on another. It is **not compatible** with the Module Port, and no AEL event crosses it. Because such a cable will eventually be plugged in, every Module Port SHALL:

- **survive it indefinitely** — two AEL drivers in contention and two terminated receivers with no driver SHALL cause no damage at either end, which follows from the RS-485-class transceiver requirements of the AEL specification and is verified, not assumed;
- **produce no valid AEL frame** on any link while it is connected, being connected or being removed — the fail-safe and idle rules of [AEL §4](./ael.md#4-electrical-layer) apply to the contention case as to every other fault;
- **make the fault visible** where the device can — an `MCL` link that never sees its master, an AEL IN that never leaves idle — through the ordinary link-state and counter observability of the Hub and the Module, not through a special cable-detection mechanism, which is not defined.

## 6. Mechanical, Protection and Hot-Plug

- **Live insertion is normal.** A Module is connected to and disconnected from a running bench. Insertion or removal of a Link Cable SHALL NOT disturb any other Module Port of a Hub ([AES-HUB-002](../03-architecture.md#aes-hub-002-port-independence-and-scale-interoperability)) and SHALL NOT produce a valid AEL frame on any link ([AES-AEL-002](../05-interfaces-and-versioning.md#aes-ael-002-point-to-point-links-direct-and-routed-operation)). The contact make and break order of the connector family is not relied on for either property; the fail-safe receiver and the idle rules provide them.
- **Protection at the connector.** Every contact except `RESERVED` carries ESD and transient protection at the connector, ahead of termination and transceiver, per the Hardware Design Guide; `RESERVED` is protected too where the protection network is a common part, and is otherwise left open. The transceiver's internal ESD rating is not the protection strategy.
- **No back-drive.** An unpowered device SHALL NOT be back-driven through, and SHALL NOT source current into, any Module Port contact; this covers the `MCL` pair as well as the AEL pairs.
- **No power.** No contact of the Module Port carries a Module's primary operating power, and none is used as a power return. A design that needs to power something at the far end of a Link Cable has misidentified the interface ([AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation)).
- **Isolation — not required.** As for AEL, galvanic isolation is not part of this version. `GND` ties the two devices' references through the cable; a design sensitive to ground loops records the consequence in its design notes.

## 7. Compatibility

| Compatibility Class | Rule | Test |
|---|---|---|
| Physical | M8 8-position A-coded, female on every device; contact roles of Section 4 with one assignment on every port; position numbering per Section 8 once fixed. | Fit check of a Link Cable into every Module Port of the product and into every other M8 connector on it; a power plug does not enter a Module Port. |
| Cable | Link Cable wiring of Section 5: AEL crossover with polarity preserved, `MCL`/`GND`/`RESERVED` straight, one twisted pair per link, shield to shell both ends, male-to-male, marked. | Continuity and pair-assignment test of the cable against the table; both orientations verified identical. |
| Electrical | Signal-only port; no back-drive when unpowered; protection at the connector; survives a straight-through cable indefinitely. | Straight-through cable connected for the product's documented soak time with no damage and zero valid AEL frames; unpowered-device leakage per contact within the AEL and `MCL` transceiver limits. |
| Behavioral | Live insertion and removal disturb no other port and produce no valid frame; the `RESERVED` contact is open on the device. | 100 insertion/removal cycles with the bench armed: zero valid frames on every link of every port; `RESERVED` measured open. |
| Topology | Exactly one Module Port per Module; direct 1:1 with the same cable; Hub-to-Hub links on the same connector and cable; a downstream Hub's link port on an upstream Hub's Module Port carries cascaded `MCL` ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)). | Two Modules exchange events in both directions over one Link Cable with no Hub; the same cable connects each to a Hub port. |

## 8. Settled and Open Items

### 8.1 Settled in this Draft

Decided by [EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md); an implementer may build against these:

- M8 8-position A-coded connector, female on every device; one Module Port per Module; no separate AEL connector.
- Contact roles: `MCL_P`/`MCL_N` (one half-duplex pair), `AEL_IN_P`/`AEL_IN_N`, `AEL_OUT_P`/`AEL_OUT_N`, `GND`, `RESERVED`; `P`/`N` polarity naming; one assignment on every port.
- `RESERVED` not connected on any device, wired through in the cable, Platform-owned.
- The AURIORA Link Cable: AEL crossover, everything else straight, non-oriented, one twisted pair per link, shielded to the shells, male-to-male, marked.
- Generic straight-through cables incompatible; every port survives one indefinitely with no valid frame.
- Hub-less operation is the direct 1:1 link; Hub-to-Hub links on the same connector and cable.
- `MCL` roles by port kind: a Module Port's end is the master, a Hub-to-Hub link port's and a Module's end a responder; cascaded `MCL` runs from an upstream Hub's Module Port to a downstream Hub's link port ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)).
- No primary power on any contact; signal-only port; live insertion as a normal operation.

### 8.2 Open

Decided before this specification reaches `1.0`, from an explicit Platform decision or from bring-up measurement of the first Module, Hub and cable:

- **Position numbering** of the eight contacts, under the constraints of Section 4, together with the `MCL` binding's electrical profile.
- **Cable impedance, conductor size, shield construction and maximum validated length** at the AEL and `MCL` bit rates; **`MCL`-to-AEL crosstalk** limits in the shared cable.
- **`MCL` electrical profile, termination topology for a bidirectional pair, and line discipline** — line ownership at idle, initiation (the Hub polls), driver- and receiver-enable behavior, turnaround after end of frame and maximum response time, behavior when both ends drive, idle differential state — all from the `MCL` binding specification, none fixed by a constant here; the path element width and depth that cascading requires ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)).
- **Two `MCL` masters on one pair.** A Link Cable between two Hubs' Module Ports — rather than between a Hub's Module Port and its peer's Hub-to-Hub link port — puts two polling masters on one `MCL` pair. Each port detects and reports it as a cabling fault ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)); by what contention rule the binding detects it is decided with the binding, and the survival requirement of Section 5.1 already covers the electrical side.
- **`GND` return-current bound.** `GND` is a signal reference, not a power return, yet with several Modules on independent 12 V sources sharing signal ground through a Hub it can carry unintended return current. The bound, and whether it is met by a contact rating, a series impedance or isolation in a later version, is set from bring-up measurement.
- **Environmental rating** (IP class, temperature) of the connector and cable, as a Platform minimum or a product statement.

## 9. Version History

| Version | Change | Compatibility Impact |
|---|---|---|
| 0.1 (Draft) | Initial draft ([EDR-011](../edr/EDR-011-module-external-interfaces-and-power.md)): M8 8-position A-coded female Module Port carrying half-duplex `MCL`, AEL IN, AEL OUT, `GND` and one reserved contact with one assignment on every port; the AURIORA Link Cable as a non-oriented AEL-crossover cable; generic straight-through cables incompatible and survivable; direct 1:1 hub-less operation; Hub-to-Hub links on the same port. Position numbering, cable impedance and length, crosstalk limits and `MCL` electricals left open. | Not release-binding; replaces the standalone M8 3-position AEL ports of AEL `0.1` |
