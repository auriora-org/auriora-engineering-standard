# EDR-015: Module Power Interface Limits and External Connector Reservation

## Status

Accepted (2026-10-01)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module, Module Hub or power source relies on the figures fixed here.*

**Closes** the Module Power Interface items left open by [EDR-011](./EDR-011-module-external-interfaces-and-power.md): the accepted input-voltage range, the Platform current limit and the power cable's conductor size and length rule. **Tightens** the Hub power rule of `AES-HUB-001` from preferred to required, and **adds** `AES-MOD-006` with the External Connector Register. Everything else in EDR-011 stands.

## Context

EDR-011 fixed the shape of the Module Power Interface — M8 3-position A-coded, male input on the Module, female output on the source, positions 1/3/4, 12 V DC nominal — and deliberately left its numbers open until real Modules and sources existed. They now do. The first measurement Module carries eight M8 3-position **female** electrode inputs beside its power input; the first Hub needs its own power input; and the first bench and field power sources are commercial 12 V adapters, battery packs and solar charge controllers whose output cables are re-terminated with a female M8 3-position connector. Each of these asked a question the Draft could not answer: how much current a Module may draw, what voltage it must accept, whether a Hub may run from USB, and whether a female M8 3-position measurement input is a conflict with the power input or not.

A maintainer proposal answered them in one piece: 12 V nominal, 3 A per port from the connector rating, a suggested 10.5–14.0 V range, a Hub with its own power input, a platform-wide rule that the M8 3-position male form is power-input only, and a connector register. The review below accepts the shape of the proposal and changes three of its numbers.

## Alternatives Considered

### Current limit per input

| Option | Assessment |
|---|---|
| **3 A continuous**, the connector family's contact rating, as proposed | Rejected. The Hardware Design Guide's own derating table holds connector contact current to 50–70 % of rating, and a 3 A continuous Platform limit would exempt the Platform's own interface from it. The cable decides as well: a 0.25 mm² conductor pair drops about 0.4 V per metre at 3 A, so a 2 V budget buys under five metres of cable. |
| Leave the limit open, as EDR-011 did | Rejected. A source designer cannot size an output, and a Module designer cannot size a power tree, against "open". |
| **2 A continuous, 3 A start-up, with 3 A / 60 V as the connector ceiling** | **Chosen.** 2 A is inside the derating rule, leaves a usable cable length, and is the figure the first Modules fit under with margin. The 3 A ceiling is written down so that no later revision can raise the continuous limit above the contact rating by argument. The current limit is a *current*, not a power: a constant-power Module draws its highest current at the bottom of the voltage range, so about 20 W is the practical Module power under this profile, not 36 W. |

### Accepted input-voltage range

| Option | Assessment |
|---|---|
| **10.5–14.0 V**, as proposed | Rejected on the upper bound. A 12 V battery under charge sits above 14.0 V — lead-acid absorption at 14.4 V, four-cell LiFePO4 at 14.4–14.6 V — and a solar charge controller's load output follows it. A Module that stops at 14.0 V stops whenever its battery is being charged. |
| 9–16 V operating, 18 V no-damage (automotive-style) | Considered. The upper end is the same as chosen; the lower end costs a wider regulator input range and more cable-drop allowance than the first Modules need. |
| **10.0–15.0 V operating; 0–18 V and reverse polarity to −18 V without damage** | **Chosen.** 15.0 V covers every 12 V battery chemistry under charge; 10.0 V allows 2 V of cable drop from a regulated source at the current limit and sits above a battery's low-voltage disconnect; 18 V is the no-damage bound a battery or charger fault can reach and the clamp target a regulator input tolerates. |

### Hub power input

| Option | Assessment |
|---|---|
| A Module Power Interface input "preferred" on a Hub, USB powering a product decision (EDR-011) | Rejected. A Hub whose router timing depends on how much a laptop port supplies has no timing contract, and the exposed-contact safety argument of the gender rule was written for "the Module's input" only, leaving the Hub's input undescribed. |
| **A Hub SHALL take its primary operating power through a Module Power Interface input**, with USB powering as a declared, back-feed-protected option exactly as for a Module | **Chosen.** One rule for every Platform device; the gender rule and the back-feed rule then cover every male power contact in the system. |

### M8 3-position connectors other than the power input

| Option | Assessment |
|---|---|
| No other M8 3-position connector on a Module at all (the Hardware Design Guide's current wording) | Rejected. The form is the common sensor and electrode connector, the first measurement Module already carries eight of them, and the hazard the rule exists for — a live power cable entering a measurement input — is decided by gender, not by the position count. |
| **The M8 3-position male / pin-contact panel form is reserved for the Module Power Interface input; the female / socket-contact panel form is a power source's output and, otherwise, a measurement-side port under a recorded mis-mating analysis** | **Chosen.** A power cable's live end is female and cannot enter a female measurement input; a power cable's male end enters only a female output and is never live, because no device energizes a male contact ([EDR-011](./EDR-011-module-external-interfaces-and-power.md)); a measurement cable's female end can enter a Module's power input, where it meets an unenergized, protected input. Every physically possible mis-mating is therefore harmless by construction, and the analysis a product records is the confirmation that its own measurement ports keep it so. |

### Name

The proposal re-raised "AURIORA Power Interface". EDR-011 adopted **Module Power Interface** to keep it apart from the Unit Interface's managed power, and the term is in use in every document; it is not changed ([AES-TERM-001](../02-terminology.md#aes-term-001-vocabulary-preservation)).

### A power input on every Module

The proposal would require every Module to carry a Module Power Interface input. `AES-MOD-005` requires it *where a Module has an external primary power input*, which admits a sealed battery-only Module. Kept as is: the rule is about the form of the input, not about forbidding a product that has none.

### Pin assignment

Re-examined against the proposal's 1/3/4 assignment and the connector family's convention; unchanged from EDR-011.

### Where the connector register lives

| Option | Assessment |
|---|---|
| In the Hardware Design Guide | Rejected. The register decides what a Module *may* carry, which is an AES conformance matter; the guide tells how to build it. |
| **In the Document Index beside the Family Identifier Register and the AOID assignments, with the rule as `AES-MOD-006`** | **Chosen.** Registers already live there, and an assignment to an unassigned form is an EDR, like every other register entry. |

## Decision

1. The Module Power Interface specification moves to **`0.2`** with these figures fixed: **12.0 V DC nominal**; **operating range 10.0–15.0 V** at the Module's input, within which a Module meets its full specification; **no-damage range 0–18 V and reverse polarity to −18 V**, indefinitely; **continuous current 2 A** per input (any 1 s average) and **start-up current 3 A** (any 10 ms average); the connector family's **3 A / 60 V** rating is the ceiling no version of the interface exceeds. A source output stays within **11.4–15.0 V** across its rated load; a power cable uses conductors of at least **0.25 mm²**, is rated 3 A, states its length, and is chosen so that the Module's input stays at or above 10.0 V at the Module's maximum continuous current. Specification: [`docs/interfaces/module-power.md`](../interfaces/module-power.md).
2. Below 10.0 V a Module MAY cease to operate but SHALL do so in a defined way — no damage, no undefined output, no valid AEL frame, automatic recovery when the input returns to range under [AES-MCI-007](../05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance). Reverse-polarity, overcurrent, transient and hot-plug protection at the input remain as EDR-011 and the Hardware Design Guide require; a Module declares its input capacitance until the Platform fixes an inrush figure.
3. **Contact terminology.** The specifications and the guide name the contact type beside the gender — *male / pin-contact* and *female / socket-contact* — because supplier vocabulary for "receptacle" and "plug" is not uniform.
4. **`AES-HUB-001`** is tightened: a Module Hub SHALL take its primary operating power through a Module Power Interface input under the rules of `AES-MOD-005`; its host-facing interface MAY power it only as a declared, back-feed-protected option. The gender-rule rationale of `AES-MOD-005` names the Module's and the Hub's inputs.
5. **`AES-MOD-006` — External Connector Reservation** ([Architecture §3](../03-architecture.md#aes-mod-006-external-connector-reservation)): the M8 3-position A-coded **male / pin-contact panel** connector is reserved on every Platform device for the Module Power Interface input and SHALL NOT be used for anything else; the M8 3-position **female / socket-contact panel** connector is the Module Power Interface output of a power source and otherwise MAY serve only a measurement-side function, with a recorded mis-mating analysis; the M8 8-position A-coded form is reserved for the Module Port and the Link Cable. Platform-facing and power connectors are chosen so that a hazardous or damaging mis-connection is prevented by mechanical incompatibility, with marking in addition and never instead. The **External Connector Register** in the [Document Index](../document-index.md#external-connector-register) lists every assigned form; an assignment to an unassigned form is made by EDR.
6. **Power sources are not specified as products.** A bench adapter, a commercial 12 V supply with its output re-terminated, a battery pack, a solar charge controller's load output or a future power distributor is a conformant source if its output meets the specification's source requirements and presents a female / socket-contact M8 3-position connector. The Platform standardizes the DC interface, not the supply behind it. A future power distributor's own input is not required to use this interface where its total exceeds the per-port figures.

## Rationale

The numbers follow from three things that did not exist when EDR-011 was written: a connector derating rule the Platform should obey on its own interface, cable lengths a field bench actually needs, and battery and charger voltages a field source actually presents. The current limit is derated because the alternative is a Platform rule that violates the Platform's own guide. The upper voltage bound is set by the battery under charge because excluding it would make the solar-and-battery case — the reason the interface is not "a 12 V adapter" — non-conformant on day one. The lower bound is where cable drop and battery disconnect meet.

The reservation rule is gender-based rather than form-based because the hazard is gender-based: what must never happen is a live contact entering a port that was not designed for it, and in this system the only live contacts are female and the only male contacts are unenergized. Writing the rule that way lets the common sensor connector stay on measurement ports, which a form-based ban would have forbidden for no safety gain, while giving a new design one sentence to check before it chooses a panel connector.

## Consequences

- AES gains `AES-MOD-006` and the External Connector Register; `AES-HUB-001` is tightened; `AES-MOD-005`'s rationale, [Architecture §7](../03-architecture.md#7-module-hub) and `AES-HUB-003`'s Hub-power sentence are updated; [Terminology §3](../02-terminology.md#3-supporting-terms) updates *Module Power Interface* and *Module Hub*.
- The Module Power Interface specification moves from `0.1` to `0.2`: open figures become fixed, the source and cable sections gain requirements, a mis-mating section replaces the cross-mating bullet. Compatible with every `0.1`-built device that declared a range and current inside the new figures; a `0.1` device outside them is a Draft device that documented its own limits, as `0.1` required.
- **Released within AES `0.11.0`**, a MINOR release: additive and tightening, nothing Released behind it.
- The [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) revises §5.2 (Hub power), §6.2 (figures, contact terminology, the reservation rule, source and cable sizing, prototype sources) and the checklists.
- EDR-011's open-item list is annotated.

## Scope and Remaining Open Items

**Settled by this record:** the input-voltage figures; the current figures and the connector ceiling; source output range; cable conductor minimum and length rule; brownout behavior; Hub power input required; contact terminology; the connector reservation rule and the register; power sources as unspecified products behind a specified interface.

**Open — Platform decisions, taken with the evidence they need:**

- **Inrush figure** — the input capacitance a conformant Module may present, and the inrush a conformant source output tolerates without tripping, from the first source and Module measured together. Until then a Module declares its input capacitance and a source its tolerance.
- **Function of the reserved contact**, if any; **source fault behavior** as a Platform rule; **environmental rating** of connector and cable — unchanged from EDR-011.
- **Measured cable validation** — the computed length figures confirmed on built cables at the current limit.
- A **higher-power power profile** — a second Module Power Interface profile on a larger connector family — if a Module class exceeds 2 A, per EDR-011's review criteria.

**Open — product decisions, recorded with each product:** a Module's power-tree figures within the profile; the mis-mating analysis of any M8 3-position female measurement port; whether a Module or Hub supports USB powering and in which modes; everything about a power distributor.

## Affected Requirements / Documents

- [Architecture §3](../03-architecture.md#3-module-design) — `AES-MOD-005` (rationale), `AES-MOD-006` (new); [§7](../03-architecture.md#7-module-hub) — introductory text, `AES-HUB-001` (tightened), `AES-HUB-003` (Hub-power sentence).
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Module Power Interface*, *Module Hub*.
- [`docs/interfaces/module-power.md`](../interfaces/module-power.md) (`0.1` → `0.2`); [`docs/interfaces/module-port.md`](../interfaces/module-port.md) (cross-mating note points to the register); [`docs/interfaces/README.md`](../interfaces/README.md); [`docs/interfaces/sync.md`](../interfaces/sync.md) (historical note).
- [Document Index](../document-index.md) — External Connector Register (new), interface version table; `STANDARD.md`, `CHANGELOG.md`.
- [EDR-011](./EDR-011-module-external-interfaces-and-power.md) — open-item annotation.
- Hardware Design Guide §5.2, §6.2, §16.

## Future Review Criteria

Revisit if: a Module class needs more than 2 A continuous, which is the case for a second, larger power profile rather than for raising this one; a field source class — a charger or a solar controller in common use — presents more than 15.0 V in normal operation; the first measured inrush shows that the declared-capacitance approach does not protect a common source; or a product needs an M8 3-position male panel connector for a non-power function and no other connector family serves, which would be a case for changing the register by EDR, never for an exception on the product.
