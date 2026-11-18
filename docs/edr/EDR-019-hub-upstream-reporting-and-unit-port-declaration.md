# EDR-019: Hub Upstream Reporting and Unit Port Declaration

## Status

Accepted (2026-11-18)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module Hub or Unit-hosting Module relies on this architecture.*

This record completes the declarations of [EDR-012](./EDR-012-hub-capability-discovery-and-unit-enumeration.md) (Hub capabilities, Unit enumeration) in the light of [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md) (cascading) and [EDR-017](./EDR-017-unit-link-profile-and-family-consolidation.md) (Unit Ports). It supersedes nothing.

## Context

Comparing the first host software and the first hardware against AES `0.14.1` found three places where a device knows something the host needs and no requirement makes it readable.

**A Hub's upstream.** A Module Hub accepts MCI from one upstream at a time — its host-facing interface or one Hub-to-Hub link port ([AES-HUB-005](../03-architecture.md#aes-hub-005-cascading-and-path-addressing)) — and holds that as state. [AES-HUB-004](../03-architecture.md#aes-hub-004-hub-identity-and-capability-discovery) has the Hub report the link state of every port but not which link port its MCI arrives on. The first Hub has two link ports. With one cascaded into an upstream Hub's Module Port and the other on an AEL-only link to a third Hub, both links are up; the host knows from the tree walk that the Hub hangs on the upstream Hub's Module Port, but not which of the Hub's own link ports is the other end of that cable. It needs that index: the events arriving over the cascade are an ingress on that port, and a route table is keyed by ingress port. Today the host can only infer it — by eliminating the AEL-only link the operator declared — and two swapped cables then produce a route table that is wrong without any error.

**A Module's Unit Ports.** [Naming and Identity §5](../04-naming-and-identity.md#5-product-numbers-and-revisions) makes a Module's Unit Port count part of its host-visible contract and says a host learns it from the Module's declarations. [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery), written before Unit Ports existed, has the Module report the Units present and which interface each occupies — not how many ports there are. A host can therefore show the Units it was told about but not an empty port, and it cannot tell a four-port Module with one Unit from a one-port Module. The requirement also still says *Unit Interfaces* where the rest of AES says *Unit Port*, and it passes on a Unit's API version without the API identifier that [AES-UNIT-006](../03-architecture.md#aes-unit-006-declared-capabilities-and-unit-api) has the Unit declare beside it, so that two Units with different APIs at the same version number look alike to the host.

**A device's firmware version.** [AES-MCI-002](../05-interfaces-and-versioning.md#aes-mci-002-module-identity) and `AES-HUB-004` each require "its firmware version". The first Hub has two controllers with separate firmware images, and a Module may contain several Controllers. Which version the identity carries was not said.

## Alternatives Considered

### The Hub's upstream

| Alternative | Assessment |
|---|---|
| **Leave it to inference** from link state and the operator's declaration of AEL-only links | Rejected. It makes a route table depend on a manual declaration being right, and its failure is silent — the class of failure [AES-MCI-002](../05-interfaces-and-versioning.md#aes-mci-002-module-identity) was written against. |
| **Fix the role by port**: one link port is the uplink by construction | Rejected. `AES-HUB-005` makes every link port a possible upstream and fixes roles by port *kind* only; a per-port role would be a product convention the host would have to know by product. |
| **Have the upstream Hub report what is on its Module Port** in more detail | Does not answer the question. The upstream Hub knows its own port index; the index wanted is the downstream Hub's, and only the downstream Hub knows it. |
| **The Hub reports its active upstream** — the host-facing interface or the index of one link port — and any second upstream it has refused (chosen) | A fact about the Hub itself, already held as state, reported in the declaration that already exists. It stays within EDR-012's rule that a Hub reports only its own ports and links. |

### The Module's Unit Ports

| Alternative | Assessment |
|---|---|
| **Leave the count in the product table** and let the host read it from documentation | Rejected; it is the product table in host software that `AES-MCI-003` refuses, and it contradicts Naming §5. |
| **Report the number of Unit Ports and a stable index for each, with one state per port** — unpowered, empty or occupied | Insufficient. A Unit that was identified and refused, on a port the Module then switched off, is both unpowered and occupied; a port whose current limit tripped is unpowered for a reason the three values cannot carry. |
| **Report the number of Unit Ports, a stable index for each, and for each port its power and its occupancy as two facts**, next to the Units already reported (chosen) | Mirrors what `AES-HUB-004` requires of a Hub's Module Ports. An empty port becomes a reported fact instead of an absence, a refused Unit stays visible on its port after the port is de-energized, and a tripped port says why it is off. |

### The firmware version of a device with several images

| Alternative | Assessment |
|---|---|
| **One version per controller in the identity** | Rejected as the identity. A host, a deployment record and a release note need one thing to name; a list of image versions is diagnostic detail and varies with the internal design the identity is meant to hide. |
| **One version for the device — the released set of images — with per-image versions optionally readable, and a mismatched set reported as such** (chosen) | The firmware version of the identity is the version of what was released for the product. A device holding images that are not a released set is in a state the host must see, not one to be summarized by the newest number. |

## Decision

1. **`AES-HUB-004` is extended.** A Module Hub reports its **active upstream**: whether the MCI it is answering arrives through its host-facing interface or through a Hub-to-Hub link port, and in the latter case that port's stable index; and any second upstream it has refused under `AES-HUB-005`, identified in the same way — the host-facing interface, which has no index, when a host is plugged into a Hub that is already cascaded, or a link port by its index. A host takes the far end of a cascaded link from this report and does not infer it from link state, port labels or an operator's declaration.
2. **`AES-MCI-003` is extended and reworded.** A Module that hosts Units reports the number of its Unit Ports, a stable index for each — the index it reports Units under and labels the port with — and for each port two separate facts: its power — off, on, or switched off by the port's own protection, with the reason — and its occupancy — not yet discovered, empty or occupied. A Unit the Module has identified stays reported on its port, with its outcome, after the port is de-energized, until the port is discovered again. The Units present are reported per Unit Port, each with its Unit API identifier as well as its version. A host takes the Unit Port count from this declaration. *Unit Interfaces* becomes *Unit Ports* throughout the requirement.
3. **One firmware version per device.** The firmware version of a Module's or Hub's identity names the device's firmware as released, one version whatever the number of controllers. A device holding more than one image MAY expose each image's version in addition, and reports a set of images that is not a released set as that, never under a release version.
4. **Editorial, alongside:** the product table example of [Naming and Identity §8](../04-naming-and-identity.md#8-name-mapping) lists the link ports and names the host-facing interface correctly; the *Hub-to-Hub AEL link* Terminology entry no longer calls `MCL` cascading open.
5. **Unchanged:** the far end of an AEL-only link is still not identified by anything on the link and is still declared by the operator ([AEL specification](../interfaces/ael.md) Section 8.6); the form of the Hub's management contract and of MCI's encoding remain with the bindings.

## Rationale

Each item makes a fact the device already holds readable, in the declaration that already carries its neighbours. None adds a mechanism.

The upstream is reported rather than fixed by port because fixing it would move knowledge into a product convention. `AES-HUB-005` chose roles by port kind so that every link port is the same hardware and the same firmware; a host that reads the active upstream needs no convention at all, and a Hub with one link port, two or eight answers the same question the same way. The management contract is still the same object from either upstream, as `AES-HUB-005` requires: the active upstream is part of that object, and reads the same whichever way it is fetched.

The Unit Port count belongs in `AES-MCI-003` for the reason the Module Port count belongs in `AES-HUB-004`. Naming §5 already promised it; the requirement now delivers it. Reporting the power and the occupancy of every port, not only the Units found, is what lets a host show a port that looks empty while hardware is plugged into it — the case the refused-Unit rule was written for and could not fully serve.

One firmware version per device follows from what an identity is for. Controllers are an internal partition ([EDR-001](./EDR-001-controller-module-separation.md)); the product is released as a whole, and its record, its compatibility statement and its support history name one version. The mismatch rule is the part that carries weight: a device whose images were updated unevenly is the state a field update produces and a single version number would hide.

All three items are stated at the level of what is reported, not how it travels, and hold unchanged under any MCI transport binding.

## Consequences

- `AES-HUB-004`, `AES-MCI-003` and `AES-MCI-002` are extended; [Terminology §3](../02-terminology.md#3-supporting-terms) (*Unit Port*, *Module Hub*, *Hub-to-Hub link port*, *Hub-to-Hub AEL link*), [Naming and Identity §8](../04-naming-and-identity.md#8-name-mapping) and the [AEL specification](../interfaces/ael.md) Section 8.6 change accordingly.
- **Additive normative change, released as AES `0.15.0`.** Nothing Released exists. A Hub and a Module that already hold these facts conform once they report them.
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) rule that a host cannot tell from a Hub's answers which way it came in is restated: the contract is the same from either upstream, and the active upstream is part of it. It also gains the Unit Port readout and the multi-image version rule. The [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) takes the cascade ingress from the Hub's report. These companion changes are made in their own releases.
- A Hub product whose link ports are labelled as if one were the uplink and the other a downlink describes a convention AES does not have: any link port may be the upstream, and a downstream Hub is reached through a Module Port.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** the active upstream and refused second upstream in a Hub's declaration; the Unit Port count, indices and per-port power and occupancy in a Module's declaration; the Unit API identifier beside its version; one firmware version per device with the mismatch rule.

**Open — decided with the bindings:** the form in which these are reported; how quickly a change of upstream or of a Unit Port's state becomes readable, which is the asynchronous-notification question of [Interfaces and Versioning §5.2](../05-interfaces-and-versioning.md#52-guidance-non-normative).

**Open — product decisions, recorded with each product:** how a product composes its device firmware version from its images; how its link ports are labelled.

## Affected Requirements / Documents

- [Architecture §7](../03-architecture.md#7-module-hub) — `AES-HUB-004` (extended).
- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-003` (extended, reworded), `AES-MCI-002` (firmware version).
- [Terminology §3](../02-terminology.md#3-supporting-terms), [Naming and Identity §8](../04-naming-and-identity.md#8-name-mapping), [AEL specification](../interfaces/ael.md) Section 8.6.
- EDR-012 — its open product item reworded for Unit Ports.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- Firmware Style Guide and Software Style Guide — follow-up in their own releases.

## Future Review Criteria

Revisit if: a use case asks for redundant uplinks, which makes "the active upstream" plural; a binding cannot report a change of upstream soon enough for a host to notice a recabling before it deploys; a Module hosts Units on something that is not a Unit Port; or a product cannot name one firmware version for its images because they are released on separate schedules.
