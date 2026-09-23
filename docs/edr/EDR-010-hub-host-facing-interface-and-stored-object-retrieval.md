# EDR-010: Hub Host-Facing Interface and Stored Object Retrieval

## Status

Accepted (2026-09-18)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module or Module Hub relies on this architecture.*

This record adds to [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) (MCI and Module Hub), [EDR-008](./EDR-008-auriora-event-link.md) (AEL) and [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md) (autonomous operation). It resolves two items those records left open — the Hub's host-facing transport and the retrieval of locally stored data — and supersedes nothing in any of them.

## Context

Three earlier records left the same two gaps in place on purpose. EDR-007 introduced the Module Hub with a "(host-facing transport)" in its diagram and listed that transport as open. EDR-008 made the Hub an AEL router, required it to be host-manageable, recorded MCI reuse as the preferred management contract, and named "bulk measurement-data transport — explicitly not AEL" as a separate concern. EDR-009 gave a Module the right to record for weeks with no host, required it to preserve completion status, event log and the integrity state of its stored data for later readout, and then stated that "retrieval of locally stored data — the bulk-data path — remains outside MCI and AEL and is not designed here". The [worked example](../../examples/worked-example-unattended-field-deployment.md) ended with about 8 GB of data on a Module and no standard way to get it off.

Both gaps are now on the critical path. AURIORA Studio needs one local connection to a Module Hub through which it discovers, configures, deploys, arms and monitors a bench; a Plant Electrophysiology Module returning from the field needs to hand over what it recorded, whether it is plugged into a laptop directly or into a Hub, and whether it recorded under a host or alone. The originating proposal asked for a dedicated USB connection on the Hub, for stored measurement and log retrieval over the managed differential links, for a clear separation between time-sensitive and throughput-oriented traffic, and for the standalone case to use the same retrieval mechanism as the coordinated one.

The proposal was treated as a design to validate. Most of it fits the architecture as it stands and fills recorded open items; parts of it were built on vocabulary and assumptions AES does not share — a management "fabric" between Hubs, a four-class quality-of-service scheme, a transfer session with open, read and complete phases — and those were reconciled rather than adopted. The decision is platform-wide under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger): it changes what a Platform interface (MCI) covers, what a Module Hub is, and the obligations of the firmware, software and hardware guides.

## Alternatives Considered

### What the Hub's host connection is

| Alternative | Assessment |
|---|---|
| **A Module Port used upstream** — the Hub reaches the host over one of its own `MCL`/AEL ports | Rejected. It spends a Module Port and an AEL link pair on a device that has no AEL bindings and no lifecycle, and it makes the host an AEL endpoint, which [AES-MCI-004](../05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary) keeps it from being. |
| **A separate host protocol for Hubs** — USB-specific, distinct from MCI | Rejected. Studio would carry two protocol stacks for one bench, and a Module reached through a Hub would be operated differently from the same Module on a local cable, which [AES-MCI-001](../05-interfaces-and-versioning.md#aes-mci-001-transport-independence) forbids. |
| **A dedicated host-facing interface that is an MCI transport binding — the Hub's instance of the direct local transport — over which the host reaches the Hub's own management and the MCI of every Module on its Module Ports; USB as its first realization, with the Hub as the USB device** | **Chosen.** One binding family for a Module on a cable and a Hub on a cable; the Hub's management contract, whose content EDR-008 left open, is carried the same way; nothing about it is USB-specific above the binding, so a later Hub can add another host transport without touching Module semantics. |

The proposal's terminology was corrected as well. AES uses *host* for the system host — the computer running Studio — and *Host Interface* for the interface a Module exposes to it, so the proposed "USB Host Connection" would read as the Hub acting as USB host controller, which it does not. The interface is named for its role — the Hub's **host-facing interface** — and USB roles are stated where they matter: the Hub is the USB device, the system host is the USB host.

### Where bulk data belongs

| Alternative | Assessment |
|---|---|
| **AEL** — large frames or a payload extension | Rejected without discussion; `AES-AEL-001` excludes it, and the four-byte frame cannot grow by accident. |
| **A new bulk-transport layer** beside MCI and AEL, with its own framing, sessions and flow control | Rejected. AES would carry a third interface for one direction of one kind of object, and a Module would hold two object inventories — one for what it received, one for what it recorded. |
| **A separate service on the MCI transport** — bulk traffic as a distinct protocol multiplexed onto `MCL` and USB | Rejected as a Platform concept. What it separates — control from bulk — is a carriage concern, and carriage belongs to the bindings ([AES-MCI-001](../05-interfaces-and-versioning.md#aes-mci-001-transport-independence)). Made a Platform-level service it would need its own identity, version and error model. |
| **An optional MCI function, *stored object retrieval*, symmetric to the staged transfer of `AES-MCI-005`**: the same inventory with identity and content integrity value, extended with metadata, and offset-based reads in bounded chunks | **Chosen.** MCI already exposes a stored object inventory with content identity so that a host can skip a transfer; reading an object back is the same inventory in the other direction. One object model covers Assets, Sessions, firmware, recordings and logs, and one capability declaration says whether a Module offers it. |

This overrides the sentence in EDR-009 that placed the bulk-data path outside MCI. That sentence recorded an absence, not a decision against MCI; with the object model already in `AES-MCI-005`, keeping retrieval outside would have been the more expensive choice.

### Transfer model

| Alternative | Assessment |
|---|---|
| **A transfer session** — open, read sequentially, acknowledge, complete; resume by reopening at a negotiated offset | Rejected. Session state on the Module is what a disconnected host leaves behind, and resume then depends on the Module still holding it. It also gives an intermediate Hub something to time out. |
| **Stateless offset reads of immutable, content-identified objects**: a completed object never changes; any chunk is readable in any order; an interrupted retrieval resumes from any offset without negotiation; completeness is proven by the whole-object integrity value already in the inventory | **Chosen.** Resume, retry, cancellation and host-paced flow control fall out of the model instead of being features of it; the Module holds no transfer state beyond the request it is answering; a Hub forwards a response only against an outstanding request, so a slow host cannot overflow anything. |
| **Chunk size fixed by AES** | Rejected. The bound is a declared limit per Module and per binding; a Platform-wide figure would be wrong for every second link. |

### Priority between events, control and bulk

| Alternative | Assessment |
|---|---|
| **A four-class priority scheme** — event, interactive control, telemetry, bulk — applied across the network | Rejected as unnecessary. The class the scheme protects first, events, is not on the same wire: the Module Port carries `MCL` and the AEL pairs as electrically independent links and an AEL event never becomes a message on `MCL` ([Architecture §7.1](../03-architecture.md#71-the-module-port)); Hub-to-Hub links carry AEL only; the host-facing interface carries no AEL frames at all. Inside the router, `AES-AEL-005` already requires the timing contract to hold regardless of management load. |
| **No rule** — let bindings arrange it | Rejected. A binding that lets one retrieval occupy the link for the length of an object makes an arm or abort operation wait behind it, and nothing in AES would say that is wrong. |
| **Two classes of MCI traffic — control and bulk — with the chunk as the interleaving unit**: a control operation issued during a retrieval is served within the time of one chunk plus binding overhead, on the same link and, through a Hub, across Module Ports; and the AEL router's published timing SHALL hold while bulk MCI traffic passes through the same device | **Chosen.** It states the invariant the proposal cared about — bulk never monopolizes, events never wait — in the two places where it is not already structural. |

### Cascaded Hubs

| Alternative | Assessment |
|---|---|
| **Decide `MCL` cascading now** so that retrieval is specified across a Hub-to-Hub management path | Rejected. Whether `MCL` cascades is open in EDR-007 and Architecture §7 because it decides whether the binding's addressing is flat or hierarchical, and nothing here needs that decided. The proposal's "fabric port" is not an AURIORA concept: between Hubs there are Hub-to-Hub AEL links, which carry events only. |
| **Specify retrieval end-to-end between host and Module, with every intermediate device forwarding MCI without understanding objects** | **Chosen.** This is already what [AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope) requires of a Hub. However `MCL` cascading is later decided, retrieval crosses it unchanged, because no device between the endpoints was ever allowed to know what a stored object is. |

### Live data, writes and the USB class

| Alternative | Assessment |
|---|---|
| **Define a live measurement stream now** | Rejected. MCI in this version is host-initiated request/response; a Module-pushed stream at acquisition rate needs the asynchronous mechanism that §5.2 leaves open for the first binding. The *distinction* — event, telemetry, live stream, stored recording — is introduced in terminology, and a host that reads the growing tail of an in-progress recording gets live monitoring at modest rates without a new mechanism. |
| **Add delete, upload and general write access with retrieval** | Rejected. Host-to-Module transfer of Assets, Sessions and firmware already exists as staged transfer under `AES-MCI-005`. Retrieval is read-only; deletion, where a Module offers it, is a separately declared operation, and the only implicit destruction of stored data remains the *overwrite oldest* policy a deployer chose under `AES-MCI-006`. |
| **Fix the USB device class in AES** | Rejected. Nothing in AES depends on it; it is a decision of the direct local transport binding specification and of the first products that implement it, recorded there. |

## Decision

1. A Module Hub SHALL provide a **host-facing interface**: the connection through which the system host reaches the Hub's own management contract and, through the Hub's `MCL` concentrator, the MCI of every Module on its Module Ports. It is distinct from Module Ports and Hub-to-Hub AEL links and consumes neither. It is an MCI transport binding — the intended realization is the direct local transport binding also used by a Module on a local cable, extended by the addressing a concentrator needs, which is fixed with that binding. Its first physical realization is USB, on which the Hub is the USB device and the system host is the USB host. AEL frames are not carried on it; the host observes events through logs and counters. It is not the power source of the Hub's Module Ports or of its AEL router. Rule: `AES-HUB-003` in [Architecture §7](../03-architecture.md#7-module-hub).
2. MCI gains an optional function, **stored object retrieval**, and `AES-MCI-003`'s minimum capability list gains **local recording** and **stored object retrieval**. A Module that declares retrieval exposes an inventory of its **stored objects** — recordings, event logs, diagnostic records and committed Assets and Sessions — each with identity, type and, once complete, size and a content integrity value; a recording additionally carries the run and run segment it belongs to, the deployment and Session identities, its local-time and sample-index range, its completion state, its data format identifier and version, and the firmware version that produced it. Rule: `AES-MCI-008` in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface).
3. Retrieval is **stateless, host-paced and read-only**: an object is read by identity, offset and length in chunks bounded by the Module's declared maximum; a completed object is immutable and any part of it is readable in any order; an interrupted retrieval is resumed from any offset without negotiation; the Module never pushes; a retrieval is complete only when the assembled object matches the inventory's integrity value; and retrieval changes no lifecycle state, configuration, stored data or deployment policy. A Module MAY offer reads of an in-progress recording, in which case bytes once readable never change and the inventory says the object is in progress.
4. **Two classes of MCI traffic**, control and bulk, with the chunk as the interleaving unit: a binding and a Hub SHALL serve a control operation issued during a retrieval within the time of one chunk plus binding overhead, on the same link and across Module Ports, and the AEL router's published timing contract (`AES-AEL-005`) SHALL hold while bulk MCI traffic — including retrieval — passes through the same device. No further priority classes are defined.
5. **A Hub forwards retrieval as MCI**, without understanding stored objects, buffering no more than the responses to outstanding requests. Retrieval is specified end-to-end between host and Module; whether `MCL` cascades remains open and does not affect it.
6. **Standalone and coordinated recordings are the same objects.** Provenance — deployment identity, run and segment, deployment policy, segment boundaries — is recording metadata inherited from `AES-MCI-007`; neither Hub nor host needs to know how a recording came to exist in order to enumerate and read it.
7. **Terminology** gains *host-facing interface*, *stored object*, *recording*, *stored object retrieval*, *bulk transfer* and *live measurement stream*; *Module Hub* and *MCI transport binding* are extended. The proposal's terms — "USB host port", "Fabric Port", "fabric link", "RS-485 link" — are not adopted.
8. **Not decided here:** the USB device class and descriptors (binding specification and product); how the direct local binding addresses several Modules behind one Hub (binding specification); `MCL` cascading; a Module-pushed live measurement stream and asynchronous notification in general (first binding); deletion of stored objects; the throughput a Module or Hub must sustain; whether a Hub may be powered from its host-facing interface (product, with documented limits).

## Rationale

The Hub decision follows from a sentence already in AES: a Module reached through a Hub is the same Module, operated the same way, as on a local cable. The only way to keep that true for the host is to reach the Hub with the same binding, and the only way to keep it true for the Hub is to make the Hub an addressable endpoint on that binding rather than a protocol of its own. Everything USB-specific then sits below the binding, where it can be replaced.

Putting retrieval into MCI rather than beside it is what makes the standalone case free. A Module that recorded alone for three weeks already keeps, under `AES-MCI-007`, everything a reader needs to interpret the data — run, segments, boundaries, policy, completion — and already exposes, under `AES-MCI-005`, an inventory with content identity. Retrieval adds the read operation and the metadata fields, and the same enumeration then lists a recording made under a Hub, a recording made alone, and the Session that produced both.

Statelessness is the design's one real idea, and it earns its place several times over. An immutable, content-identified object read by offset needs no transfer session, so nothing is left behind when a host disappears, and resume is a read at a different offset. The Module never sends what was not asked for, so the host's read rate is the flow control, and a Hub that only forwards responses to outstanding requests cannot be overflowed by a slow laptop. Completion is proven by the integrity value the inventory already carried, so the host knows it has the object and not something that looks like it. The chunk bound, finally, is what turns "bulk must not monopolize the link" from a wish into a measurable interleaving rule.

The priority question shrinks once the wiring is looked at. Events are on their own pairs, and the only place bulk and events meet is inside the router's controller, where EDR-008 already made the timing contract independent of management load. What remained unstated was that a control operation must not wait behind an object, and that the router's figures must be measured with bulk running; both are now stated, and nothing more elaborate was found to be necessary.

Deferring `MCL` cascading costs nothing because retrieval was specified end-to-end. An intermediate device that may not understand stored objects has nothing to do differently on a cascaded path, and a decision that determines the addressing model of an unwritten binding is not one to take for the sake of a diagram.

## Consequences

- AES gains `AES-HUB-003` and `AES-MCI-008`; `AES-MCI-003` (capability list) and `AES-AEL-005` (timing under concurrent MCI load) are extended; [Architecture §7](../03-architecture.md#7-module-hub) gains the host-facing interface; [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) gains the retrieval requirement and guidance; [Terminology §3](../02-terminology.md#3-supporting-terms) gains six supporting terms. Frozen core vocabulary is unchanged.
- **This is an additive normative change, released as AES `0.9.0`.** Nothing Released exists; no deployed artifact is affected. MCI still has no version number; the first binding carries it.
- The EDR-009 statement that the bulk-data path lies outside MCI is superseded by this record; EDR-009 is otherwise unchanged and its open-item list is annotated.
- The [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) gains host-side retrieval rules; the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) gains Module-side retrieval rules and Hub forwarding rules; the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) gains the Hub's host-facing USB interface. The private engineering knowledge base is re-derived afterwards.
- The direct local transport binding, when written, must now cover both a single Module and a Hub with several Modules behind it, must define the chunk bound and the interleaving of control and bulk traffic, and must record the USB device class it chooses.
- A Module that declares local recording without retrieval is conformant but hands its data over by other means — a removable medium, a product-specific path — and says so; the Platform path is retrieval.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** the Hub's host-facing interface as an MCI transport binding with USB as first realization and the Hub as USB device; retrieval as an optional MCI function with a stateless, host-paced, read-only, chunked, resumable, integrity-proven model; the minimum recording metadata; the two-class traffic rule with the chunk as the interleaving unit and the router timing contract holding under bulk load; end-to-end retrieval through Hubs that never understand objects; one object model for standalone and coordinated recordings.

**Open — Platform decisions, taken with the evidence they need:**

- **Direct local transport binding**: USB device class and descriptors; framing, correlation, flow control and error signaling; how a Hub and the Modules behind it are addressed on one connection; the chunk bound; the interleaving of control and bulk traffic; host-loss supervision (from EDR-009). One specification answers all of these.
- **`MCL` cascading** — unchanged from EDR-007 and Architecture §7. Retrieval does not depend on it. *Decided in [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md): cascaded through a Module Port with path addressing.*
- **Live measurement stream** at acquisition rate, and asynchronous notification in general: a Module-pushed flow changes what every binding must provide, and is decided with the first binding, as §5.2 already records.
- **Deletion of stored objects** as a declared operation, and the state rules under which it is refused.
- **Retrieval during `RUNNING`**: whether the Platform should require it or leave it declared per Module. Left declared; a long field deployment that must be read out without stopping is the case that would change this.
- **Throughput**: no figure is required of a Module, a Hub or a binding. A field Module returning with gigabytes will decide whether one is needed.

**Open — product decisions, recorded with each product:** whether a Hub may be powered from its host-facing interface and with what limits; a Hub's Module Port and Hub-to-Hub link counts; which Modules offer in-progress reads; the data format identifiers each Module's recordings carry.

## Affected Requirements / Documents

- [Architecture §7](../03-architecture.md#7-module-hub) — `AES-HUB-003` (new); introductory text and diagram; the `MCL` cascading paragraph.
- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-008` (new); `AES-MCI-003` (capability list extended); §5 introduction, §5.1 bindings table and §5.2 guidance. [§4](../05-interfaces-and-versioning.md#4-auriora-event-link) — `AES-AEL-005` (timing contract holds under concurrent MCI load).
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *host-facing interface*, *stored object*, *recording*, *stored object retrieval*, *bulk transfer*, *live measurement stream* (new); *Module Hub*, *MCI transport binding* (extended).
- [EDR-007](./EDR-007-module-control-interface-and-module-hub.md), [EDR-008](./EDR-008-auriora-event-link.md), [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md) — open-item annotations only.
- [Worked Example: Unattended Field Deployment](../../examples/worked-example-unattended-field-deployment.md) — §9 extended with the retrieval of the two recordings.
- [Document Index](../document-index.md), `STANDARD.md` — indexing.
- Software Style Guide §3.5 (extended); Firmware Style Guide §14.3 (extended) and §14.5 (new); Hardware Design Guide §5.2 (new).

## Future Review Criteria

Revisit if: the first binding finds that stateless offset reads cannot meet a real Module's storage architecture without an open-object operation; a control operation's latency behind a chunk proves too long for an abort path at a realistic chunk size; a use case needs retrieval across Hubs before `MCL` cascading is decided and finds that end-to-end specification was not enough; a Module class needs a live stream that polling an in-progress recording cannot approximate; or a second host transport on a Hub reveals something USB-specific that leaked above the binding.
