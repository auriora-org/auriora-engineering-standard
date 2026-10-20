# AURIORA UIF-MI2C-8 Unit Interface Profile — Superseded

**Profile Identifier:** `UIF-MI2C-8`
**Version:** `0.1`
**Status:** Superseded by [`UIF-RS485-4`](./uif-rs485-4.md) as of AES `0.14.0` (2026-10-20)

`UIF-MI2C-8` was the default Unit Interface Profile for low-bandwidth Managed Units — `UIF-I2C-6`'s six signals plus a generic `UIF_IRQ_N` and a second ground on an 8-position 1.00 mm JST SH connector — in AES `0.5.0` to `0.13.0`, decided in [EDR-005](../edr/EDR-005-low-bandwidth-managed-unit-interface.md).

It is superseded by [`UIF-RS485-4`](./uif-rs485-4.md) under [EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md), which keeps what this profile established — a Managed Unit API independent of transport, one discovery record and validation order, the power cycle as recovery, optional events declared in capability metadata — and moves the interface from a single-ended board-level bus with discrete control signals to a differential link for any distance, with the control signals carried as link states. The second ground this profile added for "metres of thin field wiring" was the symptom the new profile answers.

The full `UIF-MI2C-8` `0.1` Draft specification is preserved in the repository history and in the last AES release that carried it: [`v0.13.0`](https://github.com/auriora-org/auriora-engineering-standard/tree/v0.13.0/docs/interfaces/uif-mi2c-8.md). No Released Unit or host implemented it; AENU-01's rework toward it was withdrawn before hardware and retargeted to `UIF-RS485-4`. The identifier is reserved and is not reused.
