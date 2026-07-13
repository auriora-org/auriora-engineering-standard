# ADR-001: Platform-First Modular Architecture

## Status

Accepted

## Context

AURIORA is intended to evolve for decades across biological sensing, electrophysiology, photobiomodulation, environmental sensing, acoustics and related technologies. A product-by-product architecture would optimize early prototypes but would create incompatible connectors, inconsistent documentation, non-reusable firmware and poor repairability.

## Decision

AES adopts a Platform-first modular architecture with canonical roles: Platform, Module, Controller, Unit, Host Interface and Unit Interface. Modules are standalone products; Controllers are dedicated control implementations; Units are replaceable functional building blocks; interfaces are versioned contracts.

## Consequences

This decision increases early documentation and design effort. In exchange, it enables reuse, compatibility review, long-term maintenance, repairability and open engineering collaboration. Local optimizations that fragment the Platform require explicit exceptions.

## Affected Requirements

- [AES-GOV-002](../../STANDARD.md#aes-gov-002-platform-first-decisions)
- [Principles](../01-principles.md) and [Architecture](../03-architecture.md) — platform-first thinking and ownership boundaries
