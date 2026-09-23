# EDR-012: Hub Identity and Capability Discovery, and Unit Enumeration through MCI

## Status

Accepted (2026-09-23)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module Hub relies on this architecture.*

This record adds to [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) (MCI and Module Hub), [EDR-008](./EDR-008-auriora-event-link.md) (AEL router) and [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md) (host-facing interface). It supersedes nothing. The `MCL` cascading item of EDR-007, Architecture §7 and EDR-010 remains open and is deliberately not touched.

## Context

A proposal from the maintainer asked AES to guarantee that a host can map an AURIORA installation — which Modules and Hubs are present, of what type, with which capabilities, on which ports — through the Platform's own discovery and without a hard-coded product list. Concretely it asked for a machine-readable *Module Descriptor* and *Hub Descriptor*, run-time discovery of a Hub's Module Port and Hub-to-Hub link counts so that Hub variants of different sizes share one platform, exposure of a Module's Units to the host, protocol-level rather than presence-pin discovery, and normative rejection of ring topologies. The same proposal asked for `MCL` communication and mutual discovery on the direct 1:1 Module-to-Module link, for a Module to act as a bridge so that a host reaching Module A also reaches Module B behind it, for tree-shaped multi-Hub management topologies, for the term *Cascade Port*, and for the renaming of MCI to `MCL`.

The review against AES `0.9.0` found most of the descriptor content already normative. [AES-MCI-002](../05-interfaces-and-versioning.md#aes-mci-002-module-identity) fixes a Module's identity — Family, Product, Revision, firmware, instance, MCI version and bindings, AOID once Released — and [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery) fixes its declared capabilities — AEL in and out with their limits, recording, retrieval, autonomous continuation, event logging, firmware update — together with the rule that a host queries and never infers. [AES-HUB-002](../03-architecture.md#aes-hub-002-port-independence-and-scale-interoperability) already forbids encoding a port count in any protocol so that Hubs of different sizes interoperate. The Module Port specification already has no presence contact and the Unit Interface already determines presence by discovery, not by a presence pin ([Interfaces and Versioning §3.1](../05-interfaces-and-versioning.md#31-unit-interface-signals-and-profiles)). The [AEL specification](../interfaces/ael.md) Section 8.6 already requires an acyclic Hub-to-Hub topology, validated by the host before deployment, and states that no run-time mechanism compensates for a cycle.

Two things were missing at Platform level. A Hub's *own* identity and capabilities — how many Module Ports, how many Hub-to-Hub links, which index is which, what the router can do — were required nowhere, although the [multimodal worked example](../../examples/worked-example-multimodal-ael-experiment.md) already showed a host reading them and the AEL specification listed the router management contract as open. And a Module's Units, discovered and validated by the Module under [AES-UNIT-007](../03-architecture.md#aes-unit-007-deterministic-discovery-and-activation-sequence), were not required to be reported to the host, although a Hub never reaches them and the Module is therefore the only source.

The remaining items of the proposal were found to depend on decisions AES has left open on purpose, or to conflict with decisions it has made. They are recorded below as not decided or not adopted, so that the next record can take them up with the evidence they need.

## Alternatives Considered

### What the host learns about a Hub

| Alternative | Assessment |
|---|---|
| **Leave the Hub's management contract entirely open**, as AEL §10.2 had it, and let the first Hub product define what it exposes | Rejected. `AES-HUB-002` forbids fixing the port count in a protocol precisely so that Hubs of several sizes coexist; without a run-time readout that freedom pushes the sizes into a product table in host software — the failure `AES-MCI-003` was written to prevent for Modules. |
| **A separate "Hub Descriptor" object with a defined structure** | Rejected as a parallel mechanism. AES already has an identity rule and a capability rule for Modules; a Hub needs the same two things with Hub-specific content. The decision states the content as a requirement on the Hub's management contract and leaves the serialization to that contract, exactly as MCI's own encoding is left to its bindings. |
| **State the content now, leave the form open** (chosen) | The host needs to know what it can rely on; the wire representation is decided once, with the binding, from bring-up evidence. Fixing content early and form late is how MCI itself was introduced. |
| **Identify the far end of each Hub-to-Hub link** as part of the Hub's capabilities | Deferred. An AEL link carries frames with no device identity; learning the neighbour needs either `MCL` on that link or an identification exchange, both of which are the open cascading decision. A Hub reporting only its own ports and links stays correct either way. |

### What the host learns about a Module's Units

| Alternative | Assessment |
|---|---|
| **Leave Unit enumeration to each Module's product documentation** | Rejected. The Module already reads every Unit's EEPROM identity and declared capabilities and already decides whether to activate it; withholding that from the host makes the host guess from the Module type what is behind it, and hides a Unit that was refused. |
| **Report Units through the Hub** | Rejected; `AES-HUB-001` keeps the Hub away from Units and from Module-specific meaning. |
| **Extend `AES-MCI-003` with the Units present, their identity, declared model and capabilities, the Unit Interface each occupies and its activation outcome** (chosen) | Reuses Unit discovery unchanged; adds no Unit protocol; makes a refused Unit visible instead of silently absent. |

### Items of the proposal not adopted or not decided here

| Item | Assessment |
|---|---|
| **Rename MCI to `MCL`** and treat them as one interface | Not adopted. In AES they are two layers: MCI is the transport-independent contract, `MCL` one wired binding of it, the direct local transport (USB) another. Collapsing them leaves the contract on the host-facing interface without a name and contradicts the proposal's own separation of host connection and Module Port. |
| **A "Module Descriptor" as a new object** | Not adopted; `AES-MCI-002` and `AES-MCI-003` already are that descriptor, now extended with Units. Its encoding remains with the bindings. |
| **`MCL` active on the direct 1:1 link, with mutual discovery** | Not decided. `MCL` has the Hub as polling master; on a Link Cable between two Modules the pair joins two responder ends and is idle ([Module Port specification](../interfaces/module-port.md)). Activating it requires a master rule for a peer link — the "two masters on one pair" item that specification lists as open. A separate record. |
| **Module A as bridge to Module B; host-side management trees across Hubs; topology discovery across Hub-to-Hub links** | Not decided. Each is the `MCL` cascading decision — flat or hierarchical addressing in the binding — that EDR-007, Architecture §7 and EDR-010 left open. Today a host reaches every Hub through that Hub's own host-facing interface and supports several at once (`AES-HUB-002`). A separate record, together with the item above. |
| **Run-time recognition of a ring topology** | Not adopted now. AEL §8.6 already requires an acyclic topology, validated by the host, and records that no hop count, spanning tree or duplicate suppression exists. Recognizing a cycle at run time requires knowing what is at the far end of each link, which is the deferred item above; a requirement without a mechanism would bind nobody. Revisited with that decision. |
| **The term *Cascade Port*, with upstream/downstream roles** | Not adopted. AES names the connector a Hub-to-Hub link port; it is a Module Port connector, the Link Cable is non-oriented, and the two AEL directions in it are already independent, so no fixed IN/OUT role exists to remove. The name is reconsidered with the cascading decision. |
| **A physical presence-detect for the direct link** | None exists on the Module Port and none is added; discovery-based presence is the Platform's existing rule for Units and applies here once `MCL` on the direct link is decided. |
| **Fix Hub port counts, encodings, field sizes, maximum depth, address width** | Not fixed; each is a product decision or belongs to the binding specification, as the proposal itself asked. |

## Decision

1. AES gains **`AES-HUB-004` Hub Identity and Capability Discovery** in [Architecture §7](../03-architecture.md#aes-hub-004-hub-identity-and-capability-discovery). Through its host-facing interface and before configuration a Module Hub exposes a persistent identity with the content and path-independence `AES-MCI-002` requires of a Module, plus the AEL version and MCI bindings it implements, and its capabilities: the number of Module Ports and of Hub-to-Hub AEL links, a stable index for each, the link state of each, event origination and its limit, and the router's declared figures; per-index capability where ports differ. The host takes counts and figures from these declarations and never from product knowledge; a Hub refuses a configuration that names a port or link it lacks with a defined error. The requirement fixes the content of the Hub's management contract and leaves its form to that contract. It identifies nothing at the far end of a Hub-to-Hub link.
2. **`AES-MCI-003` is extended**: a Module that hosts Units exposes through MCI the Units present — the electronic identity read through Unit discovery, the declared execution model and capabilities, the Unit Interface each occupies, and whether it was activated or refused and why. No new Unit protocol; the Hub is not involved.
3. **Terminology**: the *Module Hub* entry states what the host learns from it. No new frozen or supporting term is introduced; *Cascade Port*, *Module Descriptor* and *Hub Descriptor* are not adopted.
4. **AEL specification §10.2**: the *router management contract* item now fixes its content by `AES-HUB-004`, leaves its form open and names the host-facing interface as its transport; the *identity and naming* item reduces to naming.
5. **Not decided here**, and left for a following record: `MCL` on the direct 1:1 link and its master rule; `MCL` cascading with its addressing model; a Module acting as bridge to a directly connected peer; host-side topology discovery across Hub-to-Hub links and run-time loop recognition; the name of the Hub-to-Hub link port.

## Rationale

The decision states once, for Hubs, what AES already states for Modules: identity is persistent and independent of the path, capabilities are declared by the device and read by the host, and the host never keeps a product table. It follows from `AES-HUB-002` rather than adding to it — a rule that forbids fixing the port count in the protocol only works if the count is readable at run time, otherwise it has moved the count into host software, not removed it.

Content is fixed and form is not, for the same reason MCI was introduced without a binding: what the host can rely on is an architectural commitment, and the wire representation is an engineering result of the first Hub's bring-up. A stable per-port index is the one structural element required, because a route table, an observability counter and a recorded bench topology all have to name a port, and a name that changes with enumeration order is the Hub-side version of the device-node failure `AES-MCI-002` was written against.

Units are reported by the Module because nothing else can report them. The Module already holds each Unit's identity and declared capabilities and has already decided whether to activate it; the requirement only makes that knowledge readable. The activation outcome is included because a Unit that is present but refused is the case a host most needs to see and is otherwise indistinguishable from an empty interface.

The far end of a Hub-to-Hub link is left out on purpose, and with it loop recognition and the management tree. Each requires deciding whether `MCL` cascades and how the binding addresses across Hubs, a decision AES has deferred three times for the same reason — it fixes the addressing model of an unwritten binding — and a Hub that reports only itself is correct under either outcome. Recording the deferral here, with the proposal's items attached to it, is what lets the next record take them up together instead of piecemeal.

## Consequences

- AES gains `AES-HUB-004`; `AES-MCI-003` is extended; [Architecture §7](../03-architecture.md#7-module-hub), [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface), [Terminology §3](../02-terminology.md#3-supporting-terms) and the [AEL specification](../interfaces/ael.md) Section 10.2 change accordingly. Frozen core vocabulary is unchanged.
- **This is an additive normative change, released as AES `0.10.0`.** Nothing Released exists; no deployed artifact is affected. MCI still has no version number; the first binding carries it. A Hub that already exposes port counts and router figures conforms once it does so through its management contract with a stable index; a Module without Units conforms without change.
- The Hub's management contract, when specified, must carry the identity and capability content of `AES-HUB-004` and define its form; the direct local transport binding, which reaches the Hub, is where that form is expected to be defined ([EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md)).
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) is expected to gain Hub-side identity and capability rules and Module-side Unit reporting; the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) host-side rules that take a Hub's size from the Hub and never from its product. These companion changes are made in their own releases. The private engineering knowledge base is re-derived afterwards.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** the content of a Module Hub's identity and capability declaration and the host's obligation to use it; Unit enumeration through MCI; that no separate descriptor object, no Hub-side far-end identification and no run-time loop mechanism is introduced now.

**Open — Platform decisions, taken together in a following record:**

- **`MCL` on the direct 1:1 link**: whether the pair carries `MCL` between two Modules, which end initiates, and how two Modules discover each other over it. Depends on the `MCL` binding's line discipline ([Module Port specification](../interfaces/module-port.md) Section 8).
- **`MCL` cascading and addressing**: whether a Module Port may feed another Hub's management path, flat or hierarchical addressing in the binding, and with it a Module as bridge to a directly connected peer, host-side discovery of the device at the far end of a Hub-to-Hub link, run-time recognition of a cycle, and the name of the Hub-to-Hub link port.
- **The form of the Hub's management contract** — MCI reuse preferred — decided with the direct local transport binding.

**Open — product decisions, recorded with each product:** a Hub's Module Port and Hub-to-Hub link counts and whether its ports differ in capability; which Modules host Units and how many Unit Interfaces they present.

## Affected Requirements / Documents

- [Architecture §7](../03-architecture.md#7-module-hub) — `AES-HUB-004` (new).
- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-003` (Unit enumeration added to requirement and rationale).
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Module Hub* (extended).
- [AEL specification](../interfaces/ael.md) Section 10.2 — *router management contract* and *identity and naming* items reworded.
- [Worked Example: Multimodal AEL Experiment](../../examples/worked-example-multimodal-ael-experiment.md) — the Hub capability readout referenced to `AES-HUB-004`.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- Firmware Style Guide and Software Style Guide — follow-up in their own releases.

## Future Review Criteria

Revisit if: the first Hub's bring-up finds that a stable per-port index cannot be kept across firmware updates or port-module replacement; a host needs the far end of a Hub-to-Hub link before the cascading decision is taken; a Module class hosts Units whose identity cannot be read before activation, so that the enumeration would have to be reported in stages; or the `MCL` peer-link decision changes what a Module must expose about a directly connected neighbour.
