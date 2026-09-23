# EDR-013: MCL Cascading and Path Addressing

## Status

Accepted (2026-09-23)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module Hub relies on this architecture.*

This record closes the `MCL` cascading item that [EDR-007](./EDR-007-module-control-interface-and-module-hub.md), [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md), [EDR-011](./EDR-011-module-external-interfaces-and-power.md) and [EDR-012](./EDR-012-hub-capability-discovery-and-unit-enumeration.md) left open, and with it the peer-link, bridge, topology-discovery and loop questions EDR-012 attached to it. It also closes four smaller items that needed no measurement: the Hub's route table after a reset (EDR-009), MCI as a Release requirement (EDR-007), the Hub's AOID class (EDR-007) and the Module's declared event sources. It supersedes nothing; where it changes a Draft rule it says so.

## Context

AES `0.9.0` reached every Module Hub through that Hub's own host-facing interface and scaled events through Hub-to-Hub AEL links, leaving open whether `MCL` may be cascaded — a Module Port feeding another Hub's management path — because that decides whether the `MCL` binding's addressing is flat or hierarchical. EDR-012, earlier the same day, fixed what a Hub declares about itself and deferred cascading once more, collecting the items that depend on it.

Two facts made the deferral untenable. The host-facing interface is a few metres of USB; the Link Cable is an RS-485-class run. A bench spread across a room, or a deployment across a greenhouse, cannot be one USB cable per Hub, so cascading is not optional for the Platform's own use cases. And the `MCL` binding cannot be written without knowing whether it addresses one Hub's ports or a tree, so every day the decision waited was a day the binding could not start.

The maintainer's product plan for the first Hub — eight Module Ports and two Hub-to-Hub link ports, one link toward the host side and one toward a further Hub, always one root Hub on the host — was the concrete case the model had to fit without a hardware change.

## Alternatives Considered

### How a downstream Hub is reached

| Alternative | Assessment |
|---|---|
| **No cascading**; every Hub on its own host-facing interface, as in `0.9.0` | Rejected. Distance alone rules it out; it also makes the host's topology view a set of unrelated trees joined by AEL-only links it cannot discover. |
| **Cascade through a Module Port**: a downstream Hub's link port cabled to an upstream Hub's Module Port, the upstream Hub polling it exactly as it polls a Module (chosen) | Reuses the master role every Module Port already has and the responder role every Module already implements. No new port type, no new cable, no new transceiver; the role of each port is firmware and is declared per index under `AES-HUB-004`. An upstream Hub needs no knowledge of what hangs on a port to forward to it. |
| **Dedicated cascade ports** with fixed IN and OUT roles, a daisy chain | Rejected as a Platform rule, accepted as a product labelling. A "cascade OUT" port whose `MCL` end is a master and whose AEL pairs cross in the cable *is* a Module Port; giving it a second name in the standard would create two rules for one thing. The first Hub may label one Module Port *Downstream Hub* and place it beside the link port; the standard sees nine Module Ports and one link port. A fixed chain also forces the deepest event path to grow with every Hub, where a tree keeps it short. |
| **Roles negotiated on the wire** — any port may become master or responder depending on what it finds | Rejected. On a half-duplex pair this is an election with collision handling in every Hub's firmware, exactly the class of mechanism AES has avoided everywhere else, and it makes the outcome of plugging in a cable depend on timing. Fixed roles by port kind make two like ends meeting on a cable either silence (two responders) or a detectable fault (two masters), never a negotiation. |

### Addressing

| Alternative | Assessment |
|---|---|
| **Flat addresses** assigned at discovery, routed by tables in each Hub | Rejected. Needs an allocation protocol, tables in every Hub, and a rule for what happens to addresses when a cable moves — the machinery of a network for a tree of at most a few Hubs. |
| **Path of port indices from the root Hub** (chosen) | The `AES-HUB-004` stable index already exists; a Hub forwards to the port its element names and strips it, interpreting nothing (`AES-HUB-001`). Topology discovery is a walk of the tree. A cycle cannot be expressed. Identity stays separate from path (`AES-MCI-002`), so recabling changes addresses, not identities, and the host follows devices by identity as it already must. |
| **Fix the path element width and maximum depth now** | Rejected; both are the binding's, decided with its frame format. AES states the model, not the field. |

### Upstream rule and faults

| Alternative | Assessment |
|---|---|
| **One upstream per Hub** — its host-facing interface or one link port — with a second refused and reported (chosen) | Makes the management topology a tree by construction; a Hub that finds itself polled from two sides reports it rather than choosing. The management contract is one object seen the same from either upstream. |
| **Allow several uplinks for redundancy** | Rejected for this version. Redundant paths are a routing problem with a failover rule; no use case asks for it, and it would reintroduce the cycle question. |
| **Two Hubs' Module Ports cabled together** | A cabling fault. Each port detects and reports it; nothing is damaged, because every port already survives any cable indefinitely. How the binding's contention rule detects it stays with the binding. |
| **Two link ports cabled together** | Remains what it was: an AEL-only Hub-to-Hub link, two responders on an idle `MCL` pair. Allowed because it costs nothing and keeps the like-ends rule complete; the product family does not plan to use it, since one root Hub and cascading cover every planned installation. |

### The binding consequence

| Alternative | Assessment |
|---|---|
| **Lock-step request-response** on each `MCL` link, with the response time bounded per Module | Rejected. A request that travels through a downstream Hub to a Module behind it cannot answer within the response time of a Module on the port; the upstream Hub would have to know the depth behind each port and scale its timeouts. |
| **Tagged correlation**: a request is acknowledged, its response is carried in a later exchange under its identifier (chosen) | Already listed as "request correlation" in the binding's open items; cascading decides its direction. A Hub forwards without holding state beyond the outstanding requests it already may hold under `AES-HUB-003`. |

### The direct 1:1 link

| Alternative | Assessment |
|---|---|
| **`MCL` between two Modules**, one of them polling, and a Module as bridge so that a host on Module A reaches Module B | Rejected, permanently. A Module that polls a peer and forwards MCI is a Hub with fewer ports; giving Modules that role is the Controller-and-Module blurring the Platform has refused since EDR-001. The two-Module case is served by each Module's own service connection (EDR-011) or by a small Hub. |
| **Direct link carries AEL only; the `MCL` pair joins two responders and is idle; a Module is never an `MCL` master** (chosen) | This was already the physical state of the link; the decision makes it the rule rather than a consequence of the binding not being written. It is worth stating once and keeping in mind: "two Modules can be connected directly" is true for events and false for control. |

### Loop recognition

| Alternative | Assessment |
|---|---|
| **A run-time loop mechanism** — hop count, spanning tree, duplicate suppression | Rejected, unchanged from EDR-008. |
| **Structural impossibility on the management tree, host validation for AEL-only links** (chosen) | With one upstream per Hub, a cycle in the management topology cannot be addressed and a Hub reached twice is reported by the second upstream. Every cascaded link is therefore known to the host from discovery. An AEL-only link between two link ports is operator-declared and host-validated, as before; with one root Hub such links do not occur. |

### Items closed alongside

| Item | Decision |
|---|---|
| **Hub route table after a reset** (EDR-009) | A router reinstates nothing unless the host has set a **route recovery policy** of *reinstate*, held persistently; then it restores the last committed table only after its content identity verifies, records the reinstatement with the reset cause and reports it. Default *none*. The Module already has this pattern in its deployment policy (`AES-MCI-006`, `AES-MCI-007`); a Hub-connected unattended deployment was the one case the Platform could not survive. |
| **MCI mandatory for Released Modules** (EDR-007) | Yes: over at least one Released binding, over `MCL` where the Module has a Module Port; no substitute protocol. Every Platform promise about a bench is a promise about MCI. |
| **Hub AOID class and family** (EDR-007) | AOID class `HUB`; family identifier `AMH` (AURIORA Module Hub), first product AMH-01, `AOID:PUB:HUB:GEN:AMH:001` reserved provisionally in the Document Index. |
| **Declared event sources and actions** | `AES-MCI-003` now requires a Module to declare its logical event sources and receivable actions with stable names or indices; the AEL specification's "semantic names live in Module documentation" becomes "in the Module's declared sources and actions". Without it a host still needed a product table to build bindings. |

## Decision

1. AES gains **`AES-HUB-005` Cascading and Path Addressing** in [Architecture §7](../03-architecture.md#aes-hub-005-cascading-and-path-addressing): a Module Port's `MCL` end is the master and a Hub-to-Hub link port's a responder; a downstream Hub's link port on an upstream Hub's Module Port carries cascaded `MCL` and a Hub-to-Hub AEL link; one upstream per Hub, a second refused and reported, one management contract from either; devices addressed by the path of port indices from the root Hub, each Hub forwarding to the named port without interpreting the rest; link-port-to-link-port is AEL only; Module-Port-to-Module-Port between Hubs is a reported cabling fault; the binding correlates requests and responses by identifier and never assumes lock-step; a Module is never an `MCL` master and the direct 1:1 link is AEL only. Path element width, depth and per-hop MCI latency are the binding's.
2. **`AES-AEL-005`** and the AEL specification's §8.4 change compatibly: reinstatement of a route table after reset only under a host-set, persistently held **route recovery policy**, *none* by default or *reinstate* after content identity verifies, recorded and reported; the router declares which it supports. Architecture §7's Hub paragraph and EDR-009's open item are updated.
3. AES gains **`AES-MCI-009` MCI in Released Modules**.
4. **`AES-MCI-003`** additionally requires the Module's logical event sources and receivable actions with stable names or indices.
5. **AOID** class `HUB`; `AOID:PUB:HUB:GEN:AMH:001` reserved provisionally for the AURIORA Module Hub.
6. **Terminology**: *Module Control Link* and *Module Port* extended; *Hub-to-Hub link port* added. *Cascade Port*, *upstream port* and *downstream port* are not terms of the standard; a product may print such labels.
7. **The first Hub product** needs no hardware change for this decision: its ten identical ports are declared as nine Module Ports and one Hub-to-Hub link port, one Module Port labelled for a downstream Hub. That is a product decision recorded here as the case the model was checked against, not as a rule.

## Rationale

The whole decision follows from taking the roles AES already had and refusing to add a third. A Module Port polls; a Module answers; a Hub is a box of Module Ports with one management contract. Making a downstream Hub *answer on one port* and *poll on the others* is the smallest possible extension: the responder code is the Module's, the master code is the Hub's, and forwarding is stripping one index. Nothing in it needs a Hub to know what is on a port, which is `AES-HUB-001` kept intact one level deeper.

Fixed roles are the safety of the design. Every alternative that let a port decide its own role put an election on a half-duplex pair, and an election is the one thing that can make plugging in a cable produce a different bench on different days. With roles by port kind, the outcome of every possible cabling is known before power is applied: like ends are silent or faulted, unlike ends work. That property is worth more than the Module Port it costs to hang a Hub on.

Path addressing is chosen because a tree is all there is. One upstream per Hub is what makes it a tree, and once it is one, a path is the natural name of a leaf, discovery is a walk, and a cycle is not a failure mode but a syntax error. The standard's earlier insistence that identity never derive from position (`AES-MCI-002`) is what makes path addressing safe: the path may change with a cable, the Module does not, and the host already had to cope with that.

The direct link is settled negatively because the alternative was a Module pretending to be a Hub. The sentence to keep in mind is that two Modules connect directly *for events*; for control each is reached over its own service connection. That asymmetry is now a permanent feature of the Platform and not an artifact of the binding's timing.

The four items closed alongside share one property: each needed a decision, not a measurement, and each had been waiting on nothing but attention. The route recovery policy in particular was the last gap between a Module that survives a power loss alone and a bench that does not survive one with a Hub in it.

## Consequences

- AES gains `AES-HUB-005` and `AES-MCI-009`; `AES-AEL-005` and `AES-MCI-003` are extended; [Architecture §7](../03-architecture.md#7-module-hub) is rewritten around one root Hub and a tree; [Terminology §3](../02-terminology.md#3-supporting-terms) gains *Hub-to-Hub link port*; [Naming](../04-naming-and-identity.md) gains AOID class `HUB`; the [AEL](../interfaces/ael.md) and [Module Port](../interfaces/module-port.md) specifications are aligned. Frozen core vocabulary is unchanged.
- **This is an additive normative change, released as AES `0.10.0`** together with EDR-012. The one rule that changes, `AES-AEL-005`'s reinstatement clause, changes compatibly: a router that never reinstates conforms under the default policy. Nothing Released exists.
- The **`MCL` binding**, when written, is hierarchical: it carries a path of port indices, defines the element width and maximum depth, uses tagged request-response correlation, and states how a master detects another master. Its response-time rule is per hop, not per Module.
- The **Hub's management contract** is reachable through the host-facing interface and through cascaded `MCL`, and is the same object on both.
- The **first Hub product** declares nine Module Ports and one link port; one Module Port may be labelled for a downstream Hub. Hubs of other sizes remain interoperable under `AES-HUB-002`.
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) is expected to gain the Hub's two `MCL` roles, path forwarding, the one-upstream state and route recovery; the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) tree discovery by path, addressing by identity with path as metadata, and the route recovery policy as a deployment setting; the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) notes that all Hub ports are identical hardware with roles in firmware. These follow in their own releases. The private engineering knowledge base is re-derived afterwards.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** the cascading model, roles by port kind, one upstream per Hub, path addressing, the fate of every like-ends cabling, tagged correlation as a binding requirement, the direct link as AEL only with no Module ever an `MCL` master, loop handling, route recovery policy, MCI at Release, the Hub's AOID class and family, declared event sources and actions.

**Open — decided with the `MCL` binding specification:** path element width and maximum depth; the per-hop MCI latency budget and the resulting response-time rule; how a master detects another master on the pair; the tag space and lifetime of request correlation; whether a downstream Hub may hold responses for a slow upstream beyond the outstanding-requests bound; host-loss supervision across a cascade. **Decided with the first Hub's bring-up:** every electrical, cable and timing figure already listed open in the Module Port and AEL specifications.

**Open — Platform decisions not touched here:** cross-Module clock alignment and absolute time (EDR-005, EDR-008, EDR-009), the next architectural record; redundant uplinks, if a use case ever asks for them; the security posture of a network-facing Hub (EDR-007).

**Open — product decisions, recorded with each product:** the number of Module Ports and link ports and which Module Port, if any, is labelled for a downstream Hub; whether a Hub supports *reinstate*; the recommended maximum depth of a product's Hubs from its measured per-hop figures.

## Affected Requirements / Documents

- [Architecture §7](../03-architecture.md#7-module-hub) — `AES-HUB-005` (new); Hub paragraph (route recovery policy) and scaling paragraph rewritten; `AES-HUB-004` far-end sentence; §7.1 direct-link bullet and open-item list.
- [Interfaces and Versioning](../05-interfaces-and-versioning.md) — `AES-AEL-005` (reinstatement clause), `AES-MCI-003` (event sources and actions), `AES-MCI-009` (new), §5.1 bindings table.
- [AEL specification](../interfaces/ael.md) — §6 (semantic names), §8.4 (recovery), §8.6 (cascaded and AEL-only links), §10.2 (transport of the management contract).
- [Module Port specification](../interfaces/module-port.md) — direct-link bullet, topology row, §8.1 settled roles, §8.2 open items narrowed.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Module Control Link*, *Module Port* (extended); *Hub-to-Hub link port* (new).
- [Naming and Identity](../04-naming-and-identity.md) — AOID class `HUB`. [Document Index](../document-index.md) — `AOID:PUB:HUB:GEN:AMH:001`.
- [Worked Example: Multimodal AEL Experiment](../../examples/worked-example-multimodal-ael-experiment.md) — H2 as a downstream Hub on H1's Module Port 3.
- [EDR-007](./EDR-007-module-control-interface-and-module-hub.md), [EDR-008](./EDR-008-auriora-event-link.md), [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md), [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md), [EDR-011](./EDR-011-module-external-interfaces-and-power.md), [EDR-012](./EDR-012-hub-capability-discovery-and-unit-enumeration.md) — open-item annotations only.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- Firmware Style Guide, Software Style Guide, Hardware Design Guide — follow-up in their own releases.

## Future Review Criteria

Revisit if: the first binding finds that a downstream Hub's forwarding latency, multiplied by a realistic depth, exceeds what an abort path can tolerate; a deployment needs a redundant uplink; a use case needs two Modules to exchange control without a Hub and without a host on each; the one-upstream rule proves too strict for a Hub that must be commissioned over USB while cascaded; or route reinstatement under *reinstate* is found to re-arm anything a host would not have re-armed.
