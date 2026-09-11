# Worked Example: Module Synchronization

**Document ID:** AES-EXAMPLE-SYNC
**Status:** Informative
**Depends On:** [Interfaces and Versioning](../docs/05-interfaces-and-versioning.md), [SYNC specification](../docs/interfaces/sync.md)

This example shows the Module Synchronization Interface ([Interfaces and Versioning §4](../docs/05-interfaces-and-versioning.md#4-module-synchronization-interface)) in its two intended uses — as a trigger and as a marker — on a hypothetical bench of two Audio Modules and one Plant Electrophysiology Module. It creates no obligations. Configuration keys and event names are illustrative; each Module documents its own.

## The bench

```text
                              ┌──► AAM #1  SYNC IN
Host ──(control)──► AAM #1    │
                    SYNC OUT ─┴──► SYNC HUB ──┬──► AAM #2   SYNC IN
                                              └──► APEM     SYNC IN
```

The host configures every Module over its Host Interface before anything is armed. SYNC carries nothing but the edge; every meaning below is in the configuration.

## Trigger use: one edge, two stimulus Modules

```text
AAM #1:  protocol = 3        sync_in_action = NONE            sync_out_source = PROTOCOL_START
AAM #2:  protocol = 7        sync_in_action = START_PROTOCOL  sync_delay = 500 ms
         retrigger_policy = IGNORE_WHILE_RUNNING   post_complete = ONE_SHOT
```

The host arms AAM #2, then starts AAM #1's protocol by command. Nothing else is commanded.

```text
AAM #1  first stimulus sample leaves the converter
          ↓
AAM #1  SYNC OUT pulse           (source = PROTOCOL_START — the actual onset, not the command)
          ↓  Hub: regenerate, documented delay
AAM #2  SYNC IN rising edge      state = ARMED → accepted
          ↓  configured delay 500 ms, timed from the captured edge
AAM #2  Protocol #7 starts
          ↓
AAM #2  COMPLETE → IDLE          (ONE_SHOT: a second edge now does nothing but get logged)
```

Three AAMs with delays of 0, 500 and 1000 ms would start staggered from the same edge. The stagger is configuration on each receiver; the wire carried one identical pulse to all three.

## Marker use: an acquisition Module that never stops

APEM records continuously and is not a stimulus device. It binds the same edge to a different action:

```text
APEM:    sync_in_action = INSERT_MARKER     (APEM is armed for this action whenever it is recording)
```

```text
ADC ADC ADC ADC │SYNC│ ADC ADC ADC ADC ADC │SYNC│ ADC ADC
```

APEM's log needs only the sample index of each edge:

```text
sample 1824401  SYNC_RX  count=17  action=INSERT_MARKER
sample 2978233  SYNC_RX  count=18  action=INSERT_MARKER
```

AAM #1's log says what each of those edges was:

```text
12.000021  SYNC_TX  count=17  source=PROTOCOL_START  run=12
19.240530  SYNC_TX  count=18  source=PROTOCOL_START  run=13
```

Joining the two logs on the counter and on order gives the stimulus onset in the electrophysiology timeline to the precision of the capture, independent of host latency. Neither pulse carried a run number; both logs did.

## A retrigger arrives mid-run

AAM #2 is `RUNNING` when a second edge arrives:

```text
17.423812  SYNC_RX       count=35  state=RUNNING
17.423812  SYNC_IGNORED  count=35  reason=RUNNING
```

Nothing restarts, stops or queues. The event is visible, its reason is stated, and the experiment record shows that an unexpected trigger occurred. Had the Module been configured with an explicit `RESTART` retrigger policy, the log would show that policy being applied; the default is the safe one.

## Counting finds the lost pulse

After a session of 100 protocol starts:

```text
AAM #1   SYNC_TX count = 100
AAM #2   SYNC_RX count = 100
APEM     SYNC_RX count = 99
```

One edge did not reach APEM. The counters are local — nothing on the wire numbered the pulses — but comparing them across the sender and every receiver localizes the loss to one path (the Hub-to-APEM link) before anyone opens the data. Which run is missing follows from the timestamps.

## What this example did not do

- It did not put a run number, a protocol number or a "start versus marker" flag on the wire. A receiver seeing only the pulses could not tell the trigger use from the marker use — and did not need to.
- It did not let a Module react to an edge it was not configured and, where the action requires it, armed for.
- It did not chain the Modules by forwarding SYNC IN to SYNC OUT; AAM #1's output marks its own onset, and the Hub does the fan-out.
