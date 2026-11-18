# EDR-020: Retrieval by Removable Medium

## Status

Accepted (2026-11-18)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module relies on this architecture.*

This record adds to [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md) (stored object retrieval) and [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md) (autonomous operation). It answers the *Throughput* item EDR-010 left open and changes one of its consequences: a removable medium is no longer only the alternative of a Module without retrieval. It supersedes nothing.

## Context

EDR-010 made stored object retrieval over MCI the Platform's path for getting recorded data off a Module, and noted that a Module declaring local recording without it "hands its data over by other means — a removable medium, a product-specific path". It required no throughput of any Module, Hub or binding, and recorded when that would be revisited: "a field Module returning with gigabytes will decide whether one is needed."

The first autonomous recording Module is that case. It records to a removable card and also declares retrieval. At its highest continuous profile it stores 96 kB/s, 8.3 GB per day. Its direct local transport is full-speed USB, which moves roughly 1 MB/s at best: more than two hours of reading for each recorded day, more through a Hub. A week in the field is most of a day at the bench. People will take the card out.

When they do, nothing in AES applies. [AES-MCI-008](../05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval) defines what a host can rely on when it reads over MCI — an inventory, an integrity value per object, the metadata that make a recording a dataset. It says nothing about what is on the medium. A host that reads the card sees files. It cannot verify them against anything, cannot tell a complete recording from one that was being written when the card was pulled, and has to reconstruct run, segment, Session and time from file names — the reconstruction that the retrieval rules exist to make unnecessary. The Module declares retrieval, so even the obligation to document another path does not bind it.

The requirement behind retrieval was that a recording made alone in the field and one made under a Hub are indistinguishable to the tool that reads them. Unless the medium is a Platform path, that holds only for recordings small enough to be read over a cable.

## Alternatives Considered

### Whether the medium is a Platform path

| Alternative | Assessment |
|---|---|
| **Leave it to each product** | Rejected. Every recording Module with a card would define its own layout and its own importer, and host software would special-case each — for the Platform's largest datasets. |
| **Require a throughput** of retrieval instead, so that nobody needs to remove the card | Rejected as the only answer. A figure that makes 60 GB practical over a service cable fixes the transport of every recording Module, and a card in a reader will still be faster. EDR-010's position that no figure is required stands. |
| **Make the medium a second, declared retrieval path that yields the same objects with the same proof** (chosen) | The object model does not change. What is added is a place to read the inventory from when the Module is not there. |

### What the medium carries

| Alternative | Assessment |
|---|---|
| **Self-describing files only** — each recording carries its own metadata and digest | Insufficient alone. It cannot say which objects *should* be on the medium, so a missing or truncated file is undetectable, and logs and non-recording objects would each need their own header. |
| **A manifest: the Module's identity and, for every stored object on the medium, the inventory entry `AES-MCI-008` requires, with where the content is** (chosen) | The inventory a host would have read over MCI, written next to the objects. Verification and provenance are then the same operations on the same values. |
| **Fix the file system and the manifest encoding now** | Not now. Content is fixed and form is not, as for MCI and for the Hub's management contract: the encoding is an engineering result of the first Module and is fixed in a versioned specification before any Module claims Released conformance. |

### Removal and foreign media

| Alternative | Assessment |
|---|---|
| **Forbid removal except in `IDLE` or `COMPLETE`** | Unenforceable; a card can be pulled at any moment. The requirement is on what survives. |
| **Whatever is listed complete is complete, at any instant of removal or power loss; what was in progress is listed incomplete** (chosen) | The power-loss discipline AES already requires of persistent deployment state, applied to the manifest. |
| **Let a Module record onto any medium it is given** | Rejected for a medium that names another Module or fails validation: writing onto it mixes two Modules' objects under one manifest or destroys evidence. A medium with no manifest is different — initializing it discards nothing a Module wrote. |

### Proof of origin

| Alternative | Assessment |
|---|---|
| **Treat a verified import as equal to a verified retrieval** | Not quite true. Both prove the copy matches the inventory; only the retrieval was read from the Module. A medium has been outside the Module's control, and nothing prevents its content and manifest from being rewritten together. |
| **Record the path, and leave a signed manifest for when origin matters** (chosen) | The host records how each object reached it. A manifest signature is the mechanism where origin has to be proven, defined by EDR when the first use case needs it — the position `AES-EEPROM-007` takes for the Unit identity record. |

## Decision

1. AES gains **`AES-MCI-011` Retrieval by Removable Medium** in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#aes-mci-011-retrieval-by-removable-medium).
2. **A declared, optional function.** A Module that keeps stored objects on a medium a user can remove MAY declare **medium retrieval**; one that records to such a medium SHOULD. It is declared in addition to stored object retrieval, not instead of it, and both paths yield the same objects.
3. **The medium manifest.** A Module that declares medium retrieval keeps on the medium a manifest carrying its schema version, the identity of the Module that wrote it, and for every stored object on the medium the inventory entry of `AES-MCI-008` — recording metadata included — together with where the object's content is found, and an integrity value over the manifest itself. An object on the medium is byte-identical to the object the Module would serve over MCI under the same identity.
4. **Consistent at any instant.** After a power loss or a removal at any moment, every object the manifest lists as complete is present and matches its integrity value, and an object that was in progress is listed as incomplete.
5. **Removal is detected and recorded.** A Module reports the absence of its medium, refuses to arm a Session that records while none is usable, and treats removal while `ARMED` or `RUNNING` as a storage fault under its declared fault classes.
6. **A foreign medium is not written.** A medium whose manifest names another Module, is invalid or is of an unsupported schema is reported and left untouched until a host explicitly initializes it — a deletion, under the deletion rule of `AES-MCI-008`. A medium with no manifest MAY be initialized by the Module itself.
7. **The host imports as it retrieves.** A host reads the manifest first, takes identity, metadata and provenance from it and never from file names, paths or file-system dates, treats an object as retrieved only when its content matches the manifest's integrity value, modifies nothing on the medium, and records for each object whether it was retrieved over MCI or imported from a medium.
8. **Form is open.** The file system and the manifest encoding are fixed in a versioned specification with the first Module that declares medium retrieval.

## Rationale

The decision adds no second model. A stored object is still immutable once complete, still identified, still proven by one integrity value; the manifest is the inventory written down. That is why the host obligations fit in one sentence: everything a tool does with a retrieved object it does with an imported one, from the same values.

Consistency at any instant is the requirement that carries the weight. A card is removed by a person standing in a greenhouse, not by a protocol, and the only useful promise is about what the card then contains. Stating it as "complete means complete" lets a Module choose its own mechanism — a journal, two manifest slots, closing objects at intervals — and makes the cost visible: the data written since the last closed object is at risk on removal, which is a figure a product can state and a user can plan around.

Refusing a foreign medium follows from the same rule that keeps deletion out of retrieval. Recording onto another Module's card silently is the one action that can make a field recording unrecoverable or misattributed, and a Module cannot tell a mistake from an intention. A blank medium is excluded from the refusal because the field workflow depends on it: a full card is exchanged for an empty one with no host present.

The path is recorded because the two proofs differ and a record should say which one it has. Requiring a signature now would bind every Module to key handling for a need no deployment has stated.

The decision does not depend on the transport that made it necessary. A faster MCI binding would move the point at which people reach for the card; it would not remove recordings made where no host is, or the reader in a laptop.

## Consequences

- AES gains `AES-MCI-011`; [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery) lists medium retrieval among the declared functions; [AES-MCI-008](../05-interfaces-and-versioning.md#aes-mci-008-stored-object-retrieval) is unchanged; [Terminology §3](../02-terminology.md#3-supporting-terms) gains *Medium retrieval* and *Medium manifest*.
- **Additive normative change, released as AES `0.15.0`.** Nothing Released exists. A Module without a removable medium, or one that does not declare medium retrieval, conforms without change — but the second documents that its medium is not a retrieval path, as `AES-MCI-008` already requires of any other means.
- The manifest specification is owed before a Module claims Released conformance to `AES-MCI-011`. Until then a Module may build against the content fixed here.
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) gains manifest and removal rules; the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) gains import rules beside its retrieval rules; the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) is expected to require that removal of a recording medium is detectable. These companion changes are made in their own releases.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** the removable medium as a declared Platform retrieval path; the content of the medium manifest; consistency under removal and power loss; the foreign-medium rule; the host's import obligations and the recorded retrieval path.

**Open — Platform decisions, taken with the evidence they need:**

- **The manifest specification**: file system, manifest encoding and location, object layout, the schema version rule. Decided with the first Module.
- **A signed manifest**, where origin must be proven.
- **Exchange of the medium during a run**: whether a Module may continue recording onto a newly inserted medium without ending the run, and how the segment and the two manifests then relate. Today removal while `RUNNING` is a storage fault with whatever recovery the Module declares.
- **Throughput** of retrieval over MCI remains without a required figure, as EDR-010 left it.

**Open — product decisions, recorded with each product:** how a product closes objects so that a removal loses a bounded amount; whether it offers a means to prepare the medium for removal and how it indicates that removal is safe; the media it supports.

## Affected Requirements / Documents

- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-011` (new); `AES-MCI-003` (declared function added).
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Medium retrieval*, *Medium manifest* (new).
- EDR-010 — the removable-medium consequence and the *Throughput* item annotated.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- Firmware, Software and Hardware guides — follow-up in their own releases.

## Future Review Criteria

Revisit if: the first Module cannot keep the manifest consistent under removal without a cost in acquisition timing; a published file system cannot hold the objects a product writes; a deployment needs the medium exchanged without ending the run; a dataset's origin is challenged and the recorded path is not enough; or a binding makes retrieval fast enough that no product ships a removable medium.
