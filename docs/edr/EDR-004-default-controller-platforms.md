# EDR-004: Default Controller Platforms

## Status

Accepted

*Accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance): the decision records the platform convergence already realized across the existing Unit and Module families rather than proposing a new direction.*

## Context

AURIORA spans Units with a single bounded sensing function and Modules performing continuous acquisition, DSP and multi-task real-time work. Controller platform selection for one product is ordinarily routine engineering judgment ([Decisions and Governance §3](../08-decisions-and-governance.md#3-when-a-decision-needs-a-record)), recorded at most in a project ADR.

Repeated across a growing family of products, however, it stops being local. Every new platform multiplies the HAL, build, debug, flashing, test and bring-up work the Platform must carry, and firmware written against one MCU family does not transfer to another. Left unstated, the choice is made per project by whatever was convenient that month, and the reuse the Platform exists to concentrate ([AES-HIST-001](../08-decisions-and-governance.md#2-fixed-historical-decisions)) never accumulates. That reach — cross-repository, shared across product families, expensive to unwind once firmware exists — is what makes this a Platform decision requiring a record ([AES-EDR-001](../08-decisions-and-governance.md#aes-edr-001-edr-trigger)).

Naming vendor platforms in AES is a deliberate exception. AES and its companion guides are otherwise technology-neutral, and the companion guides remain so: the [Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) states no part numbers, and the [Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) is written to apply to any embedded platform. That neutrality is what keeps *design rules* durable while parts age. A statement of which platforms AURIORA has actually converged on is a different kind of statement, and hiding it does not make it less true — it only makes departures invisible.

## Alternatives Considered

| Alternative | Assessment |
|---|---|
| No stated default; per-project choice | Status quo. Maximum freedom per board, but firmware reuse, toolchain investment and reviewer familiarity fragment across families. The decision still gets made every time, just without a baseline to depart from. |
| Single platform for everything | Simplest possible story. Rejected: no one MCU family serves both a sub-µA-budget sensor Unit and a multi-channel streaming Module well. Forcing one direction wastes power in the small case or starves throughput in the large one. |
| **Two defaults, selected by workload profile** | **Chosen.** Two platforms is few enough to sustain real reuse and broad enough to cover the actual range. Keying selection to the workload — bounded low-power function vs. local processing — rather than to the Unit/Module role keeps the rule correct for a Managed Unit doing DSP and for a thin Module alike. |
| Two defaults, keyed to Unit vs. Module | Rejected. Simpler to read, but wrong at the edges the Platform already contains: AEU-01 is a Unit with a substantial controller ([EDR-003](./EDR-003-uif-mspi-connector-and-pin-assignment.md)), and Modules exist whose Controller does little. A role-keyed rule would turn ordinary designs into documented deviations. |
| Mandatory (`SHALL`) rather than default (`SHOULD`) | Rejected. A hard mandate would force an exception record for legitimate cases — a part with no alternative in the default families, a radio or compute SoC whose controller is intrinsic to the function, an experiment on borrowed hardware. `SHOULD` with a stated reason gets the convergence without the ceremony. |

## Decision

AURIORA has two default controller platforms, selected by workload profile: a **low-power STM32-class MCU** (STM32U0 / STM32L0 families) for a bounded low-power sensing, actuation or interface function, and an **RP2040-class MCU** where higher local processing, buffering, DSP or parallel real-time workloads justify it. The rule is normative as [AES-ARCH-001](../03-architecture.md#aes-arch-001-default-controller-platform) at `SHOULD` strength; another platform may be used where technical requirements warrant it, with the reasons stated in the project's design notes or an ADR.

## Rationale

The two profiles reflect a real discontinuity rather than a preference. A bounded sensor function is dominated by sleep current, wake latency and part count, which is what the low-power STM32 families are built for and where their integrated Flash and minimal external circuitry pay off directly. A streaming or DSP workload is dominated by sustained throughput, DMA depth, SRAM and concurrency, where programmable I/O, a second core and larger SRAM change what the firmware can do at all.

Keying the default to the workload rather than the architectural role also means the rule survives new products: a Unit or Module family that does not exist yet is classified by what its firmware must do, without amending AES.

## Consequences

- The Platform commits to maintaining toolchain, HAL and bring-up support for two MCU families, and to keeping that support current — a real recurring cost, accepted in exchange for reuse.
- New designs inherit a starting point and a reviewable question ("which profile is this, and does the default fit?") instead of an open field.
- Departures become visible: choosing outside the defaults now requires a stated reason, which is the point.
- AES now names vendor platforms in exactly one place, [Architecture §6](../03-architecture.md#6-default-controller-platform-strategy). Any further vendor-specific content requires its own decision; the companion guides stay technology-neutral.
- The named families will age. When a default family reaches end-of-life or a successor supersedes it, this EDR is superseded by a new one rather than edited ([AES-EDR-002](../08-decisions-and-governance.md#aes-edr-002-decision-record-structure-and-immutability)).
