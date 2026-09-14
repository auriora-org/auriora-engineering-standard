# AURIORA Module Synchronization Interface (SYNC) — Superseded

**Interface Identifier:** `SYNC`
**Version:** `0.1`
**Status:** Superseded by [`AEL`](./ael.md) as of AES `0.8.0` (2026-09-14)

The Module Synchronization Interface — a single-meaning rising-edge event on a point-to-point RS-422-compatible differential link, with a controller-less fan-out Hub — was the Platform's Module-to-Module event interface in AES `0.6.0` to `0.7.1`. It was decided in [EDR-006](../edr/EDR-006-module-synchronization-interface.md) and placed inside the Module Hub by [EDR-007](../edr/EDR-007-module-control-interface-and-module-hub.md).

It is superseded by the **AURIORA Event Link (AEL)** — [`docs/interfaces/ael.md`](./ael.md), [Interfaces and Versioning §4](../05-interfaces-and-versioning.md#4-auriora-event-link) — under [EDR-008](../edr/EDR-008-auriora-event-link.md). AEL keeps SYNC's point-to-point differential electrical layer, its M8 3-position connector and its receiver-side termination, and replaces the bare edge with a small typed event frame routed by an active Hub. The reasons, the alternatives weighed and the deliberately accepted trade-offs are in EDR-008. The requirement identifiers `AES-SYNC-001` to `AES-SYNC-004` are retired and listed in the [Document Index](../document-index.md).

The full SYNC `0.1` Draft specification, the SYNC requirements and the SYNC worked example are preserved in the repository history and in the last AES release that carried them: [`v0.7.1`](https://github.com/auriora-org/auriora-engineering-standard/tree/v0.7.1/docs/interfaces/sync.md). No Module or Hub ever claimed Released conformance to SYNC; it was Draft throughout. AEL is not wire-compatible with it.
