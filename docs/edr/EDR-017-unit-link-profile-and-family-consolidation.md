# EDR-017: The Unit Link Profile and Unit Interface Family Consolidation

## Status

Proposed

*Self-authored draft pending maintainer acceptance per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Unit or Module relies on this profile.*

Supersedes the profile decisions of [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md) (items 1–6 and 8) and the connector and pin assignment of [EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md). EDR-005's separation of management model from transport, and its identifier pattern, stand as reasoning; the profiles they produced are withdrawn. Both records are annotated, not rewritten ([AES-EDR-002](../08-decisions-and-governance.md#aes-edr-002-decision-record-structure-and-immutability)).

## Context

The Unit Interface of AES `0.2.0` to `0.13.0` was built for a Unit that sits beside its Module: three profiles — [`UIF-I2C-6`](../interfaces/uif-i2c-6.md), [`UIF-MI2C-8`](../interfaces/uif-mi2c-8.md), [`UIF-MSPI-14`](../interfaces/uif-mspi-14.md) — on 1.00 mm JST SH connectors, carrying single-ended I²C or SPI plus discrete `UIF_PWR_EN`, `UIF_READY`, `UIF_IRQ_N` and, on one profile, `UIF_RESET_N`.

The first Module designed in earnest against it, the Plant Electrophysiology Module (APEM), showed the assumption to be wrong for the laboratory the Platform is for. A plant under a bell jar is measured by APEM's electrodes and, at the same time, by an Environmental Sensor Unit (AENU) that must be *under the jar* while APEM must not be. The same holds for a canopy sensor above a bench, a soil probe in a pot, a spectral head at a leaf: the Unit belongs where the measurement is, the Module belongs where the power, the host and the other Modules are, and the distance between them is centimetres on one bench and metres on the next.

[EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md) had already conceded the point without resolving it: it justified `UIF-MI2C-8`'s second ground contact with "metres of thin field wiring", and listed bus capacitance budget and maximum cable length as open. Single-ended I²C at 400 pF total, with no isolation path and a ground reference carried on one thin conductor beside the supply return, does not become a field interface by adding a ground; it stays a board-level bus with a cable attached.

Three facts made the direction obvious:

- The Platform already has a wired differential, point-to-point, half-duplex, polled management link on a small circular connector: `MCL` in the Module Port ([EDR-011](./EDR-011-module-external-interfaces-and-power.md)). A Module-to-Unit link with the same electrical class and framing is one transceiver class and one line discipline for the whole Platform.
- Every planned Unit — AENU, ASPU, ASOU, AWNU, ACTU, AGEU — has its own controller and a Unit API. No Passive Unit exists or is planned; `UIF-I2C-6` had no candidate.
- `UIF-MSPI-14` had no realization, an open electrical layer and a provisional status by its own record. It occupied a cell the Platform has not yet needed.

This is a Platform interface decision — a new Unit Interface Profile, the withdrawal of three, changes to normative Unit requirements and to the EEPROM metadata field set, and a new external connector assignment — and requires an EDR under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger) and [AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation).

## Alternatives Considered

### Transport

| Alternative | Assessment |
|---|---|
| **Keep I²C and fix the length** (bus buffers, lower clock, thicker cable) | Rejected. Buffers add parts at both ends without changing what the bus is: single-ended, capacitance-bounded, referenced to one conductor, with no isolation path. The ground-shift problem EDR-005's second ground was meant to halve is the problem, not its magnitude. |
| **Multidrop RS-485 bus with Unit addresses** | Rejected. Fewer transceivers per Module, but address allocation returns — exactly the collision problem [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-one-unit-per-port) had to legislate for I²C — per-port power switching and fault containment are lost, "which Unit is where" becomes a configuration question instead of a discovery answer, and one faulted Unit or damaged cable takes the bus with it. |
| **Point-to-point RS-485-class link per Unit Port, the port polling** | **Chosen.** The Module Port model one level down: one port, one Unit, one transceiver, one switched and current-limited supply, no addressing, any Unit on any port. The port index is topology, not identity. Per-port cost is a transceiver, a load switch and a connector — roughly what an I²C port plus its protection cost already. |
| **CAN** | Rejected. A second transceiver class beside the Platform's RS-485-class links, an arbitration model built for multidrop that a polled point-to-point link never exercises, and a frame format that constrains the Unit API's payload for no gain. |
| **Full-duplex, two pairs (six positions), Unit may initiate** | Rejected for this version. Lets a Unit raise an event unprompted, but the M8 6-position form is rarer and costlier, the event latency the portfolio needs is milliseconds and polling serves it, and parity with `MCL` is worth more than an unsolicited path. Recorded as a review criterion. |

### Profile family

| Alternative | Assessment |
|---|---|
| **Add the new profile beside the three existing ones** | Rejected. Two host port designs, two discovery mechanisms, two fixture sets, for the same cell. EDR-005's own principle: a profile fills an empty cell; it does not fragment an occupied one. |
| **Keep `UIF-MI2C-8` as the in-enclosure profile** | Rejected. Inside the enclosure the new link costs one transceiver pair per Unit and buys one host design; the internal-realization clause of the new profile lets an internal Unit use a product-chosen connector without a second profile. |
| **Keep `UIF-I2C-6` and the Passive execution model** | Rejected. No Passive Unit exists or is planned. The model ties host firmware to a Unit's internal devices, which is what [AES-UNIT-003](../03-architecture.md#aes-unit-003-replaceability-without-source-modification) exists to prevent; a board without a reusable contract is a Module subassembly, and a controller-less sensor is a Unit's internal sensor, as the Soil Unit's Modbus probe already is. A Unit controller and a transceiver cost about a dollar. |
| **Keep `UIF-MSPI-14` as the streaming profile** | Rejected. The cell is real — deterministic, streaming and time-reference needs exist — but the profile was speculative, unrealized and electrically open. The cell stays open in the family table, to be filled by a profile designed against the first Unit that needs it. |
| **Withdraw all three, define one** | **Chosen.** Nothing Released stands behind any of them; AENU-01's rework had not reached hardware. The cost of withdrawal is three stub files now; the cost of keeping them is a migration obligation later. |

### Connector, power and gender

| Alternative | Assessment |
|---|---|
| **M8 4-position A-coded** | **Chosen.** Unassigned in the External Connector Register; the smallest IEC circular form with four contacts; the industry's standard sensor cordset, so the Unit cable is a procurement item. The one physical mis-mating — a 3-position male plug entering a 4-position female socket — is made harmless by placing power on the same positions 1 and 3 as the Module Power Interface. |
| M8 4-position B-coded | Rejected. Excludes the 3-position plug mechanically, but rarer, costlier, fewer cordsets, and the exclusion buys nothing once the A-coded mis-mating is harmless by construction. |
| M12 4-position | Rejected. About half again the panel area per port on a Module whose panel is already the constraint; more current than a Unit needs. Remains the candidate for a higher-power profile. |
| M8 8-position | Rejected. Reserved for the Module Port; four contacts suffice. |
| **`UIF_PWR_VIN` in the Module Power Interface band (10.0–15.0 V)** | **Chosen.** Lower drop over metres of 0.25 mm² cable, local regulation on the Unit as on a Module, and the mis-mating with the power interface lands in band on both sides. |
| 5 V regulated at the port | Rejected. Significant drop on long thin cable, a second regulated external rail on the Module, and a 12 V mis-mating that would have to be protected against on every Unit. |
| **Female Unit Port on the Module, male input or captive cable on the Unit, straight male-to-female cable** | **Chosen.** The power-cable pattern: live free contacts are female, male contacts are inputs nothing energizes from inside ([AES-MOD-006](../03-architecture.md#aes-mod-006-external-connector-reservation)). The live power cable cannot enter a Unit at all. Matches the sensor cordset market. |
| Female on both devices, male-to-male cable (the Module Port pattern) | Rejected. Works, but puts a non-live female on the Unit for no reason, needs a male-to-male 4-position cordset, and loses the "a live cable never enters a Unit" property. |

### Isolation

| Alternative | Assessment |
|---|---|
| Mandatory on every Unit Port | Rejected. Robust, but an isolated supply and transceiver per port on every Module, including ones whose reference is not a measurement reference. |
| Default (SHOULD), deviation noted | Rejected as the rule, though close: the decision is genuinely product-specific, and a default would be read as a requirement. |
| **Product decision, documented with the ground-loop analysis** | **Chosen.** The profile permits both and makes them indistinguishable to the Unit; a Module records its choice. A measurement front end that shares its reference with electrodes isolates; a Hub-like device may not. |

## Decision

1. A new Unit Interface Profile, **`AURIORA UIF-RS485-4`** ([`docs/interfaces/uif-rs485-4.md`](../interfaces/uif-rs485-4.md), version `0.1`, Draft), is the Platform's Unit Interface Profile. It is point to point, one Unit per port, the port polling, on one half-duplex RS-485-class differential pair with power and return: M8 4-position A-coded, positions 1 `UIF_PWR_VIN`, 2 `UIF_LINK_P`, 3 `GND`, 4 `UIF_LINK_N`.
2. `UIF-I2C-6`, `UIF-MI2C-8` and `UIF-MSPI-14` are **withdrawn**. Their files remain as notices; their full text stays in the AES `v0.13.0` tag. No artifact migrates: none was Released.
3. The **Passive execution model is withdrawn**. Every Unit contains a controller and exposes a versioned Unit API — the Managed model, now the only one. The EEPROM execution-model record is withdrawn with it.
4. The discrete Unit Interface signals `UIF_PWR_EN`, `UIF_READY`, `UIF_IRQ_N`, `UIF_RESET_N`, `UIF_I2C_*` and `UIF_SPI_*` are withdrawn. Their meanings live on as **link states and messages**: *enable*, *disable*, *ready* and *events pending*, with the semantics the signals had. The `UIF_` signal set is `UIF_PWR_VIN`, `GND`, `UIF_LINK_P`, `UIF_LINK_N`.
5. Discovery is unchanged in content and order: the [EEPROM Metadata](../06-eeprom-metadata.md) record, served over the link by the Unit controller, validated per [AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order). Presence is a valid answer. [AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence) is restated in link terms with the same seven steps.
6. [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-one-unit-per-port) becomes **one Unit per port**: no addressing on any profile, the port index held as topology separate from identity. [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration) becomes **profile declaration**: every Unit declares `UIF-RS485-4`; a need the profile cannot meet — deterministic transfer, streaming, sub-millisecond latency, a hardware time reference — is a new profile by EDR, never a Unit-specific contact.
7. `UIF_PWR_VIN` is in the **Module Power Interface band**, 10.0–15.0 V, switched and current-limited per port, with the Unit's discovery domain powered from it and its functional domain switched locally on *enable*. Recovery is a port power cycle.
8. **Galvanic isolation** of a Unit Port is a product decision, documented with its ground-loop analysis.
9. The Unit Link and `MCL` share **one electrical profile and one framing**, written as one binding when the `MCL` binding is written. Until then both are open in the same terms.
10. The **External Connector Register** assigns the M8 4-position A-coded form: female / socket-contact panel to the Unit Port; male / pin-contact panel to a Unit input; male-to-female cable as the Unit cable; male-to-male and female-to-female cables prohibited.
11. A Unit MAY be realized **internally** with a product-chosen connector on the same four conductors, and MAY carry a **captive cable** instead of a panel connector. The recommended internal connector is the **JST SH 1.00 mm 4-position** with the profile's position assignment, so that internal pinouts do not diverge between products and an internal Unit reaches an external port through one adapter. This extends the Platform's admitted vendor naming in the same bounded way as [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md): the family and pitch are named because a pinout recommendation without a connector is not one; the sub-series and part number stay open.
12. The profile identifier pattern becomes **`UIF-<transport>-<positions>`**; the `[M]` of EDR-005's pattern carried the execution model and has nothing left to carry.
13. **AENU-01 adopts `UIF-RS485-4`**, superseding EDR-005's consequence; its `UIF-MI2C-8` rework is withdrawn before hardware. The Plant Electrophysiology Module is the first host, with its Unit Port count a product decision recorded in its product table.

## Rationale

The decision applies a pattern the Platform already trusts. The Module Port put a Module's management and event links on a small circular connector with a differential, polled, half-duplex link and a cable that can be metres long; the Unit Port does the same for a Unit, with the port as master, the same transceiver class and the same framing. One pattern, two levels, is cheaper to specify, build, test and explain than two patterns at one level each.

Moving the discrete signals into the protocol is what makes four conductors enough, and it loses nothing the signals provided. `UIF_PWR_EN` was a host decision expressed as a level; *enable* is the same decision expressed as a message, and the Unit still switches its functional domain locally. `UIF_READY` was a Unit status expressed as a level; *ready* is the same status in every answer, and a Unit that does not answer is not ready — which is the stronger definition. `UIF_IRQ_N` was a latency optimization whose cause had to be read over the bus anyway; *events pending* in the status answer costs one poll of latency and no contact. `UIF_RESET_N` had already been rejected on `UIF-MI2C-8` in favour of a power cycle, for reasons that hold here unchanged.

Withdrawing Passive removes an execution model that had no Unit and a contract that pulled against the Platform's replaceability rule. The cost it was meant to save — a microcontroller on a trivial Unit — is now a dollar, and the trivial sensor has a better home as a Unit's internal device.

Point to point rather than multidrop is the choice with the longest consequences, and it is the Module Port's choice for the same reasons: containment, independent power control, no configuration, and a discovery answer that is also a location. The price is one transceiver per port, which the Platform pays once per port on a Hub already.

The connector decision is the one place the Platform spends a register entry, and the mis-mating analysis is what earns it. The 3-position power plug enters a 4-position socket; rather than fight that with coding, the profile puts power on the same two positions as the power interface, so the one powered mis-mating in each direction delivers the right voltage to the right contacts and a floating line to an open one. A property that holds by construction is worth more than one that holds by a rarer part.

Isolation is left to the product because the Platform cannot know the Module's reference. A Hub-class device with no measurement front end has nothing to protect; an electrophysiology front end with its electrode reference on the same ground as a Unit under a bell jar, metres away, has everything to protect. The profile's job is to make both choices conformant and invisible to the Unit; the Module's job is to record the choice.

## Consequences

- The Platform has **one** Unit Interface Profile with one connector form, and the position-count discriminator that kept the earlier profiles from mating is no longer needed between profiles; it remains in the identifier because it is the connector's name.
- The **Passive execution model, the discrete `UIF_` control signals and the Unit API transport address** are withdrawn from [Terminology](../02-terminology.md), [Architecture §5](../03-architecture.md#5-unit-design), [Interfaces and Versioning §3](../05-interfaces-and-versioning.md#3-interface-contracts) and [EEPROM Metadata](../06-eeprom-metadata.md). The EEPROM fixed header is unchanged; two TLV records are withdrawn.
- **AES-UNIT-006** becomes *Declared Capabilities and Unit API*; **AES-UNIT-007** is restated for the link; **AES-IF-009** and **AES-IF-010** are rewritten under new titles with the same identifiers.
- The **External Connector Register** gains three M8 4-position rows; the former "Unassigned" row is consumed.
- **Module design.** A Module that accepts Units carries Unit Ports on its panel; the count is a product decision and part of the product contract. A Module that offers no Unit Port is conformant. A Module's Unit Ports are measurement-side connectors under [AES-MOD-005](../03-architecture.md#aes-mod-005-external-interfaces-and-power-separation) and draw their `UIF_PWR_VIN` from the Module's input, so a Module that cannot hold the band keeps its ports disabled.
- **AENU-01** retargets before hardware. The Spectral Unit (ASPU) is designed against this profile from the start.
- The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) rewrites its Unit Interface power section for the link, adds a Unit Port section beside the Module Port one, and lifts its rule that `UIF_PWR_VIN` is never on an external connector.
- The **Firmware Style Guide** and the **AI Engineering Knowledge Base** reference `UIF_READY`, the execution model and the I²C profiles; they are updated in their own rounds and are listed as pending in the Document Index until then.
- The profile is **Draft**: no Released conformance may be claimed until its framing, timing and electrical figures are fixed and it reaches `1.x`.
- A distributed hardware time reference, and deterministic or streaming transfer, remain recorded unmet needs, to be met by a new profile.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

Not resolved here; they are the open items of [`uif-rs485-4.md` §11.2](../interfaces/uif-rs485-4.md#112-open), decided with the `MCL` binding and from the first Module's and Units' bring-up: framing and message set; bit rate, turnaround, response and enable-to-ready bounds; termination and fail-safe figures; maximum validated length with and without a paired cable; maximum discovery-state current and minimum off-time; the Unit input's no-damage range; sleep and wake bounds; environmental rating.

## Affected Requirements / Documents

- [`docs/interfaces/uif-rs485-4.md`](../interfaces/uif-rs485-4.md) — the new profile (new).
- [`docs/interfaces/uif-i2c-6.md`](../interfaces/uif-i2c-6.md), [`uif-mi2c-8.md`](../interfaces/uif-mi2c-8.md), [`uif-mspi-14.md`](../interfaces/uif-mspi-14.md) — withdrawn notices; [`docs/interfaces/README.md`](../interfaces/README.md).
- [Terminology](../02-terminology.md) — Unit, Passive Unit, Managed Unit, Unit Interface Profile; Unit Port and Unit Link added.
- [Architecture §5.1](../03-architecture.md#51-execution-model-and-transport), [AES-UNIT-006](../03-architecture.md#aes-unit-006-declared-capabilities-and-unit-api), [AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence), [AES-UNIT-001](../03-architecture.md#aes-unit-001-electronic-identity), [§6](../03-architecture.md#6-default-controller-platform-strategy).
- [Interfaces and Versioning §3.1–3.2](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles), [AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles), [AES-IF-009](../05-interfaces-and-versioning.md#aes-if-009-one-unit-per-port), [AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration), [§5.1](../05-interfaces-and-versioning.md#51-transport-bindings).
- [EEPROM Metadata](../06-eeprom-metadata.md) — purpose, [AES-EEPROM-002](../06-eeprom-metadata.md#aes-eeprom-002-deterministic-validation-order), [AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-profile-and-api-metadata).
- [Naming and Identity §5](../04-naming-and-identity.md#5-product-numbers-and-revisions) — Unit Port count as product contract.
- [Document Index](../document-index.md) — interface table, retired identifiers, External Connector Register, AOID note, pending companion updates.
- [`examples/worked-example-unit-interface-profile-selection.md`](../../examples/worked-example-unit-interface-profile-selection.md) — withdrawn; [`worked-example-unattended-field-deployment.md`](../../examples/worked-example-unattended-field-deployment.md) — profile references.
- [EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md), [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md) — annotated as superseded.

## Future Review Criteria

Revisit if: a Unit needs unsolicited, sub-poll-latency events, which would argue for the two-pair form; the first Units cluster at the profile's payload or rate limits, which would argue for the open high-bandwidth cell; a Passive-class need appears that a Unit's internal sensor cannot absorb; the Module panel proves unable to carry the Unit Ports a product needs, which would argue for a higher-density connector; or bring-up shows the discovery-state current or the 12 V band to be the wrong choice for very small Units.
