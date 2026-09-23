# EDR-011: Module External Interfaces — Module Port, Module Power Interface and USB

## Status

Accepted (2026-09-18)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module or Module Hub relies on this architecture.*

**Supersedes** items 8 and 9 of the Decision of [EDR-008](./EDR-008-auriora-event-link.md) — the M8 3-position AEL connector and the retention of standalone AEL ports — and resolves the Module Port physical-layer and `MCL` duplex-model items left open by [EDR-007](./EDR-007-module-control-interface-and-module-hub.md). Everything else in EDR-007, EDR-008, [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md) and [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md) stands.

## Context

AES had, until this record, three partial answers to the question *what does the outside of a Module look like*:

1. **AEL** had a physical layer — an M8 3-position A-coded connector per standalone AEL IN and AEL OUT port, pin 1 `GND`, pin 2 `AEL_P`, pin 3 `AEL_N` — inherited from SYNC ([EDR-006](./EDR-006-module-synchronization-interface.md)), with gender, keying and cross-mating explicitly open "against the full AURIORA connector inventory".
2. The **Module Port** — one cable carrying `MCL`, AEL IN and AEL OUT to a Module Hub — was architectural intent only. Connector, contact count, gender, pinout and cable were open because they follow from the `MCL` duplex model, which was itself open; and [Architecture §7.1](../03-architecture.md#71-the-module-port) stated that the Module Port *does not replace* the standalone AEL ports.
3. **Power** had no Platform answer at all. AES fixed no nominal Module supply voltage, no power connector and no rule about who powers a Module. EDR-007 had deliberately excluded power delivery over the Module Port as "a separate specification concern"; [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope) forbade a Hub to power *Units* but said nothing about Modules; and the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §5.2 spoke in passing of "the power the Hub supplies to its Module Ports" — a sentence that, read as a requirement, would have made every Hub a power distributor sized for the sum of its Modules.

A proposal from the maintainer asked for a coherent platform-level model: one M8 8-position connector for all Module-to-Module and Module-to-Hub communication, a separate M8 3-position 12 V input as the Module's primary power, USB-C as the local service connection, and the principle that **communication and primary Module power stay on separate connectors**. The proposal also asked that the standalone AEL ports be rethought rather than preserved.

The review found the proposal compatible with everything AES had settled *architecturally* — point-to-point AEL, the Hub as an active star, the Module as a standalone product, a Hub that is never a prerequisite — and in conflict with two things AES had settled *physically*: the M8 3-position AEL connector, which the same connector family as the proposed power input would have turned into a cross-mating hazard, and the retention of standalone AEL ports, which one Module Port makes redundant. Both were Draft-level decisions with nothing Released behind them. The review also found that the eight-position choice silently decides an open architectural question — the `MCL` duplex model — and that direct Module-to-Module cabling through a single port needs a cable rule that a generic straight-through cable cannot satisfy. Those consequences are decided here explicitly rather than inherited.

## Alternatives Considered

### Standalone AEL ports beside the Module Port

| Option | Assessment |
|---|---|
| **Keep the standalone M8 3-position AEL IN / AEL OUT ports** alongside a Module Port, as Architecture §7.1 stated | Rejected. Three external connectors carrying the same two AEL links twice; the M8 3-position form collides with the power input chosen below and with the sensor and electrode ports the Hardware Design Guide already warns about; the gender and keying question that had been open since EDR-006 exists only because of these ports. Their stated purpose — direct Module-to-Module operation without a Hub, test fixtures, adapters to laboratory equipment — is met by the Module Port with the cable rule below. |
| **One Module Port carrying `MCL`, AEL IN and AEL OUT; no separate AEL connector** | **Chosen.** One connector per Module for everything that is communication; one cable type; the AEL electrical layer, frame, timing and routing rules are untouched — only the connector through which the pairs leave the enclosure changes. |

### Connector for the Module Port

| Option | Assessment |
|---|---|
| **M8 8-position A-coded** (IEC 61076-2-104 form), female on every device | **Chosen.** Eight contacts carry three differential pairs, a reference and one reserved contact; the form is compact, sealed, locking and widely available; the insert is not intermateable with the 3- and 4-position M8 inserts, which is what makes a 3-position power input on the same enclosure safe. Female on Module and Hub alike means every cable is male-to-male and no device exposes contacts that could be live. |
| M12 or a larger circular family | Rejected for the communication port. Nothing on it needs the contact rating, and the size penalty on a small Module is real. Left available for a future power distributor's outputs if a current rating ever demands it. |
| Two connectors — `MCL` on one, both AEL links on the other | Rejected. It is the "two boxes and two cables per Module" wiring the Module Port exists to avoid, and it reintroduces the cross-connection the single port makes impossible. |

### AEL duplex model — re-examined, not changed

A follow-up review asked whether AEL needs two unidirectional pairs at all, or whether one bidirectional half-duplex pair (`AEL_A`/`AEL_B`) would do, saving a pair and a transceiver.

| Option | Assessment |
|---|---|
| **One half-duplex AEL pair per Module Port**, both ends able to drive | Rejected. AEL has, by design, no arbitration, no direction control, no addressing, no acknowledgment and **no retransmission** ([AES-AEL-001](../05-interfaces-and-versioning.md#aes-ael-001-ael-is-the-module-level-typed-event-interface), [AES-AEL-002](../05-interfaces-and-versioning.md#aes-ael-002-point-to-point-links-direct-and-routed-operation)); its frame reference instant *is* the event's timestamp. On a shared pair two peers can legitimately emit at the same instant — a detector event leaving a Module while a routed completion event arrives for it, or two routers exchanging fan-out over one Hub-to-Hub link — and the only outcomes are a collision that destroys two events with no recovery, or a medium-access rule (carrier sense, polling, tokens) that makes a Module's source-to-frame latency depend on its peer's traffic and turns AEL into the message protocol EDR-008 refused to build. The saving is one pair that the eight-position connector has anyway, bought with a MAC layer, direction control and turnaround timing at both ends of every link. |
| **Two unidirectional pairs per link — AEL IN and AEL OUT — one driver per pair, receiver-terminated** | **Retained.** Collision-free by topology, timing of each direction independent of the other, fail-safe and idle rules unchanged, and exactly what `AES-AEL-002` and EDR-008 item 8 already settle. This is not "full duplex because the transceivers were full duplex": it is two simplex links, and a device may build them from any driver and receiver — two single-pair parts used one way each included — provided no single half-duplex part serves both. |

### `MCL` duplex model — decided by the contact budget

| Option | Assessment |
|---|---|
| Full duplex on two pairs | Rejected. Two `MCL` pairs plus two AEL pairs plus a reference need nine contacts. Dropping the reference and using the shield as `GND` is not a differential link the Platform wants to specify. |
| Full duplex on one pair with simultaneous bidirectional transmission | Rejected. It needs an echo-cancelling PHY class that has nothing in common with the RS-485-class transceivers AEL already requires, so a Module would carry two transceiver technologies for two links in one cable, for no benefit `MCL`'s bursty, polled management traffic can use. |
| **Half duplex on one pair, RS-485-class, Hub-polled** | **Chosen.** Fits the budget with one contact to spare, shares AEL's transceiver class and protection strategy, and has a natural master: the Hub polls, the Module answers, and there is no arbitration problem on a point-to-point link. The `MCL` binding — framing, correlation, bit rate, turnaround, termination — remains open; only the duplex model and the pair count are decided here. |

### Cabling one port to a Hub *and* to a peer Module

| Option | Assessment |
|---|---|
| Straight cable; the Hub-side port is the mirror image of the Module-side port | Rejected. A direct Module-to-Module link then needs a *second* cable type with the AEL pairs crossed, and the two types are indistinguishable at a glance. Two cable types that both fit every port is exactly the mis-wiring the single connector was meant to remove. |
| **One device-side pinout on every port; every cable crosses AEL OUT to AEL IN — the AURIORA Link Cable** | **Chosen.** Module-to-Hub, Module-to-Module and Hub-to-Hub use one cable. Because the crossover is its own inverse the cable has no orientation. The consequence is stated rather than hidden: a generic straight-through M8 8-position cable is **not** an AURIORA Link Cable, would connect two drivers to one pair, and every port SHALL survive that indefinitely. |
| Auto-detection of a crossed or straight cable in firmware | Rejected. AEL is a one-directional pair with one driver; there is nothing to negotiate on, and an event interface that reconfigures its pins after a cable is plugged in is an interface that can emit a frame while doing so. |

### Hub-less topology

| Option | Assessment |
|---|---|
| Preserve the ability to chain three or more Modules without a Hub (A → B → C over independent direct links) | Rejected as a requirement. It was never one: [AES-AEL-002](../05-interfaces-and-versioning.md#aes-ael-002-point-to-point-links-direct-and-routed-operation) forbids daisy-chaining through a Module as the means of reaching several receivers, and AES-HUB-001 requires only that *two* Modules exchange events directly. The standalone ports made a chain of independent links physically possible; nothing in AES relied on it. |
| **Hub-less operation is the direct 1:1 link; three or more Modules use a Hub** | **Chosen** and stated explicitly, so that the loss of the incidental chain is a recorded decision and not a surprise. |

### Primary Module power

| Option | Assessment |
|---|---|
| Power over the Module Port, using the spare contact and `GND` | Rejected, as EDR-007 already did in principle. It makes the Hub a power distributor sized for the sum of its Modules — eight Modules at 0.5 A are 4 A before a single higher-power Module, start-up peak or cable loss is counted — and it ties the power budget of an installation to the port count of a communication device. |
| USB as the deployed power source | Rejected as the Platform rule; permitted as an option. USB power negotiation, cable drop and host behavior are outside the Platform's control, and a Module that must be operable from an arbitrary computer's port cannot be a high-power Module. |
| **A dedicated Module Power Interface: M8 3-position A-coded, nominal 12 V DC, male input on the Module, female output on the source, male-to-female cable** | **Chosen.** Every Module regulates its own rails locally; a power source, a future power distributor or a bench supply provides one standard connector; the Hub stays a communication device. The gender rule is the safety rule: an energized cable end is female and exposes no live contact, and the Module's male input is never energized by the Module itself. |

### Power-connector pin positions

| Option | Assessment |
|---|---|
| Positions 1, 2, 3 as proposed (`+12 V`, `0 V`, reserved) | Rejected. The M8 3-position A-coded insert is numbered **1, 3, 4** — position 2 is not populated — and the field-sensor convention on it is pin 1 = supply, pin 3 = return, pin 4 = signal. A 1/2/3 assignment would be a private numbering of a standard insert. (The former AEL pinout carried the same numbering error; its withdrawal removes it.) |
| **Pin 1 `+12 V`, pin 3 `0 V`, pin 4 `RESERVED`** | **Chosen.** Follows the connector family's own convention, so a standard three-conductor sensor cable wired 1-1, 3-3, 4-4 is a valid power cable, and the reserved contact is the one the family treats as the signal contact. |

### Naming

| Option | Assessment |
|---|---|
| "AURIORA Interface" as an umbrella term for the communication connector | Rejected. AES already names that connector the **Module Port** and its contents `MCL`, AEL IN and AEL OUT; a second name for the same thing is what [AES-TERM-001](../02-terminology.md#aes-term-001-vocabulary-preservation) exists to prevent. |
| "AURIORA Power Interface" | Adopted as **Module Power Interface**, with the qualifier that keeps it apart from the Unit Interface's `UIF_PWR_VIN`/`UIF_PWR_EN` managed power, which is a different layer with different rules. |

## Decision

1. A Module has at most **three external interface roles**, each on its own connector and never combined: the **Module Port** (communication: `MCL`, AEL IN, AEL OUT), the **Module Power Interface** (primary operating power) and the **direct local transport** (service, configuration, firmware, local data — USB-C as its first realization). The Module Port SHALL NOT carry a Module's primary operating power, and a Module Hub SHALL NOT be required to supply it. Rules: `AES-MOD-005` in [Architecture §3](../03-architecture.md#3-module-design); `AES-HUB-001` extended in [Architecture §7](../03-architecture.md#7-module-hub).
2. AEL IN and AEL OUT remain **two unidirectional differential pairs, one driver each** — a single half-duplex AEL pair was evaluated and rejected. The **Module Port** is an **M8 8-position A-coded** connector (IEC 61076-2-104 form), **female** on a Module, on a Module Hub's Module Ports and on its Hub-to-Hub link ports alike, with **one identical contact assignment on every port**. Its contacts carry `MCL_P`/`MCL_N`, `AEL_IN_P`/`AEL_IN_N`, `AEL_OUT_P`/`AEL_OUT_N`, `GND` and one `RESERVED` contact. A Module provides **exactly one** Module Port where it provides `MCL`, AEL IN or AEL OUT at all, and no separate AEL connector. Specification: [`docs/interfaces/module-port.md`](../interfaces/module-port.md), `0.1` Draft.
3. **`MCL` is half duplex on one differential pair**, RS-485-class, with the Module Hub as the polling master of each link. The duplex model and pair count are decided; the binding — electrical profile, framing, correlation, bit rate, turnaround, termination, cascading — remains open and is specified as recorded in EDR-007 and EDR-010.
4. The **AURIORA Link Cable** is the only cable for a Module Port: M8 8-position male-to-male, **crossing AEL OUT to AEL IN in both directions** with polarity preserved, `MCL`, `GND` and `RESERVED` straight, shield to shell at both ends, each differential link on its own twisted pair. It is non-oriented, and the same cable connects a Module to a Hub, a Module to a Module and a Hub to a Hub. A generic straight-through M8 8-position cable is not compatible; every Module Port SHALL survive one indefinitely without damage and without a valid AEL frame.
5. **Hub-less operation is the direct 1:1 link**: two Modules joined by one Link Cable exchange AEL events with no infrastructure, each managed over its own direct local transport. Three or more Modules in one event exchange use a Module Hub. Hub-to-Hub AEL links use the same connector and cable.
6. The **Module Power Interface** is the primary external power input of a Module: **M8 3-position A-coded, male on the Module**, **nominal 12 V DC**, **pin 1 `MPI_VIN` (+12 V), pin 3 `MPI_RTN` (0 V), pin 4 `RESERVED`**. A power source — a bench supply, a future power distributor — provides a **female** output; the power cable is **male-to-female**, wired straight. Each Module generates its internal rails locally. A Module SHALL NOT energize its power-input contacts from any other source, and neither the Module Power Interface nor any other source SHALL back-feed a host's USB port. The accepted input-voltage range and the Platform current limit are **open engineering decisions** and are not standardized here; the connector family's rating is a ceiling on them, never their value. Specification: [`docs/interfaces/module-power.md`](../interfaces/module-power.md), `0.1` Draft.
7. The **reserved contact** of either connector is not connected on any device, is wired through in the cable, and acquires a function only through a new version of the respective specification — never through a Module design.
8. **USB-C** is the preferred realization of a Module's direct local transport and of a Module Hub's host-facing interface. USB MAY power a Module for development, service, configuration or low-power operation where the Module supports it safely and declares it; USB is not the deployed power distribution of the Platform, and a Module operable from both sources implements power-path protection so that neither source is back-driven.
9. A future **power distribution device** providing several Module Power Interface outputs is architecturally allowed and is not specified: no port count, total power, per-port limit, switching, sensing, enable, detection, protocol or fault behavior is decided. The Module Hub and any such device remain separate responsibilities; a Hub SHOULD take its own power through a Module Power Interface input.
10. The former **standalone M8 3-position AEL ports are withdrawn**; the [AEL specification](../interfaces/ael.md) moves to `0.2` with its physical layer carried by the Module Port and everything else unchanged. **Terminology** gains *Module Power Interface* and *AURIORA Link Cable* and updates *Module Port*, *Module Control Link*, *Module Hub* and *Hub-to-Hub AEL link*. Frozen core vocabulary is unchanged.

## Rationale

The whole record rests on one separation: what a Module *says* and what a Module *eats* arrive on different connectors. Once that is fixed, every other decision is the shortest path to a consistent whole. A Hub that does not power Modules is a communication device whose port count is a product decision and not a power budget; a Module that regulates its own rails from a standard 12 V input works on a bench, in a field enclosure and under a Hub with the same hardware; and a power distributor, if one is ever built, is a product that provides a connector the standard already defines, not an architecture the standard has to invent first.

Withdrawing the standalone AEL ports is what makes the connector inventory small enough to be safe. With them gone, the only M8 3-position connector the Platform defines is the power input, and the M8 8-position Module Port cannot mate with it. The gender question that stayed open through EDR-006 and EDR-008 — the "OUT = male / IN = female" idea — was a symptom of having two connectors that carried the same signal; one connector with one pinout has no gender to decide beyond "female on devices".

The eight-position budget deciding the `MCL` duplex model is accepted rather than regretted. Half duplex on one pair is what a Hub-polled management link wants anyway: one transceiver class for all three pairs, one protection strategy, and traffic that is bursty and latency-tolerant by AES's own description of the concentrator. The one contact left over is reserved precisely so that it is not spent by the first design that finds a use for it.

The Link Cable's crossover is the one non-obvious consequence of a single port, and it is made a Platform rule because the alternative — two cable types — fails the Hardware Design Guide's own test that anything which can be plugged in wrong eventually will be. Requiring every port to survive a wrong cable is the same principle applied to the cable that will inevitably be substituted in the field.

The power connector's 1/3/4 numbering follows the insert rather than the proposal because a Platform that writes its own numbering onto a standard connector has created a private convention its cable suppliers do not share. Keeping the input-voltage range and the current limit open is not indecision: both depend on regulator choices, cable losses and the power of Modules that do not yet exist, and a SHALL written today would either be violated by the first real Module or be so loose as to say nothing.

## Consequences

- AES gains `AES-MOD-005`; `AES-HUB-001` is extended; [Architecture §3](../03-architecture.md#3-module-design) and [§7.1](../03-architecture.md#71-the-module-port) are rewritten around the settled Module Port; [Interfaces and Versioning §5.1](../05-interfaces-and-versioning.md#51-transport-bindings) records the `MCL` duplex model; [Terminology §3](../02-terminology.md#3-supporting-terms) gains two terms and updates four.
- Two Draft interface specifications are added — the **Module Port** and the **Module Power Interface** — and the **AEL specification moves from `0.1` to `0.2`**, an incompatible physical-layer change to a Draft specification. Nothing Released carried the `0.1` connector; the Audio Module's reserved single-ended `SYNC_IN`/`SYNC_OUT` GPIOs, already non-conformant to AEL `0.1`, are now expected to align to a Module Port.
- **This is released within AES `0.9.0`**, folded into the same version as EDR-010 on the day of that release. The AEL physical-layer change is recorded as incompatible in the changelog under pre-Release `0.x` versioning ([AES-VER-001](../05-interfaces-and-versioning.md#aes-ver-001-semantic-versioning-for-released-contracts)).
- Items 8 and 9 of EDR-008's Decision are superseded; EDR-007's and EDR-008's open-item lists are annotated. EDR-006 remains a historical record.
- The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) rewrites its AEL port rules around the Module Port, corrects the §5.2 sentence about Hub-supplied Module Port power, and gains Module Port, Link Cable and Module Power Interface rules; the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) and [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) are unaffected. The private engineering knowledge base is re-derived afterwards.
- The `MCL` binding specification, when written, inherits the half-duplex single-pair model, the Module Port's contact assignment and the Link Cable, and assigns the Module Port's contact numbering together with the Module Port specification's first `1.x` release.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** three separated external interface roles; AEL as two unidirectional pairs, not one half-duplex pair; no primary power on the Module Port and no Hub obligation to power Modules; M8 8-position female Module Port with one contact assignment on every port and exactly one per Module; half-duplex single-pair `MCL`; the AURIORA Link Cable as the only Module Port cable, with the crossover and the survive-a-wrong-cable rule; hub-less operation as the direct 1:1 link; Hub-to-Hub links on the same port and cable; the Module Power Interface as M8 3-position male input at nominal 12 V with positions 1/3/4; reserved contacts owned by the Platform; USB-C as preferred service connection with optional, declared, back-feed-protected powering; a power distributor allowed but unspecified.

**Open — Platform decisions, taken with the evidence they need:**

- **Module Port contact numbering** — which of the eight positions carries which contact — assigned in the Module Port specification once the `MCL` binding's electrical profile is chosen, against the constraints the specification states (pairs on adjacent positions, one assignment for every port, a symmetric crossover).
- **Link Cable impedance, conductor size, shield construction and maximum validated length**, from bring-up of the first Module, Hub and cable at the AEL and `MCL` bit rates; `MCL`-to-AEL crosstalk in the shared cable, as EDR-007 required.
- **`MCL` binding** — electrical profile, framing, request correlation, flow control, bit rate, fail-safe and cascading, and the half-duplex line discipline that the duplex decision now makes necessary: line ownership at idle, who may initiate (the Hub polls; whether a Module may ever speak unprompted is the EDR-010 question), driver- and receiver-enable behavior, turnaround after end of frame and the maximum response time, behavior when both ends drive, idle differential state, and termination topology for a bidirectional pair. None of these is fixed by a constant here; unchanged in scope from EDR-007 and EDR-010 except that the duplex model is now decided. *Cascading is decided in [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md); the binding inherits path addressing and tagged correlation from it.*
- **Module Power Interface accepted input-voltage range** and **Platform continuous and start-up current limit**, derived from realistic sources, regulator input ranges, cable losses and protection behavior of the first Modules; **power cable conductor size and maximum length** follow from them.
- **Two `MCL` masters on one pair** when two Hubs' Module Ports are cabled together, and the **`GND` return-current bound** on the Module Port with several independently powered Modules on one Hub — both recorded as open in the Module Port specification, decided with the `MCL` binding and bring-up measurement respectively. *The first is a reported cabling fault per [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md); the detection rule stays with the binding.*
- **Function of the reserved contacts**, if any, on either connector.
- **AEL electrical profile, cable and termination validation, timing envelopes and router management contract** — unchanged from EDR-008 and the AEL specification.

**Open — product decisions, recorded with each product:** whether a Module supports USB powering and in which modes; a Module's power-tree figures; a Hub's Module Port and Hub-to-Hub link counts; whether a Hub's own logic may run from its host-facing interface (EDR-010); everything about a power distributor.

## Affected Requirements / Documents

- [Architecture §3](../03-architecture.md#3-module-design) — `AES-MOD-005` (new); Module design paragraphs. [§7](../03-architecture.md#7-module-hub) — `AES-HUB-001` (extended: no Module power); introductory text; [§7.1](../03-architecture.md#71-the-module-port) rewritten.
- [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link) — §4.1 topology note; [§5.1](../05-interfaces-and-versioning.md#51-transport-bindings) — `MCL` row and open-item paragraph.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Module Power Interface*, *AURIORA Link Cable* (new); *Module Port*, *Module Control Link*, *Module Hub*, *Hub-to-Hub AEL link* (updated).
- [`docs/interfaces/module-port.md`](../interfaces/module-port.md) (new, `0.1` Draft); [`docs/interfaces/module-power.md`](../interfaces/module-power.md) (new, `0.1` Draft); [`docs/interfaces/ael.md`](../interfaces/ael.md) (`0.1` → `0.2`: §2, §3, §4, §8, §9, §10, §11); [`docs/interfaces/README.md`](../interfaces/README.md).
- [EDR-007](./EDR-007-module-control-interface-and-module-hub.md), [EDR-008](./EDR-008-auriora-event-link.md) — open-item annotations; EDR-008 Decision items 8 and 9 superseded.
- [Worked Example: Multimodal AEL Experiment](../../examples/worked-example-multimodal-ael-experiment.md) — bench description names the Link Cable.
- [Document Index](../document-index.md), `STANDARD.md`, `CHANGELOG.md` — indexing.
- Hardware Design Guide §5.1 (rewritten), §5.2 (corrected), §5.3 and §6.2 (new), §16 checklists.

## Future Review Criteria

Revisit if: a Module class needs more than the single half-duplex `MCL` pair can carry for management — the presumption is that such traffic is bulk and belongs on the direct local transport, not that the port grows; the first Link Cable validation finds that three pairs at their respective bit rates cannot share one M8 8-position cable at a useful length; a real deployment needs three or more Modules to exchange events without a Hub, which would be a case for a small AEL-only router product rather than for a second port; a Module class needs more power than a 12 V M8 3-position input can safely deliver, which would be the case for a second, larger Module Power Interface profile rather than for a different voltage; or a power distributor's requirements show that a reserved contact should carry a Platform-defined function.
