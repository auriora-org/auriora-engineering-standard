# Worked Example: Choosing a Unit Interface Profile — Withdrawn

**Document ID:** AES-EXAMPLE-UIF-SELECTION
**Status:** Withdrawn as of AES `0.14.0` (2026-10-20)

This example assessed four planned Units — AENU, ASPU, the Soil Unit and the Communication & Timing Unit — against the profile-selection rule of AES `0.5.0`–`0.13.0`, which chose between `UIF-MI2C-8` and `UIF-MSPI-14` by throughput, latency, determinism and streaming. Its finding that the boundary falls on timing rather than on volume stands, and is carried into [AES-IF-010](../docs/05-interfaces-and-versioning.md#aes-if-010-unit-interface-profile-declaration) as the criteria that take a Unit beyond the Platform's single profile.

The selection it illustrated no longer exists: every Unit declares [`UIF-RS485-4`](../docs/interfaces/uif-rs485-4.md) ([EDR-017](../docs/edr/EDR-017-unit-link-profile-and-family-consolidation.md)). All four Units assessed here fit it; the Communication & Timing Unit's hardware time reference remains the recorded case for a future profile.

The full text is preserved in the repository history and in the last AES release that carried it: [`v0.13.0`](https://github.com/auriora-org/auriora-engineering-standard/tree/v0.13.0/examples/worked-example-unit-interface-profile-selection.md).
