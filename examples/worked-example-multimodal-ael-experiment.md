# Worked Example: Multimodal AEL Experiment

**Document ID:** AES-EXAMPLE-AEL
**Status:** Informative
**Depends On:** [Interfaces and Versioning](../docs/05-interfaces-and-versioning.md), [Architecture](../docs/03-architecture.md), [AEL specification](../docs/interfaces/ael.md)

This example walks one closed-loop experiment through the AURIORA Event Link ([Interfaces and Versioning §4](../docs/05-interfaces-and-versioning.md#4-auriora-event-link)) on a hypothetical bench of one measurement Module, three stimulus Modules and two Module Hubs, and then shows the same frame on a Hub-free pair. It creates no obligations. Event names, action names, configuration keys, identifiers and hash values are illustrative; each Module documents its own actions and sources, and the host allocates identifiers per deployment.

## The bench

```text
                     HOST ──(host-facing transport)──┬───────────────────────┐
                                                     │                       │
                                              ┌──────┴──────┐         ┌──────┴──────┐
                                              │  Module Hub │──AEL──►│  Module Hub │
                                              │     H1      │◄──AEL──│     H2      │
                                              └─┬─────────┬─┘         └─┬─────────┬─┘
                                         Port 1 │  Port 2 │      Port 1 │  Port 2 │
                                              APEM       AAM           US        APBM
```

- **APEM** — Plant Electrophysiology Module, recording continuously; has a threshold detector on one channel; declares the capability to continue a running Session without the host.
- **AAM** — Audio Module, plays acoustic bursts; can change playback phase while running.
- **US** — an ultrasound stimulus Module (hypothetical; no Product Family exists yet), emits a burst on request.
- **APBM** — Photobiology Module, runs a multi-wavelength light schedule; reports phase completions.
- **H1, H2** — Module Hubs with an AEL router each, connected by one Hub-to-Hub AEL link in each direction. Every Module is on a Module Port (MCL + AEL IN + AEL OUT).

## The experiment, as the researcher wrote it

```text
baseline 60 s
then, for 10 trials:
    when APEM detects a spike on channel A (refractory 20 s, max 10 detections):
        AAM plays burst B3 immediately
        US emits one burst
        APBM switches to red phase
    when APBM reports the red phase complete:
        AAM changes to phase 2 if still playing
        APEM marks it
    when AAM or US completes:
        APEM marks it
recovery 120 s
```

Nothing in this text is AEL. What follows is how the host turns it into Module Sessions, bindings and routes.

## 1. Discovery and capability query (MCI)

The host discovers four Modules through the two Hubs and reads their identity and capabilities ([AES-MCI-002](../docs/05-interfaces-and-versioning.md#aes-mci-002-module-identity), [AES-MCI-003](../docs/05-interfaces-and-versioning.md#aes-mci-003-module-capability-discovery)):

```text
APEM  serial 0x2A41  fw 1.3.0  AEL 0.1  AEL IN yes  AEL OUT yes  rx_bindings ≤ 8  src_bindings ≤ 4  autonomous_session yes
AAM   serial 0x1107  fw 2.0.1  AEL 0.1  AEL IN yes  AEL OUT yes  rx_bindings ≤ 4  src_bindings ≤ 2  autonomous_session yes
US    serial 0x0C12  fw 0.4.0  AEL 0.1  AEL IN yes  AEL OUT yes  rx_bindings ≤ 2  src_bindings ≤ 1  autonomous_session no
APBM  serial 0x3390  fw 1.1.0  AEL 0.1  AEL IN yes  AEL OUT yes  rx_bindings ≤ 4  src_bindings ≤ 2  autonomous_session yes
H1    AEL 0.1  ports 8 + 2 hub links  routes ≤ 64  queue 8/output  fwd latency 66–74 µs (input SOF → output SOF)  skew ≤ 0.4 µs
H2    (same product)
```

It also reads the Hubs' identity, capacity and timing figures through the Hub management contract ([AES-AEL-005](../docs/05-interfaces-and-versioning.md#aes-ael-005-active-hub-routing-and-bounded-overload-behavior); its concrete form is open).

## 2. Compilation: names become identifiers

The host allocates identifiers for this deployment — unique per logical event source across both Hubs, because the two routers form one routing domain:

| Semantic event | Source | `event_id` |
|---|---|---|
| `t0` | H1 (AEL event source, host-requested) | `0x0001` |
| `apem.spike_a` | APEM | `0x0201` |
| `apem.acquisition_started` | APEM | `0x0202` |
| `aam.burst_complete` | AAM | `0x0301` |
| `us.burst_complete` | US | `0x0302` |
| `apbm.red_phase_complete` | APBM | `0x0303` |

The names never leave the host. The table is stored in the deployment record so every `0x0201` in every log can be decoded later.

## 3. Module Sessions and bindings

The known timeline stays local: each Module's Session holds its own schedule against `t0`. AEL carries only what cannot be scheduled.

```text
APEM  session = REC-7   timeline: t0 → record continuously; stop at t0+60+trials+120 s
      detector A: threshold, refractory 20 s, max 10          (the guard lives here, in the Module)
      rx  0x0001 → START_SESSION      enabled in ARMED
      rx  0x0301 → INSERT_MARKER      enabled in RUNNING
      rx  0x0302 → INSERT_MARKER      enabled in RUNNING
      rx  0x0303 → INSERT_MARKER      enabled in RUNNING
      src DETECTOR_A_FIRED   → 0x0201
      src ACQUISITION_STARTED → 0x0202

AAM   session = B3      asset B3 verified present
      rx  0x0001 → START_SESSION      enabled in ARMED        (starts silent playback context at t0)
      rx  0x0201 → PLAY_BURST         enabled in RUNNING
      rx  0x0303 → CHANGE_PHASE(2)    enabled in RUNNING
      src BURST_COMPLETE → 0x0301
      post_complete = REPEAT_ARMED

US    session = PULSE-1
      rx  0x0201 → EMIT_BURST         enabled in ARMED, RUNNING
      src BURST_COMPLETE → 0x0302
      post_complete = REPEAT_ARMED

APBM  session = LIGHT-4 timeline: t0 → white baseline; red phase on event
      rx  0x0001 → START_SESSION      enabled in ARMED
      rx  0x0201 → SET_PHASE(red)     enabled in RUNNING
      src PHASE_COMPLETE(red) → 0x0303
```

Every binding is checked against the Module's declared limits (US supports two receive bindings; it gets one). `0x0202` has a source but, in this experiment, no consumer — that is allowed.

## 4. Hub route tables

Routes are compiler output, keyed by ingress port and identifier. The researcher never writes them.

```text
H1 routes (identity a41c…9e)                 H2 routes (identity 7f02…b3)
  P1 + 0x0201 → P2, LINK→H2                    LINK←H1 + 0x0001 → P1, P2
  P1 + 0x0202 → (none)                         LINK←H1 + 0x0201 → P1, P2
  P2 + 0x0301 → P1                             P1 + 0x0302 → LINK→H1
  LINK←H2 + 0x0302 → P1                        P2 + 0x0303 → LINK→H1, P1
  LINK←H2 + 0x0303 → P1, P2
  SRC + 0x0001 → P1, P2, LINK→H2
```

Note `P2 + 0x0303 → LINK→H1, P1` on H2: the compiler also routes APBM's phase completion to US (H2 port 1), where nothing is bound to it. That is deliberate here, to show what happens (step 11). Before committing, the host validates: every route's ports exist, tables fit (12 of 64), the Hub-to-Hub topology is acyclic (two Hubs, one link pair — trivially), every required Module is present with matching identity, all bindings fit, and the event/action graph's only cycle (`0x0201 → stimuli → completions → APEM marker`) is bounded by APEM's refractory period and detection count.

## 5. Stage, validate, commit

```text
host → H1: stage(route table, hash a41c…9e)   H1: validated       host → H1: commit   H1: active = a41c…9e
host → H2: stage(route table, hash 7f02…b3)   H2: validated       host → H2: commit   H2: active = 7f02…b3
```

The host reads back both active identities and records them. From this point the tables are frozen for the deployment.

## 6. Arming

The host transfers Sessions and Assets that are missing (MCI inventory says AAM already holds B3), selects them, and arms each Module. Each reports `ARMED` only after its own checks ([AES-MCI-004](../docs/05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary)): configuration valid, bindings valid, Session verified, no fault. The host confirms all four are `ARMED` before anything else. US, with no autonomous capability, is armed like the others; it simply cannot promise to finish without the host.

## 7. `T0`

```text
host → H1: emit event 0x0001
H1 SRC frame 0x0001 → P1 (APEM), P2 (AAM), LINK→H2   all outputs launched within 0.4 µs of each other
H2 LINK←H1 frame 0x0001 → gap confirmed, validated → P1 (US: unbound, ignored, logged), P2 (APBM)   +70 µs

APEM  0x0001 in ARMED → START_SESSION → RUNNING     ref instant t=0 local, sample 0
AAM   0x0001 in ARMED → START_SESSION → RUNNING
APBM  0x0001 in ARMED → START_SESSION → RUNNING     (70 µs later than APEM; recorded, not hidden)
US    0x0001 → no binding → ignored (UNBOUND), counted; stays ARMED
```

The 70 µs offset between the Hubs is one store-and-forward hop: H2 must receive all four bytes and the two-character gap (60 µs at 1 Mbit/s) before it may validate and forward. It is in H2's published figures and in the record. How long the host's request took to reach H1 is irrelevant to relative timing.

## 8. Baseline runs locally

For 60 s nothing travels on AEL. APEM records, AAM holds its silent context, APBM runs white light — each from its own Session against its own clock. The Hubs count zero frames.

## 9. APEM detects a spike

```text
APEM  sample 2 418 903  detector A crossed threshold   → src binding → frame 0x0201 on AEL OUT
      log: TX 0x0201  sample 2418903  state RUNNING  session REC-7  tx_count 2 (0x0202 was #1)
H1    P1 RX 0x0201 → validated → P2 (AAM) and LINK→H2, launched within skew
H2    LINK←H1 RX 0x0201 → validated → P1 (US), P2 (APBM)
AAM   0x0201 in RUNNING → PLAY_BURST   log: RX 0x0201 ACTED  frame ref t=…  action PLAY_BURST
US    0x0201 in ARMED   → EMIT_BURST → RUNNING
APBM  0x0201 in RUNNING → SET_PHASE(red)
```

APEM continues acquiring throughout; its detector now ignores channel A for 20 s (refractory, local configuration).

## 10. Completions come back — reactions while `RUNNING`

```text
US    burst ends → src → 0x0302 → H2 P1 → LINK→H1 → H1 P1 → APEM: INSERT_MARKER (RUNNING)   US → COMPLETE → ARMED (repeat-armed)
AAM   burst ends → src → 0x0301 → H1 P2 → H1 P1 → APEM: INSERT_MARKER
APBM  red phase ends → src → 0x0303 → H2 P2 → LINK→H1 → H1: P1 (APEM marker), P2 (AAM CHANGE_PHASE(2) — while RUNNING)
                                     → H2 P1 (US)
```

AAM changes phase mid-playback because that binding is enabled in `RUNNING`; a Module built to the old ignore-while-running rule could not have done this.

## 11. An unbound event, a corrupt frame

```text
US    RX 0x0303  → no receive binding → IGNORED (UNBOUND)  counted  no action
H1    LINK←H2  frame with integrity failure (induced for the test) → dropped, invalid_count P_LINK = 1, nothing forwarded
APEM  never sees that frame; its marker count for 0x0303 is one short of APBM's transmit count for trial 6
```

After the run the counter reconciliation — APBM TX 0x0303 = 10, H2 forwarded 10, H1 received 9 valid + 1 invalid, APEM RX 0x0303 = 9 — locates the loss at the Hub-to-Hub link, in trial 6, without ambiguity.

## 12. The host disconnects

At trial 4 the host's transport to H1 drops. Nothing on AEL notices: routes are committed, Modules are armed and running, events flow between them exactly as before. APEM, AAM and APBM have declared autonomous Session capability and continue; US continues too — it needs no host to react to `0x0201` — but had it faulted, no host was there to recover it, which is what its `autonomous_session no` declaration means.

## 13. The host returns

The host reconnects, rediscovers both Hubs and all four Modules by identity, and *reads* their state: three `RUNNING`, US `ARMED`, both route tables still active with the recorded identities, counters advanced. It does not re-arm, re-commit or restart anything ([AES-MCI-004](../docs/05-interfaces-and-versioning.md#aes-mci-004-module-lifecycle-and-the-arm-boundary), §5.2 guidance). It resumes observing.

## 14. Recovery and completion

APEM's Session stops recording at its scheduled end; `COMPLETE → IDLE` (one-shot). AAM and US return to `ARMED` after each burst (repeat-armed) and are disarmed by the host at the end. The host stages nothing new on the Hubs until every dependent Module has left `ARMED`/`RUNNING`.

## 15. The deployment record

What the host stores, and what makes the run reconstructable:

```text
run 2026-09-14/07
modules:   APEM 0x2A41 fw1.3.0 rev B  session REC-7 hash 91e…   AAM 0x1107 …   US 0x0C12 …   APBM 0x3390 …
ael:       version 0.1
event map: 0x0001 t0 · 0x0201 apem.spike_a · 0x0202 apem.acquisition_started · 0x0301 aam.burst_complete · 0x0302 us.burst_complete · 0x0303 apbm.red_phase_complete
bindings:  (per Module, as committed — see step 3)
hubs:      H1 fw 0.9.2 routes a41c…9e · H2 fw 0.9.2 routes 7f02…b3 · link H1↔H2
timing:    H1/H2 published envelopes; APEM frame-to-marker 63 µs ±0.3 (60 µs frame + gap floor, then capture-to-marker); AAM frame-to-burst 104 µs ±2 (floor + pipeline, compensated)
counters:  per device, per port, per direction; 1 invalid frame at H1 LINK←H2 (trial 6); US ignored 11 (1 × 0x0001, 10 × 0x0303)
logs:      APEM acquisition with markers by sample index; AAM/US/APBM event logs; Hub counters
```

A reader with this record and the four Modules' logs can say, for every stimulus, at which APEM sample it was triggered and at which sample its completion was marked — which is the point.

## Hub-free: the same frame, two Modules, one cable

```text
APEM  AEL OUT ──────────────────► AEL IN  AAM

APEM  src DETECTOR_A_FIRED → 0x0201                 AAM  rx 0x0201 → PLAY_BURST  enabled in ARMED, RUNNING
                                                     rx 0x0001 → (not used; AAM is started over MCI here)
```

The host starts APEM's acquisition and AAM's context over MCI (inter-Module timing of the *start* does not matter here), and from then on every detected spike is a `0x0201` frame that AAM acts on within its documented frame-to-action latency. Same firmware, same bindings, same frame, no Hub, no route table — and an identifier that is unique in a routing domain of two.
