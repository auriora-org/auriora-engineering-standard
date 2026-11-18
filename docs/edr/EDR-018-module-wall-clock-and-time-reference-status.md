# EDR-018: Module Wall Clock and Time-Reference Status

## Status

Accepted (2026-11-18)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module relies on this architecture.*

This record adds to [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) (MCI) and [EDR-009](./EDR-009-autonomous-module-operation-and-recovery.md) (autonomous operation). It takes the absolute-time half of the item [EDR-008](./EDR-008-auriora-event-link.md), EDR-009 and [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md) carried as *cross-Module clock alignment and absolute time*, and leaves the alignment half open. It supersedes nothing.

## Context

The first autonomous recording Module carries a battery-backed real-time clock and its design notes assume that "the host sets the clock on connect". Nothing in AES supports that sentence. MCI has no operation that sets a clock and no capability that declares one; no requirement says whose task a Module's time of day is; and the one place AES mentions a time reference — the segment boundary of [AES-MCI-007](../05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance) — requires its *status* without saying what the status contains.

AES uses **local time** throughout for the Module's own timebase: the clock against which samples, AEL frames and lifecycle transitions are stamped. Whether that timebase is also a time of day was never stated, and three records listed the question as open together with the alignment of clocks between Modules.

The two halves need different evidence. Aligning clocks between Modules to a known uncertainty needs a mechanism — a shared reference, a disciplining method, a figure — and measurements from real Modules. Giving one Module a time of day needs only a decision about who may set it, when, and what is recorded, and a field Module cannot be deployed without it: a recording whose start is "day 0 of an unset clock" cannot be placed against the weather, the irrigation schedule or another instrument.

The assumption as written also conflicts with rules AES already has. A host that sets a clock *on connect* changes a Module as a side effect of discovery, which [Interfaces and Versioning §5.2](../05-interfaces-and-versioning.md#52-guidance-non-normative) rules out, and a host that reconnects to a Module that is `RUNNING` unattended would move the time base of the recording it came to collect.

## Alternatives Considered

### Who sets a Module's time of day

| Alternative | Assessment |
|---|---|
| **Nobody; the Platform has no time of day**, and a recording is placed in time by the host at deployment and retrieval | Rejected. The host is absent for most of an unattended run; the start instant it noted is one point, and every segment boundary after a reset would have nothing to be placed by. |
| **Each Module product defines its own clock command** | Rejected. It is the per-product control protocol MCI exists to prevent ([AES-MCI-009](../05-interfaces-and-versioning.md#aes-mci-009-mci-in-released-modules)), and host software would grow a table of which Module sets its clock how. |
| **A declared, optional MCI capability with one set operation and a required status readout** (chosen) | The same shape as every other optional MCI function: declared, refused with a defined error where absent, read back. A Module without a clock declares nothing and is unchanged. |
| **The host sets the clock automatically whenever it connects** | Rejected. Discovery and reconnection change nothing; a clock step is a change to a Module that may be running. Setting is an explicit, recorded step. |

### When the clock may move

| Alternative | Assessment |
|---|---|
| **Any time; the Module logs the step** | Rejected. A step inside a run segment makes every interval measured across it wrong unless the reader finds and applies the log entry, and a recording's begin and end time would no longer bound its samples. |
| **Never while `ARMED` or `RUNNING`, from any source; a reference obtained in those states is recorded as an observation and not applied** (chosen) | Within a run segment the sample index is the time axis and the clock is continuous by construction. An observation — reference time against local time and sample index — carries strictly more information than a step would have, and the reader applies it or not. |
| **Only in `IDLE`** | Narrower than needed. `CONFIGURED` and `COMPLETE` hold no running time base either, and requiring `IDLE` would order the deployment steps for no reason. |

### What the status says

| Alternative | Assessment |
|---|---|
| **A quality figure — an uncertainty in seconds** | Not now. A figure needs the alignment mechanism and a drift model, which is the open half of the item. |
| **Facts the Module actually holds**: whether the clock has been set since it last lost its supply, from what kind of source, when by its own clock, and whether it kept running across the last reset (chosen) | Enough for a reader to decide how far to trust a time of day, and every item is known to the Module without a model. |

## Decision

1. AES gains **`AES-MCI-010` Wall Clock and Time-Reference Status** in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#aes-mci-010-wall-clock-and-time-reference-status).
2. **Time of day is UTC.** A Module that keeps a wall clock keeps it, stores it and exchanges it as UTC; time zones and daylight saving are host presentation.
3. **Status is always readable.** A Module that stamps any record with a time of day exposes through MCI its current time and its time-reference status: whether the clock has been set since it last lost its supply, the kind of source it was last set from, the Module's own time at which that happened, and whether the clock ran through the last reset. A clock that has not been set is reported as unset; its value is never presented as a time of day.
4. **Setting is a declared, optional operation.** A Module MAY declare a settable wall clock. The operation is refused with a defined error while the Module is `ARMED` or `RUNNING`, and every set is recorded as an event carrying the clock before and after it and the source.
5. **No step inside a run.** A Module does not step its wall clock while `ARMED` or `RUNNING`, whatever the source. A time reference obtained in those states — from a Unit, from any other declared source — is recorded as an observation pairing the reference time with local time and sample index.
6. **Every segment carries its status.** The time-reference status in force when a run segment begins is recorded with the segment, segment 0 included, so that a recording's times can be read without the Module.
7. **The host sets explicitly.** A host sets a Module's clock only as a deliberate, recorded step of a deployment — never as a consequence of discovery or reconnection — and records what it set, from which reference, and the Module's clock before and after. A host does not substitute its own clock for a Module's recorded times.
8. **Not decided here:** the alignment of clocks between Modules, and with it the expression of time uncertainty across a segment boundary (EDR-009), a shared hardware time reference (the PPS-class need of [EDR-005](./EDR-005-low-bandwidth-managed-unit-interface.md)), and any disciplining of a Module's clock during a run.

## Rationale

The decision separates the question that can be answered from the one that cannot yet. A time of day on one Module is bookkeeping; alignment between Modules is metrology. Keeping them in one open item left the first Module that needs a clock with an assumption in its design notes.

Forbidding a step inside a run is what makes the rest simple. Inside a segment the sample index already orders everything and the local timebase is continuous; a time of day is then a single mapping per segment, with observations that refine it. The Module never has to decide whether a correction is small enough to apply, and the dataset never contains an interval that silently spans a jump. A long deployment with a drifting clock and a satellite time Unit is the case this is written for: the drift stays in the data, the observations sit beside it, and nothing was rewritten in the field.

The status is a list of facts rather than a figure because a figure would be invented. A reader who knows that a clock was set by a host forty days before the segment began, and ran through two brownouts on its backup cell, can apply the drift figure of the product; a reader given "± 2 s" has to trust a model nobody has measured.

The operation is optional and declared so that the capability rule holds: a host asks, and a Module without a clock is not a special case in software.

The decision is deliberately independent of how MCI is carried. A binding that brings a time service of its own — a network transport would — becomes one more declared source under item 3; it does not change who decides, when a clock may move, or what is recorded.

## Consequences

- AES gains `AES-MCI-010`; [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery) lists the settable wall clock among the declared functions; [Terminology §3](../02-terminology.md#3-supporting-terms) gains *Time-reference status*.
- **Additive normative change, released as AES `0.15.0`.** Nothing Released exists. A Module without a wall clock conforms without change; a Module that stamps time of day gains the status readout and the no-step rule.
- The [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) gains the clock rules for Module firmware; the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) gains clock setting as an explicit deployment step and its record. These companion changes are made in their own releases.
- A product whose notes assume a clock set on connect restates the assumption as a deployment step.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** UTC as the Platform's time of day; the content of the time-reference status; the settable wall clock as a declared optional MCI function with its state rule and its event; no clock step inside a run from any source; observations in place of steps; the host's obligation to set explicitly and record.

**Open — Platform decisions, taken with the evidence they need:**

- **Cross-Module clock alignment**: the mechanism, its reference and the uncertainty it achieves; whether and how a Module's clock is disciplined rather than observed; how a segment boundary's time uncertainty is expressed. The next architectural record on time.
- **Resolution and encoding** of time values and of observations, and leap-second handling: decided with the first MCI binding.
- **A hardware time reference** between Module and Unit or between Modules, which no current interface carries.

**Open — product decisions, recorded with each product:** whether a Module has a wall clock and declares it settable; its backup source and documented drift; which time sources it accepts and how often it records an observation.

## Affected Requirements / Documents

- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-010` (new); `AES-MCI-003` (declared function added).
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *Time-reference status* (new).
- EDR-008, EDR-009, EDR-013 — the absolute-time item annotated as decided here.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- Firmware Style Guide and Software Style Guide — follow-up in their own releases.

## Future Review Criteria

Revisit if: a Module class needs its clock corrected during a run because observations cannot be applied afterwards; the first binding cannot carry a time value at the resolution a product needs; the alignment record finds that the status must carry an uncertainty after all; or a transport with its own time service makes a host-set clock redundant for Modules reached through it.
