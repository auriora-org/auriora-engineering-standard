# EDR-001: Controllers Are Separated from Modules

## Status

Accepted

## Context

AURIORA Modules may integrate microcontrollers, embedded computers, analog front ends, power management and mechanical assemblies. Early projects could document the controller board as the product, but doing so would couple product identity to implementation and make reuse harder.

## Alternatives Considered

| Alternative | Assessment |
|---|---|
| Treat controller board as the Module | Fast for prototypes, but product identity changes whenever control implementation changes. |
| Create a generic controller pool independent of Modules | Good for reuse, but too abstract for safety and product-specific behavior. |
| Separate Controllers from Modules while allowing physical integration | Preserves product boundary and implementation flexibility. |

## Decision

Controllers are architecturally distinct from Modules. A Controller may be physically inside a Module, but it SHALL not replace Module-level product documentation, safety policy or external compatibility declaration.

## Rationale

This fits AURIORA because scientific and hardware products need stable external behavior while control electronics evolve. The Module owns product behavior; the Controller owns implementation.

## Consequences

Projects must document both Module and Controller roles when both exist. This increases design documentation effort but enables controller replacement, reuse and clearer review boundaries.

## Affected Requirements

- [AES-HIST-002](../08-decisions-and-governance.md#2-fixed-historical-decisions)
- [Architecture](../03-architecture.md) — Controller design and ownership boundaries

## Future Review Criteria

Revisit only if multiple released Modules demonstrate that Controller separation creates more ambiguity than it removes, and an alternative preserves product identity, safety ownership and implementation replaceability.
