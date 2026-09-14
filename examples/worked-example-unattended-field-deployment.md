# Worked Example: Unattended Field Deployment

**Document ID:** AES-EXAMPLE-AUTONOMOUS
**Status:** Informative
**Depends On:** [Interfaces and Versioning](../docs/05-interfaces-and-versioning.md), [Architecture](../docs/03-architecture.md), [EDR-009](../docs/edr/EDR-009-autonomous-module-operation-and-recovery.md)

This example walks one Module through an unattended deployment under [AES-MCI-006](../docs/05-interfaces-and-versioning.md#aes-mci-006-autonomous-continuation-and-deployment-policy) and [AES-MCI-007](../docs/05-interfaces-and-versioning.md#aes-mci-007-recovery-after-reset-and-run-segment-provenance): prepared over a local cable, left alone for three weeks, hit by a power loss, run out of storage, and read out afterwards. It creates no obligations. The Module is a Plant Electrophysiology Module; every capability, behavior, key and value shown is **illustrative** — which behaviors APEM actually supports, and which it ships selected, are product decisions that no AES document takes ([EDR-009](../docs/edr/EDR-009-autonomous-module-operation-and-recovery.md), open items).

## The bench

```text
AURIORA Studio ──── USB (direct local MCI) ──── APEM ──── 8 electrode inputs
                                                  └─────── Environmental Unit (UIF-MI2C-8)
```

No Module Hub. No AEL: nothing needs to react to anything else. No network. The host is a laptop that will leave with the researcher.

## 1. Discovery and capabilities

```text
identity      APEM  serial 0x2A41  rev B  fw 1.4.0  MCI 0.1 over direct-local
capabilities  sessions yes   assets yes   event_log yes   firmware_update yes
              ael_in no      ael_out no                       (this build has no AEL ports fitted)
              autonomous_continuation yes
                host_loss:           continue | stop
                recovery_after_reset: none | resume
                storage_exhaustion:  stop | overwrite_oldest
                max_consecutive_recoveries 3
              storage  total 61.2 GB  free 60.9 GB  health ok
```

The host learned all of that by asking ([AES-MCI-003](../docs/05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery)). Had the same firmware been built without persistent deployment state, `recovery_after_reset` would read `none` only and the deployment below would have to be planned differently — the host would find that out here, not in the field.

## 2. Session and deployment policy are two objects

The Session says what the experiment is:

```text
session  FIELD-21D   hash 3c9e…
  acquire 8 channels @ 200 S/s, 24-bit, continuous
  environmental Unit: sample every 60 s
  duration 21 d from start
  detector A: threshold, refractory 20 s   (records markers locally; nothing to send them to)
```

The deployment policy says how it is operated *here*:

```text
policy   host_loss = continue
         recovery_after_reset = resume
         storage_exhaustion = stop
```

The same `FIELD-21D` on a laboratory bench, with a host attached and a technician nearby, might be deployed with `recovery_after_reset = none`. The Session hash would be identical; the science is the same, the operation is not. That is the point of keeping them apart.

## 3. Validation before anything is written

The host checks what it is about to ask against what the Module declared:

```text
requested host_loss = continue           declared: yes
requested recovery = resume              declared: yes
requested storage_exhaustion = stop      declared: yes
storage: 8 ch × 3 B × 200 S/s × 21 d ≈ 8.7 GB + environmental + logs   free 60.9 GB   ok
environmental Unit: discovered, UIF-MI2C-8 0.1, API 1.2, UIF_READY high   ok
```

Had the host requested `recovery_after_reset = restart`, the Module would have refused with *invalid deployment policy*, naming the behavior, and nothing would have been substituted. A storage estimate is possible here because this Module exposes free space and the Session's rate is known; a Module that exposes less makes a smaller promise, and the host says so.

## 4. Transfer, configure, read back, arm, start

```text
transfer  FIELD-21D            → staged, verified 3c9e…, committed
write     configuration        → hash 7a10…
write     deployment policy    → accepted
read back configuration 7a10…  session FIELD-21D 3c9e…  policy continue / resume / stop   match
arm                            → ARMED   (configuration valid, Session verified, Unit ready, no fault)
start_local                    → RUNNING   run R-0917-01   segment 0   local t=0   sample 0
```

The host writes the deployment record: Module identity, firmware, configuration and Session hashes, the policy exactly as read back, the run identity, and the Module's persistent-deployment-state identity. Then the researcher unplugs the cable and drives home.

## 5. The host is gone

Nothing happens. Host loss under *continue* is not an event the Session notices: the Module keeps acquiring on its own clock, the environmental Unit is sampled every minute, detector markers are stamped into the local timeline, and the persistent deployment state is checkpointed every ten minutes with the current local time and sample index. The Module is in `RUNNING`, exactly as it was when the cable was pulled.

## 6. Day 9: power loss

A supply fault drops the enclosure's power for about three minutes.

```text
boot      reset cause: BROWNOUT → POWER_ON
          outputs safe; lifecycle IDLE
recovery  persistent deployment state: present, schema 1, CRC ok
          policy: recovery_after_reset = resume            → recovery is authorized in principle
          configuration 7a10… present, hash matches
          session FIELD-21D 3c9e… present, hash matches
          environmental Unit: rediscovered, same serial, UIF_READY high
          storage: mounted, journal replayed, last committed block at sample 155 519 800
          consecutive recoveries: 0 → 1  (bound 3)
          arming checks: pass
          IDLE → CONFIGURED → ARMED → RUNNING   reason: RECOVERY
segment   run R-0917-01   segment 0 ended   last persisted t = 8d 23:58:40.000  sample 155 519 800
                          segment 1 began   t' = 0 (new local epoch)              sample 0
                          gap: unknown; RTC says ≈ 3 min 12 s, RTC status: battery-backed, uncorrected
                          cause: BROWNOUT → POWER_ON   recovery: automatic, policy resume
```

Two things did not happen. The Module did not carry on from sample 155 519 800 as if nothing occurred: the data before and after the boundary are two segments with a gap of stated uncertainty. And the Module did not need anyone: the authority for restarting acquisition was the policy the host wrote on day 0, verified against a state record that proved intact.

## 7. What a refusal would have looked like

Suppose the environmental Unit's cable had come loose in the same fault:

```text
recovery  … environmental Unit: not discovered
          Session requires it → prerequisite missing
          → remain IDLE; refusal recorded: RECOVERY_REFUSED (MISSING_PREREQUISITE: unit ENV)
          persistent deployment state and stored data preserved
```

The Module waits. It does not acquire seven channels of electrophysiology without the Unit the Session asked for, and it does not decide that "mostly" is good enough. When the host returns it reads `IDLE`, the refusal and its reason, and the person decides. A recurring fault would have looked different again: after the third consecutive recovery the counter reaches its bound and the Module stays `IDLE` with `RECOVERY_REFUSED (RECOVERY_BOUND_REACHED)` rather than minting a new segment every few minutes.

## 8. Day 19: storage exhausted

A firmware estimate was optimistic about the environmental logs; the storage fills two days early.

```text
event     STORAGE_EXHAUSTED   t' = 9d 21:14:03   sample 170 108 600   policy: stop
          recording ends; stored data preserved; persistent state updated
          RUNNING → COMPLETE   reason: STORAGE_EXHAUSTED (policy stop)
```

Under *overwrite oldest* the Module would instead have kept recording and set a persistent indicator with the extent overwritten; the researcher chose *stop* on day 0 because the first days mattered more than the last. Either way the event is in the log, and the data does not pretend otherwise.

## 9. Day 21: the host returns

The researcher plugs the laptop back in. The host does not remember anything about this Module that it trusts more than what it now reads:

```text
identify        APEM 0x2A41 rev B fw 1.4.0            same Module as the deployment record
query_state     COMPLETE   last transition: STORAGE_EXHAUSTED (policy stop)
                configuration 7a10…  session FIELD-21D 3c9e…  policy continue / resume / stop   match
recovery        occurred: yes   count 1   run R-0917-01   segments 0, 1
                boundary: BROWNOUT → POWER_ON, automatic, policy resume, day 9
storage         free 0.0 GB   overwritten: none   health ok
uptime          11d 14:02   (went backwards relative to the host's last view → a restart, consistent with the boundary)
event log       start, checkpoints, 340 detector markers, 1 reset, 1 recovery, STORAGE_EXHAUSTED, COMPLETE
```

The host re-arms nothing and restarts nothing. It reconciles the deployment record: the run now has two segments and an early completion with a recorded cause, and the record says whether that was expected (it was not) and what happened (the log says). Retrieving the ~8 GB of data is the bulk path, which is a separate concern and not MCI.

## 10. The deployment record, afterwards

```text
deployment D-0917-APEM-field
module     APEM 0x2A41 rev B fw 1.4.0   MCI 0.1 direct-local   persistent-state schema 1
session    FIELD-21D 3c9e…   configuration 7a10…
policy     host_loss continue · recovery resume · storage stop        (as read back, day 0 and day 21)
run        R-0917-01
  segment 0   day 0 → day 8 23:58:40   samples 0 … 155 519 800
  boundary    BROWNOUT → POWER_ON · automatic recovery, policy resume · gap ≈ 3 min 12 s (RTC, uncorrected)
  segment 1   day 9 → day 19 21:14:03  samples 0 … 170 108 600
outcome    COMPLETE by STORAGE_EXHAUSTED (policy stop), 2 days early · no data overwritten
events     1 reset · 1 recovery · 340 markers · 0 faults
```

A reader with this record, the two segments and the event log knows exactly what was recorded, where the recording is discontinuous and why, and which decisions were the researcher's and which were the Module's acting on them — which is the point.

## What this example did not need

No Module Hub, no AEL, no route table, no network, no cloud, and no host during the twenty days that mattered. The same Module, the same Session and the same firmware would have joined the bench of the [multimodal example](./worked-example-multimodal-ael-experiment.md) unchanged; only the deployment policy would differ, because only the way it is operated does.
