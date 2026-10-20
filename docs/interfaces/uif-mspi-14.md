# AURIORA UIF-MSPI-14 Unit Interface Profile — Withdrawn

**Profile Identifier:** `UIF-MSPI-14`
**Version:** `0.1`
**Status:** Withdrawn as of AES `0.14.0` (2026-10-20)

`UIF-MSPI-14` was the Draft Unit Interface Profile for Managed Units bound by throughput, latency, deterministic transfer timing or streaming — an SPI transport, `UIF_RESET_N` and `UIF_IRQ_N` beside the six-signal core, on a 14-position 1.00 mm JST SH connector — in AES `0.2.0` to `0.13.0`, with its connector and pinout decided in [EDR-003](../edr/EDR-003-uif-mspi-connector-and-pin-assignment.md).

It is withdrawn by [EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md). The need it was meant for is real and remains recorded: deterministic, streaming and time-reference transfer are outside [`UIF-RS485-4`](./uif-rs485-4.md), and the cell stays open in the profile family, to be filled by a profile designed against the first Unit that needs it ([AES-IF-010](../05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration)). This profile was provisional by its own record, had no realization and an open electrical layer, and would have constrained that future profile without informing it.

The full `UIF-MSPI-14` `0.1` Draft specification is preserved in the repository history and in the last AES release that carried it: [`v0.13.0`](https://github.com/auriora-org/auriora-engineering-standard/tree/v0.13.0/docs/interfaces/uif-mspi-14.md). No Unit or host implemented it. The identifier is reserved and is not reused.
