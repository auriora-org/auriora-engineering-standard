# EDR-009: Autonomous Module Operation and Recovery

## Status

Accepted (2026-09-17)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance). Independent review SHOULD be sought before any Released Module relies on autonomous recovery.*

This record adds to [EDR-007](./EDR-007-module-control-interface-and-module-hub.md) (MCI) and [EDR-008](./EDR-008-auriora-event-link.md) (AEL) and supersedes nothing in either. Its statement that the bulk-data path lies outside MCI is superseded by [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md) (2026-09-18), which places it inside MCI as stored object retrieval; the body below is otherwise unchanged.

## Context

AES already contains most of the pieces of a Module that works alone. A Module is a standalone product ([Terminology §2](../02-terminology.md#module)); the Module Hub is optional infrastructure and never a prerequisite for commissioning, recovery or direct Module-to-Module events ([AES-HUB-001](../03-architecture.md#aes-hub-001-module-hub-scope)); the direct local MCI transport exists for "standalone operation" among other things ([Interfaces and Versioning §5.1](../05-interfaces-and-versioning.md#51-transport-bindings)); MCI prepares and observes state while AEL carries the deterministic events, so the host is not in the timing path once Modules are armed; and reconnection establishes identity and capabilities and nothing more — it never re-arms or restarts.

What AES did *not* say is what happens next. The phrase "a Module that declares the capability may continue a Session while the host is away" appeared only in non-normative guidance and in a worked example, and the capability it refers to was absent from the minimum capability list of [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery). Nothing defined what a Module owes when the host is gone, what it does when the power fails, what it does when its storage fills, how a run that spans a reset is represented, or what a host is allowed to conclude when it reconnects weeks later. The Firmware Style Guide's rule that "a reset returns the Module to `IDLE` — it never rejoins an active experiment as `ARMED` because it remembers having been armed" was the only text on the subject, and read literally it forbids the one behavior a long-term field deployment needs: recovering from a power loss without a person present.

The motivating case is a Plant Electrophysiology Module prepared over a local cable in AURIORA Studio and then left recording for days or weeks with no host, no Hub and no network — in a greenhouse, a growth chamber or the field. The same case arrives in the laboratory as "the computer should not have to stay attached". It is a first-class use of the Platform, and it must be a clean extension of the existing architecture rather than a product-specific workaround.

The decision is platform-wide under [AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger): it changes the semantics of a Platform interface (MCI) and the lifecycle model every Module implements, it is safety-relevant — an autonomous restart of a stimulus Module is a hazard — and it creates obligations across the firmware, software and hardware guides.

## Alternatives Considered

### Where autonomy comes from

| Alternative | Assessment |
|---|---|
| **Infer it from the product** — acquisition Modules continue, stimulus Modules stop, APEM recovers after power loss | Rejected. It is the type-table pattern [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery) exists to prevent, it fails silently when a Module is present but lacks the behavior assumed of it, and it makes every firmware revision a potential change of host behavior. |
| **Make it mandatory** — every Module continues without a host and recovers after reset | Rejected. A stimulus Module whose safety policy forbids unattended restart would be non-conformant, and Modules that never leave a bench would carry persistent-state machinery they do not need. |
| **A declared capability, *autonomous continuation*, in the minimum capability list, with the supported behaviors declared beside it** | **Chosen.** The host plans from declared facts; a Module without the capability is operated unchanged; a Module with it says exactly which behaviors it supports. This also repairs the inconsistency between the guidance and `AES-MCI-003`. |

### Host loss and power loss

| Alternative | Assessment |
|---|---|
| **One "autonomous" switch covering both** | Rejected. Continuing while the host is away needs only volatile state and the ARM boundary; coming back after a power loss needs persistent state, validation and provenance. A Module can legitimately support the first and not the second, and a deployer may legitimately want the first without the second. |
| **Two independently declared and independently configured behaviors: host-loss behavior (*continue* / *stop*) and recovery behavior after reset (*none* / *resume* / *restart*, plus declared Module-specific ones)** | **Chosen.** Each answers a different question, each is supported or not on its own, and each is chosen per deployment from the declared set. |
| **Detect host loss from transport link state** | Rejected as a Platform rule. Link state is binding-specific and a USB suspend is not a lost host. Host loss is defined by the Module or its binding — a supervision interval without MCI activity, or a transport that reports loss — and is never a property of the Session. |

### Behavior after a reset

| Alternative | Assessment |
|---|---|
| **Never resume: a reset always ends the deployment** (the literal reading of the previous firmware-guide rule) | Rejected as the only option. It makes every brownout in a field enclosure a lost deployment, which is the case the Platform is meant to serve. It remains the behavior of every Module that declares no recovery, and *none* remains the only recovery behavior every Module supports. |
| **Always resume what was running** | Rejected. A Module that carries on after a brownout has decided alone that its Units are attached, its storage is sound and its outputs are safe, and nothing recorded the decision. It is also the pattern that turns a recurring fault into a boot loop. |
| **Restore the remembered lifecycle state** — boot directly into `ARMED` or `RUNNING` from non-volatile memory | Rejected. `ARMED` means "every precondition has been checked now"; a remembered `ARMED` is a promise made about a different moment. Restoring `RUNNING` skips the check entirely. |
| **Boot to `IDLE`, then run a recovery procedure whose authority is a persistent deployment policy the host set before it left, whose gate is full validation of persistent state and prerequisites, and whose path is the ordinary lifecycle with the arming checks repeated** | **Chosen.** The outcome an "always resume" Module reaches by assumption is reached here through verifiable facts, and a failed check produces a Module that waits in `IDLE` with the reason recorded — the state a person can reason about from a distance. |
| **A new lifecycle state such as `RECOVERING`** | Rejected. Recovery is a boot procedure that ends in an ordinary state; its steps are reported as transitions with recovery as their reason. Adding a state adds nothing a host can act on that the transition reasons do not already say. |

### Provenance across a reset

| Alternative | Assessment |
|---|---|
| **Hide it** — concatenate the data and let the sample index continue | Rejected. The gap has unknown length and the clock may have moved; every interval measured across the boundary is wrong without looking so. |
| **A new run for every reset** | Rejected as the only option. Under *resume* the deployment, the Session and the run are the same; only physical continuity broke. Forcing a new run identity discards that fact. |
| **Run segments: a run begins with segment 0, each recovery opens a new segment (under *resume*) or a new run (under *restart*), and the boundary carries reset cause, last persisted and first new local time and sample index, time-reference status and the authorizing policy** | **Chosen.** The record says what happened and where; the reader decides whether the run is still one experiment. |

### Storage exhaustion

| Alternative | Assessment |
|---|---|
| **Leave it to the Module's documentation** | Rejected. Whether the beginning of a recording is gone or the end is missing is invisible in the data and decisive for its interpretation; it has to be a declared, chosen, read-back and logged behavior. |
| **Mandate one behavior** | Rejected. A logger may want a ring buffer; an experiment may need every sample from `T0`. |
| **Two named behaviors, *stop* and *overwrite oldest*, declared and chosen like the others; overwrite never a default; exhaustion always logged; overwrite and its extent always readable** | **Chosen.** |

### Where the policy lives

| Alternative | Assessment |
|---|---|
| **In the Session** | Rejected. The same Session would then behave differently on two benches with the same protocol, and the Session stops being a reproducible scientific object. |
| **In Module configuration** | Rejected. Configuration is about the device — gains, Unit assignments — and outlives a deployment; the policy is about one installation of one Session. |
| **A separate *deployment policy*, held by the Module beside the Session, configured only from declared behaviors, read back, and recorded in the host's deployment record** | **Chosen.** Three objects with three owners: configuration says what the device is, the Session says what it executes, the policy says how it is operated here. |

### Fault recovery during a run

| Alternative | Assessment |
|---|---|
| **A Platform-wide table of fault responses** | Rejected. What is recoverable for an environmental logger is fatal for a stimulus Module; the Module owns its safety policy ([AES-MOD-004](../03-architecture.md#aes-mod-004-safety-policy-ownership)). |
| **A Platform rule about the *shape* of fault recovery: classes stated as recoverable / degraded / fatal for the run, each recovery bounded, every attempt and degradation logged** | **Chosen.** |

### The Module Hub

| Alternative | Assessment |
|---|---|
| **Give the AEL router a persistent route policy so a Hub-connected deployment survives a Hub power loss** | Not decided here. [AES-AEL-005](../05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior) says a router never reinstates an active route table on its own, and the reason still holds: a router holds numbers whose meaning it cannot validate, whereas a Module holds the deployment's content, prerequisites and safety policy. The consequence — a Hub-dependent unattended deployment survives a Module reset but not a Hub power loss without a host — is stated in [Architecture §7](../03-architecture.md#7-module-hub) and left as an explicit open question. |

## Decision

1. **Autonomous continuation** is a declared Module capability in the minimum capability list of [AES-MCI-003](../05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery): the Module continues an `ARMED` or `RUNNING` Session to its defined end, and reaches `COMPLETE`, without a connected host or Module Hub, and preserves the outcome for later readout. A Module that does not declare it is operated unchanged, and a host relies on nothing autonomous from it.
2. A Module that declares the capability holds a **deployment policy**, separate from its configuration and from the Session, configured over MCI only from the behaviors the Module declares, refused with a defined error otherwise, and readable back. Its named behaviors are: host loss — *continue*, *stop*; recovery after reset — *none*, *resume*, *restart*; storage exhaustion — *stop*, *overwrite oldest*. A Module MAY declare further behaviors and SHALL have no undeclared one. How host loss is detected is defined by the Module or its transport binding, never by the Session. ([AES-MCI-006](../05-interfaces-and-versioning.md#aes-mci-006-autonomous-continuation-and-deployment-policy))
3. Under *continue*, loss of the host, Hub or transport and any later reconnection change nothing about lifecycle state, execution, configuration, Session or bindings; the Module reaches `COMPLETE` without the host and preserves completion or stop status, local time and sample index, fault status, event log and stored-data integrity state for later readout. **Reconnection never re-arms, resumes or restarts anything.**
4. After **any reset** a Module starts in `IDLE` with safe outputs and never restores `ARMED` or `RUNNING` as a remembered state. **Autonomous recovery** — re-entering execution without a host — happens only when a present, integrity- and version-valid **persistent deployment state** records a recovery behavior other than *none*; the recorded configuration, Session, Assets and bindings are present with matching integrity values; the Session's Units, storage and other prerequisites are available; the consecutive-recovery count is within the Module's declared bound; and the arming checks of [AES-MCI-004](../05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary) pass. Recovery proceeds through the ordinary lifecycle transitions with recovery as the reported reason. If anything fails, the Module stays non-running, records the refusal and its reason, and keeps its persistent state and data for diagnosis. Corrupt, incompatible or absent persistent state never authorizes recovery. ([AES-MCI-007](../05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance))
5. Persistent deployment state carries at minimum the deployment identity; the identities and integrity values of configuration, Session, Assets and bindings; the policy; run and segment identity; the recovery count; the last lifecycle state and transition reason; and its own schema version and integrity value. Its format is an implementation detail; its update is atomic with respect to power loss.
6. Every recovery opens a new **run segment**: under *resume* a new segment of the same run, under *restart* segment 0 of a new run of the same Session. Each boundary records the reset cause where hardware exposes it (at minimum power-on / brownout / watchdog / software / external / unknown), the ended segment's last persisted local time and sample index, the new segment's first, the time-reference status across the boundary, and whether and under which policy recovery was automatic. Data across a boundary is never presented as one continuous acquisition.
7. Storage exhaustion is always logged; destructive overwrite is never a default or undeclared behavior; a Module that overwrote data makes the fact and its extent readable. Fault recovery during a run is permitted where the Module documents which fault classes are recoverable, degraded-capable or fatal for the run, bounds each recovery and logs every attempt and degradation.
8. Recovery occurrence, current run and segment identity, reset cause and any data loss or overwrite are readable through MCI. The existing AEL router rule — no self-reinstated route table after reset — is **unchanged**.
9. The supporting terms *autonomous continuation*, *deployment policy*, *persistent deployment state* and *run segment* are added; *Session* and *Module Lifecycle State* are extended. Frozen core vocabulary is unchanged.
10. Product-level defaults — which behaviors a given Module supports and which it ships selected — are product decisions recorded with the product, never Platform defaults. No default is chosen here for any Module, including APEM.

## Rationale

The decision extends the existing architecture along its own grain. The ARM boundary already separates preparation from deterministic execution and already keeps the host out of the timing path; autonomous continuation only names the promise that follows from it, and puts it where a host can read it. Reconnection already established identity and nothing more; the record keeps that and identifies the one legitimate way execution is re-entered without a host — a policy the host set *before* it left — so that the host's *return* is never mistaken for authority.

Recovery is made a validated boot procedure rather than a remembered state because that is the only form in which it is checkable. Every condition on the list is one a Module can verify at boot, and every failure of one leaves the Module in the state that is safest and most legible: `IDLE`, waiting, with the reason written down. The bound on consecutive recoveries turns a recurring fault into a recorded refusal rather than a power-cycling loop. Nothing here weakens [AES-CTRL-002](../03-architecture.md#aes-ctrl-002-deterministic-startup): outputs stay safe until the checks pass, exactly as they must on a bench.

Run segments are the reproducibility half of the same decision. The Platform records events so that a lost AEL frame can be located after the fact ([AES-AEL-004](../05-interfaces-and-versioning.md#aes-ael-004-deterministic-timing-and-observability)); a reset in the middle of a recording is a larger discontinuity than a lost frame and deserves at least the same visibility. Making the boundary explicit — with its cause, its last and first instants and the status of the clock — is what lets a reader decide what the data across it means, instead of the firmware deciding for them by making it look continuous.

Keeping the deployment policy out of the Session keeps the Session reproducible and keeps the operational choice where the deployer makes it. Keeping product defaults out of AES keeps the Platform capability-driven: APEM will very likely declare *continue* and some recovery behavior, and a stimulus Module may legitimately declare *none*; the host learns which by asking, which is the same rule that governs everything else it learns about a Module.

AES stays lean. The requirements fix the contract — capability, policy, invariants, persistent-state content, segment provenance, readback — and leave the firmware procedure, the host workflow and the hardware measures to the companion guides, where the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) §14.4, the [Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) §3.6 and the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) §14.1 carry them.

## Consequences

- AES gains `AES-MCI-006` and `AES-MCI-007` in [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface); `AES-MCI-003` names autonomous continuation and its declared behaviors in the minimum capability list; [Architecture §3](../03-architecture.md#3-module-design) states the principle and [Architecture §7](../03-architecture.md#7-module-hub) states the Hub consequence; four supporting terms are added and two extended; an informative [worked example](../../examples/worked-example-unattended-field-deployment.md) shows one unattended deployment end to end.
- **The change is additive.** A Module that declares no autonomous continuation, no recovery behavior and no local storage conforms without change; the only new obligation on every Module is the reset rule already implied by the ARM boundary and stated by the firmware guide — start in `IDLE`, restore nothing remembered — which no existing Module violates. No AEL, `MCL`, Unit Interface or EEPROM contract changes. MCI has no version number yet, so none is incremented; the first binding specification carries these semantics as part of the MCI version it declares.
- **Firmware** that declares recovery needs persistent deployment state with atomic update, a recovery procedure in its boot path, segment bookkeeping, a bounded recovery counter, reset-cause capture and explicit storage-exhaustion handling — the Firmware Style Guide §14.4. Its existing "reset returns the Module to `IDLE`" rule is clarified, not reversed: `IDLE` is where every reset begins; recovery is what may follow, on explicit authority.
- **Host software** gains a deployment preparation step for unattended Modules — verify capability and behaviors, configure only from the declared set, validate storage feasibility where inspectable, persist the policy in the deployment record, apply, read back, arm last — and a reconnection reading that includes recovery occurrence, segments, reset causes and overwrite indicators — the Software Style Guide §3.6. Autonomous behavior is shown, never hidden in defaults.
- **Hardware** that advertises unattended operation owes supervision, reset-cause capture, power-fail-safe storage, timekeeping and energy margin — the Hardware Design Guide §14.1, as implementation guidance.
- **A Hub-dependent unattended deployment does not survive a Hub power loss without a host.** This is a consequence of the unchanged `AES-AEL-005`, now stated in Architecture §7 rather than discovered in the field.
- A Module that enters a *stop* path on host loss, or that refuses recovery, may be found `IDLE` or `CONFIGURED` with its run over; the host reads that and the recorded reason, and the person decides. Nothing in the Platform restarts it for them.
- The Communication & Timing Unit, or any other time reference, is optional: a GNSS-disciplined or RTC-backed clock improves what a segment boundary can say about time, and its absence is recorded as time-reference status, not papered over. Bulk retrieval of stored data is not defined here and remains the separate concern EDR-008 already names.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled by this record:** capability-driven autonomy; the three policy axes and their named behaviors; the no-remembered-state reset rule; recovery as a validated boot procedure with a bounded retry count; the minimum content and atomic update of persistent deployment state; run segments and the content of a segment boundary record; storage exhaustion always logged and overwrite never default; the shape of fault recovery; the Session / configuration / deployment-policy ownership split; the unchanged router rule.

**Open — product decisions, taken with each product and recorded there, not in AES:**

- **APEM** has no product-level specification yet; one is needed before it can declare anything. The decisions it must take: which host-loss behaviors it supports and ships selected (*continue* is the expected candidate); which recovery behavior after power loss (*none*, *resume* as a new segment, or *restart*); which storage-exhaustion behavior (*stop* or *overwrite oldest*) and whether both are offered; its local storage architecture and capacity; the persistence technology and checkpoint cadence of its deployment state; the precision of its reset-cause reporting; its bound on consecutive recoveries; which Unit faults are recoverable, degraded-capable or fatal for a run.
- The same set for every other Module that will declare autonomous continuation. A stimulus Module decides whether any recovery behavior other than *none* is compatible with its safety policy.

**Open — Platform decisions, taken later with the evidence they need:**

- **Host-loss detection** per MCI transport binding: the supervision-interval model, its default and range, and what a binding that can report link loss contributes. Decided with each binding specification.
- **Persistent route policy for the AEL router** — whether a Module Hub may ever reinstate a committed route table under an explicitly configured policy so that a Hub-connected unattended deployment survives a Hub power loss. The reasons behind `AES-AEL-005` weigh against it; it is recorded here so that it is decided rather than assumed. *Decided in [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md): a host-set, persistently held route recovery policy, default *none*.*
- **Time across segments**: how a segment boundary's time uncertainty is expressed once the Platform has a shared clock-alignment mechanism (the open concern of EDR-005 and EDR-008). Until then the boundary carries local time, sample index and time-reference status.
- **Retrieval of locally stored data** — the bulk-data path — remains outside MCI and AEL and is not designed here. *Designed in [EDR-010](./EDR-010-hub-host-facing-interface-and-stored-object-retrieval.md) as an optional MCI function, `AES-MCI-008`.*
- Whether the readback of recovery occurrence, segments and overwrite indicators belongs to the MCI core or to an optional MCI function is fixed with the first binding, together with the MCI version that carries it.

## Affected Requirements / Documents

- [Interfaces and Versioning §5](../05-interfaces-and-versioning.md#5-module-control-interface) — `AES-MCI-006`, `AES-MCI-007` (new); `AES-MCI-003` (minimum capability list extended); §4.2 and §5.2 guidance updated.
- [Architecture §3 and §7](../03-architecture.md#3-module-design) — unattended autonomous operation principle; Hub consequence.
- [Terminology §3](../02-terminology.md#3-supporting-terms) — *autonomous continuation*, *deployment policy*, *persistent deployment state*, *run segment* (new); *Session*, *Module Lifecycle State* (extended).
- [Worked Example: Unattended Field Deployment](../../examples/worked-example-unattended-field-deployment.md) — new, informative.
- [Document Index](../document-index.md), `STANDARD.md` — indexing.
- Firmware Style Guide §14.2 (clarified) and §14.4 (new); Software Style Guide §3.6 (extended); Hardware Design Guide §14.1 (new).

## Future Review Criteria

Revisit if: a Module class needs a recovery behavior that cannot be expressed as *resume* or *restart* plus a declared Module-specific behavior; field experience shows that the bound on consecutive recoveries or the segment-boundary record is insufficient to diagnose what happened; a shared clock-alignment mechanism changes what a segment boundary should carry; the first MCI binding finds that host-loss detection cannot be kept out of the Session; or an installation genuinely needs a Hub to survive power loss unattended, which would reopen the router's persistent-route question.
