# EDR-007: Module Control Interface and Module Hub

## Status

Accepted (2026-09-12)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module or Module Hub relies on this architecture.*

## Context

AES describes three interface classes. Two of them are specified: the Unit Interface has versioned profiles, an electronic identity contract, a discovery and activation sequence and a selection rule; the Module Synchronization Interface has event semantics, a topology, behavioral rules and a Draft physical specification. The third — the Host Interface — has two requirements. [AES-IF-002](../05-interfaces-and-versioning.md#aes-if-002-host-interface-determinism) asks that a Released one be machine-parseable with a defined error model, and [AES-MOD-002](../03-architecture.md#aes-mod-002-host-interface-for-released-modules) asks that a Released Module have one at all.

That is enough to stop a Module shipping a debug UART and calling it an interface. It is not enough to stop two AURIORA Modules exposing two unrelated control protocols, two identity queries, two capability models and two incompatible notions of being ready to run. Nothing in AES currently says how a host learns *which* Module it is talking to, what that Module can do, or whether it is prepared to act — the questions the Unit Interface answers thoroughly one level down.

The gap becomes operational rather than theoretical as soon as a bench holds more than a few Modules. Configuring, updating, loading, arming and monitoring each one over its own cable does not scale, and neither does host software that special-cases each Module by type. The obvious infrastructure answer — a hub — cannot be designed until there is a control contract for it to carry.

A separate risk arrives with that hub. [EDR-006](./EDR-006-module-synchronization-interface.md) deliberately made the SYNC Hub controller-less, because a Hub with firmware has a propagation delay that depends on its load. A combined hub that also manages control traffic invites exactly the design that decision rejected: port masks, routing tables and event handling behind the same processor that is servicing bulk transfers.

Introducing a Platform interface class and its supporting architecture is platform-wide, and therefore requires an EDR under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger).

## Alternatives Considered

### Shape of the control layer

| Alternative | Assessment |
|---|---|
| **Leave the Host Interface as a quality bar** — each Module defines its own protocol, AES only requires that it be documented and deterministic | Rejected. This is the status quo, and it produces N protocols for N Modules. Host software, test fixtures and any future infrastructure must then implement each one, and the cost is paid again for every Module added. The Unit Interface demonstrates the alternative: one contract, many implementations. |
| **One end-to-end control interface** — a single specification running from differential signaling up to the command set | Rejected. It binds the semantics to one wire. The local service path (commissioning, firmware update, recovery) would then either get a second, separately defined protocol, or be described informally as "the same thing over USB" — and the two would drift. It also contradicts an existing rule: the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3.2 already requires host-side protocol code to speak to an abstract transport. |
| **A transport-independent logical contract with versioned bindings** | **Chosen.** The semantics are specified once; each transport specifies only carriage. Local service and hub-connected operation expose the same operations, so a workflow validated on the bench is the workflow that runs in the installation, and a simulated Module ([ASSG](https://github.com/auriora-org/auriora-software-style-guide) §3.4) is a first-class target rather than an approximation. |

### A shared differential physical-link abstraction

The proposal that prompted this record introduced a common differential link layer — working name *ADL* — as a fourth interface class, with control and SYNC defined as profiles over it. The stated benefit was specifying the electrical layer once.

| Alternative | Assessment |
|---|---|
| **A fourth Platform interface class** under which control and SYNC are profiles | Rejected, on three grounds. *There is little to factor out:* the SYNC electrical layer is roughly ten lines of normative text in [`sync.md`](../interfaces/sync.md) §3, and a new interface class, terminology, versioned specification and identity assignment cost more than the duplication they remove. *The two users differ where it matters:* SYNC is a unidirectional, unframed link optimized for edge fidelity and fail-safe idle; a control link is bidirectional and framed, with a bit rate, bus recovery and its own common-mode requirements over its own cable length. *The abstraction cannot yet be written:* the proposal itself left the duplex model — pair count, simultaneous transmit and receive — undecided, and a common physical layer whose most basic property is unknown and probably differs between its two users is not a specification. |
| **No shared layer; each interface specifies its own electrical requirements** | **Chosen.** SYNC keeps its specification. `MCL` gets its own when its requirements are real. Conventions that genuinely are shared — transceiver class, protection at the connector, receiver-side termination, `P`/`N` polarity naming — belong in the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide), which already carries them for SYNC ports. |
| **Defer the question** | Effectively part of the chosen option, and recorded as such: the properties that a combined Module Port really does share — connector, contacts, cable, shield, reference, hot-plug, ESD entry — are shared because they are one physical connector, not because of an abstract link layer, and they have a natural home in the Module Port connector specification when it is written. If a shared electrical baseline earns its place later, it will be factored out of two concrete specifications rather than guessed ahead of both. |

### Naming

| Alternative | Assessment |
|---|---|
| **`CTRL`** for the control interface, as in the originating proposal | Rejected. `Controller` is frozen core vocabulary ([AES-TERM-003](../02-terminology.md#aes-term-003-frozen-core-vocabulary)), `CTRL` is already an AOID class code *and* an AOID domain code ([Naming and Identity §6](../04-naming-and-identity.md#6-object-identifiers-aoids)), and `AES-CTRL-002` and `AES-CTRL-003` are existing Controller requirements. A "CTRL interface" would collide in prose, in identifiers and in search. |
| **`MCI` (logical) and `MCL` (link)** | **Chosen.** Both expand to the canonical role words, `Link` matches the existing use of the term in the SYNC specification, and neither collides with an assigned identifier. The two differ by one letter and will appear in the same sentences; that is accepted as a documentation-legibility cost, mitigated by net names that spell out direction (`MCL_*` against `SYNC_IN_*` / `SYNC_OUT_*`). `CTRL` survives only as a non-canonical working name, which [AES-TERM-001](../02-terminology.md#aes-term-001-vocabulary-preservation) permits if marked. |

### Module Hub and the SYNC path

| Alternative | Assessment |
|---|---|
| **A fully managed hub** — firmware handles control traffic and SYNC distribution alike, with per-event routing, masking and retiming | Rejected. It reintroduces exactly what EDR-006 excluded. Once firmware decides per event whether and where an edge is forwarded, the Hub's propagation delay becomes a function of its load, and the single property SYNC exists to provide is gone. Per-event flexibility also has no identified AURIORA use case. |
| **Two separate products** — a SYNC Hub and a control concentrator, never combined | Rejected as the required form, retained as a permitted one. Two boxes and two cables per Module is the wiring the Module Port concept exists to avoid, and nothing about combining them is unsafe provided the paths stay separate inside. |
| **A composite device with separated roles** — managed `MCL` concentrator, firmware-free SYNC event path, optional SYNC Source | **Chosen.** Static pre-ARM configuration keeps selectable fan-out available without a processor in the timing path. Passive observation — counting, timestamping — stays legitimate because it does not touch the edge. A Hub-originated event is generated by firmware, which is harmless: what matters is that every Module receives the resulting edge simultaneously, not how long the request took to arrive. That origination is a distinct role, named *SYNC Source*, so it is not confused with fan-out. |

### Hub topology

| Alternative | Assessment |
|---|---|
| **Passive or multidrop distribution** | Rejected, for the reasons already recorded for SYNC in EDR-006 and now applying equally to control: shared collision domain, loading that depends on how many Modules are connected, one faulty node disturbing all, and direction control on a shared pair. |
| **Active star, one independently managed port per Module** | **Chosen.** Each port has its own driver, receiver and termination; a fault, disconnection or unpowered Module costs one port. It also makes port presence, per-port diagnostics and physical location tracking straightforward, and it scales by adding ports rather than by renegotiating a bus. |

### Module Port packaging

| Alternative | Assessment |
|---|---|
| **Specify the combined connector now** | Rejected. The contact count follows from the `MCL` duplex model and the SYNC direction count, and the first of those is undecided. Choosing a connector before them is a guess that later has to be unmade, and the originating proposal asked for the same restraint. |
| **Keep control and SYNC on separate connectors permanently** | Rejected as the target. One cable per Module is less to wire, less to mislabel and impossible to cross-connect, and a combined port is the packaging a multi-Module installation wants. |
| **Record the intent, defer the physical layer, retain the standalone SYNC ports** | **Chosen.** The architecture states that a Module Port carries `MCL` and both SYNC directions as electrically independent links in one cable; everything physical stays open, crosstalk between the `MCL` and SYNC pairs explicitly included. Because the standalone M8 SYNC ports remain, this decision does not contradict and does not supersede EDR-006, and direct Module-to-Module synchronization and third-party laboratory interoperability are preserved. |

### SYNC direction through the Module Port

| Alternative | Assessment |
|---|---|
| **Downstream only** (Hub to Module) | Rejected. A Module Hub would then be unable to receive a Module's SYNC OUT, so any configuration where one Module's internal event triggers others would require reverting to direct cabling and defeat the single-cable packaging. |
| **Both directions, as two independent differential links** | **Chosen.** The Module Port carries `SYNC_IN` and `SYNC_OUT` as separate links, each under the existing SYNC rules. A Module's SYNC OUT event may therefore reach both its standalone connector and the Module Port; each is a separate point-to-point link with its own driver, which is an active fan-out at the Module and not a passive split. The Hub's handling of a received event remains subject to the firmware-free path rule above. |

## Decision

1. AES defines the **AURIORA Module Control Interface (MCI)**: the Platform's transport-independent realization of the Host Interface, covering Module identity, capability discovery, lifecycle and the ARM boundary, configuration, Assets, Sessions and bulk-object transfer. Its rules are `AES-MCI-001` to `AES-MCI-005` in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface).
2. MCI is carried by versioned **MCI transport bindings**, which define carriage only. Two are intended: a direct local transport such as USB, and the **Module Control Link (`MCL`)**, a wired differential point-to-point link to a Module Hub. **Neither binding is specified in this version.** A Module remains fully serviceable — commissioning, update, diagnostics, recovery — through its direct local transport, without infrastructure.
3. **No shared differential physical-link abstraction is introduced.** MCI/`MCL` and SYNC remain separate interfaces, each with its own electrical and protocol requirements. Shared electrical conventions live in the Hardware Design Guide; properties shared by virtue of one physical connector belong to the Module Port connector specification when it is written.
4. Naming is **MCI** for the logical contract and **`MCL`** for the differential binding. `CTRL` is a non-canonical working name only.
5. AES defines the **AURIORA Module Hub**: optional active-star infrastructure presenting one Module Port per Module, composed of a managed `MCL` concentrator, a SYNC Hub function and an optional SYNC Source. Its rules are `AES-HUB-001` and `AES-HUB-002` in [Architecture §7](../03-architecture.md#7-module-hub). The Hub carries MCI without interpreting Module-specific semantics, is never the source of Module identity, and does not reach Units.
6. The **SYNC event path stays independent of Hub firmware**, including inside a composite Hub. Routing, port enable and group membership are static configuration established before the affected Modules are armed and are not evaluated per event; passive observation that cannot alter, delay or gate the edge is permitted. `AES-SYNC-002` is amended accordingly and *SYNC Source* is added as a distinct role.
7. The **Module Port** is recorded as architectural intent: one connector and cable carrying a Module's `MCL` together with its SYNC IN and SYNC OUT as electrically independent links. Connector, pinout, contact count, cable and the `MCL`/SYNC crosstalk requirement are open. **Standalone SYNC ports are retained**, so this record does **not** supersede EDR-006.

## Rationale

The decision separates the two things that were entangled in the originating proposal: a genuine gap in the standard, and an abstraction that looked like it would help.

The gap is real. Everything a host needs in order to treat Modules as a population rather than as individual devices — persistent identity, declared capabilities, an observable lifecycle, verifiable arming, transfer that cannot half-succeed — is missing today, and none of it depends on a wire. Specifying it as a logical contract costs nothing in hardware commitment, is cheap to revise while nothing is Released, and unblocks host software immediately.

The abstraction is not. Factoring a common electrical layer out of two interfaces requires knowing both, and only one of them exists. Deferring it loses nothing: SYNC already has its specification, `MCL` will get one, and the conventions that really are common are already written down where hardware engineers read them.

The ARM boundary is what makes MCI and SYNC complementary rather than competing. MCI can prepare a Module to the point where its next action is determined and validated; it cannot deliver the instant, because a sequence of control operations produces a spread in start times that is neither bounded nor recorded, and data from such a run looks synchronized without being so. Making `ARMED` explicit and verifiable also moves the last chance to notice a missing Module to before the event rather than after it.

Keeping the Hub's SYNC path free of firmware preserves the property EDR-006 was written to protect, while conceding nothing useful: no AURIORA use case calls for a per-event decision in the Hub, and static pre-ARM configuration provides the selectable fan-out that real installations want.

Deferring the connector follows the discipline already applied to SYNC and the Unit Interface Profiles — state firmly what the architecture settles, record as open what only hardware can answer, and avoid the specification that has to be unmade.

## Consequences

- AES gains requirements `AES-MCI-001` to `AES-MCI-005` and `AES-HUB-001` to `AES-HUB-002`, an amended `AES-SYNC-002`, nine supporting terms, a new [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) and a new [Architecture §7](../03-architecture.md#7-module-hub). Frozen core vocabulary is unchanged.
- **MCI is a SHOULD, not a MUST, for Released Modules in this version.** No transport binding is specified, so requiring MCI would require conformance to something unwritten. `AES-MOD-002` is unchanged. Raising MCI to a requirement is a later decision, taken when at least one binding is specified and implemented.
- **EDR-006 is unaffected and remains in force.** Standalone SYNC ports, the M8 3-position connector, its open items and the controller-less SYNC Hub all stand. The amendment to `AES-SYNC-002` constrains composite devices; it relaxes nothing.
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) and [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) each need an implementation section — Module lifecycle, arming and staged transfer on the firmware side; device registry, identity mapping and desired-state orchestration on the host side. The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) gains nothing yet, because no electrical decision has been made.
- A Module Hub is a product and will need a Product Family identifier under [AES-NAME-001](../04-naming-and-identity.md#aes-name-001-family-identifier-stability). None is assigned here. No new AOID taxonomy value is required: MCI is a Host Interface contract and uses the existing `HIF` class code.
- The vocabulary of the originating proposal — `ADL`, `ADL instance`, `CTRL`, `device_uid` — is superseded by this record and by [Terminology §3](../02-terminology.md#3-supporting-terms). Module identity is expressed with the AOID and serial number AES already defines, not a new identifier scheme.
- **This is normative surface added ahead of hardware validation.** Three Unit Interface Profiles and the SYNC specification are still Draft, and nothing is Released. The mitigation is the split this record makes: the logical layer is cheap to revise and immediately useful, and every electrical and mechanical commitment is deferred behind measurement.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

Not resolved here. The first four are blocking for any hardware work:

- **`MCL` duplex model** — one differential pair with direction control, or two pairs with simultaneous transmit and receive. Everything physical follows from this.
- **`MCL` binding specification** — electrical layer, framing, request correlation, flow control, bit rate, termination, fail-safe and cable envelope.
- **Module Port physical layer** — contact count, connector family, gender, keying, pinout, cable construction and impedance, maximum length, reference and shield strategy.
- **`MCL`-to-SYNC crosstalk** — the isolation required so that continuous `MCL` traffic does not degrade SYNC edge timing in a shared cable, characterized and specified before the Module Port is fixed.
- MCI version numbering and its starting version; the direct local transport binding.
- Whether MCI becomes a MUST for Released Modules, and on what schedule.
- Module Hub Product Family identifier, product naming, and its host-facing transport.
- Whether a Module Hub needs an AOID interface class of its own.
- Security posture for a Hub with a network-facing upstream transport; authenticated host sessions.
- Power delivery over the Module Port. Deliberately excluded from this record: it is a separate specification concern and must not be attached to control or synchronization semantics.

## Affected Requirements / Documents

- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — new section; `AES-MCI-001` to `AES-MCI-005` (new).
- [Interfaces and Versioning](../05-interfaces-and-versioning.md#aes-sync-002-point-to-point-links-and-active-fan-out) — `AES-SYNC-002` amended for composite devices, static pre-ARM configuration, passive observation and the SYNC Source role.
- [Architecture §7](../03-architecture.md#7-module-hub) — new section; `AES-HUB-001` and `AES-HUB-002` (new); §3 Module Design gains the MCI paragraph.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — nine supporting terms.
- [Document Index](../document-index.md), `STANDARD.md` — indexing.

## Future Review Criteria

Revisit if: a second differential interface appears that genuinely shares an electrical layer with `MCL` and SYNC, making a common baseline specification worth extracting from concrete specifications rather than ahead of them; an AURIORA use case requires a per-event decision inside a Hub, which would be a reason to re-examine the timing contract rather than to relax the firmware-free rule; MCI needs to become mandatory for Released Modules; a Module Hub acquires a network-facing upstream transport, which changes the security posture; or the Module Port is found to be unable to carry `MCL` and SYNC in one cable without degrading SYNC edge timing, in which case separate connectors return as the answer.
