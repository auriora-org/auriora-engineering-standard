# EDR-014: Four-Letter Family Identifiers and the Family Identifier Register

## Status

Accepted (2026-09-23)

*Self-authored and accepted by the maintainer as a self-review per [AES-GOV-010](../08-decisions-and-governance.md#aes-gov-010-maintainer-governance).*

This record tightens `AES-NAME-001` and adds the Family Identifier Register to the Document Index. It supersedes nothing: every identifier it renames is pre-Release, which `AES-NAME-001` has always allowed.

## Context

`AES-NAME-001` allowed a family identifier of three to six letters derived from the initials of two to four durable words, and asked the author to check the Document Index and the repositories for collisions. The Document Index held no list of family identifiers, so there was nothing to check against, and initials collided at the first opportunity: a Spectral Unit and a Soil Unit were both about to be `ASU`. Three-letter identifiers with the fixed `A` prefix leave 676 combinations, and initials of English function words cluster in far fewer.

The maintainer proposed, after discussion, that every physical AURIORA product family carry a four-letter code; that the code be a mnemonic rather than initials where clarity requires it; that identifiers never be reused; and asked whether the `-01` suffix should denote a hardware generation.

## Alternatives Considered

| Alternative | Assessment |
|---|---|
| **Keep 3–6 letters and add the register** | The register alone would have prevented the collision. Rejected as insufficient because a variable width also costs uniform labels, serial numbers, file names and identity fields, and three letters leave too little room once the role letter is fixed. |
| **Exactly four letters, mnemonic function letters, role letter last** (chosen) | `A` + two function letters + `M` or `U`: 676 combinations per role, a readable label, and the existing `APEM` and `APBM` unchanged. The role is durable — a Unit never becomes a Module — so it may be in the identifier under the rule's own "durable meaning" test. |
| **Four letters without a role letter** (`AENV`, `ASPC`, `AHUB` throughout) | Rejected. It would have renamed `APEM` and `APBM`, whose `M` is a role letter, and it mixed two patterns in the same proposal (`ACTM` for a Unit). One pattern or the other; the existing one was kept. |
| **Force the role-letter pattern on the Hub** (`AMPH`, `AHUH`) | Rejected. The Hub is the one family whose role is its whole function; a contrived mnemonic would be read as a mistake. `AHUB` is registered individually as an infrastructure family, and the rule says so rather than pretending the pattern fits. |
| **Use `-NN` as the hardware generation** | Rejected; it is the exact level-mixing `AES-ID-001` forbids ("no `APEMB` because Rev B exists"). `-NN` is the product within a family, `Rev <LETTER>` the compatible hardware revision, and the runtime identity already carries Product and Product Revision separately (`AES-MCI-002`, `AES-HUB-004`). An incompatible generation is a new product; a compatible respin is a revision. Both were already expressible. |
| **Encode a countable property in the name** (`AHUB16`) | Rejected. A port count is a property the device declares ([AES-HUB-004](../03-architecture.md#aes-hub-004-hub-identity-and-capability-discovery)) and the host reads; putting it in a name creates the product table AES exists to avoid, and a false identity change when the count changes. Size variants are products: `AHUB-01`, `AHUB-02`. |
| **Reuse an identifier once its family is gone** | Rejected. Old markings and records cannot be recalled; an identifier once entered stays in the register as retired. |

## Decision

1. **`AES-NAME-001`** requires exactly four uppercase letters: `A`, two mnemonic function letters, and the role letter `M` (Module) or `U` (Unit); an infrastructure family is registered individually; entry in the register precedes any use; a registered identifier — current, renamed or retired — is never reused. Pre-Release renaming remains allowed and retires the old identifier.
2. **Naming §5** states that the product number distinguishes products within a family by host-visible contract, that a compatible redesign is a hardware revision, and that neither a hardware generation nor a countable property appears in a family identifier or product number.
3. The **Family Identifier Register** in the Document Index is the allocation record. Allocated: `APEM`, `APBM`, `AASM` (renames `AAM`), `AENU` (renames `AEU`), `AHUB`. Reserved: `ASPU`, `ASOU`, `AWNU`, `ACTU`, `AGEU`. Retired, never reused: `AAM`, `AEU`, `ASU`, `AAC` (family discontinued), `AMH` (superseded by `AHUB` before any use).
4. The Hub's provisional AOID is `AOID:PUB:HUB:GEN:AHUB:001`; `AEU`'s provisional AOID is re-registered as `AOID:PUB:UNIT:ENV:AENU:001`.
5. The **`AAM` → `AASM` and `AEU` → `AENU` renames** are decided and registered now, and this standard's own text — chapters, interface specifications, examples and the identifiers inside earlier decision records — is migrated in the same release; the release history in the changelog keeps the names it was written with. Hardware marking, firmware and the companion guides migrate before either family Releases, as one deliberate pass per family.

## Rationale

The collision was a missing register, not a missing rule; the register is therefore the load-bearing change, and the width and pattern are what make the register's entries uniform. Two mnemonic letters were chosen over initials because clarity is what a label is for, and over three because the role letter earns its place: a Unit is never a Module, and a code that says which it is can be read on a board without a lookup. Keeping `APEM` and `APBM` unchanged mattered more than pattern purity for the Hub, so the Hub is the documented individual case rather than a forced acronym.

The `-NN` question was answered by what AES already had. Product, revision and instance are separate levels, the runtime identity carries each, and a host learns ports, channels and capabilities from declarations. A generation in the name would have duplicated the revision, and a count in the name would have contradicted the discovery model decided in EDR-012 and EDR-013 the same day.

## Consequences

- `AES-NAME-001` is tightened; Naming §3 and §5 and Terminology's example identifiers change; the Document Index gains the register. Frozen core vocabulary is unchanged.
- **This is a compatible normative change, released as AES `0.10.0`.** No Released artifact carries a family identifier; every affected identifier is pre-Release.
- The `AAM` → `AASM` and `AEU` → `AENU` migrations remain pending in the Hardware Design Guide, the Firmware Style Guide, the AENU-01 schematic and firmware, and the AASM Rev A marking. Until they are done, `AAM` and `AEU` outside this standard denote the families registered as `AASM` and `AENU`. Identifiers inside earlier EDRs were migrated mechanically; the records' decisions are unchanged.
- The Hub family is `AHUB`; its first product `AHUB-01` is the 8 + 1 + 1-port Hub of EDR-013; further sizes are `AHUB-02`, `AHUB-03`, never encoded in the identifier.
- The private engineering knowledge base is re-derived afterwards.
- This is a self-authored decision; the self-review is recorded per AES-GOV-010.

## Scope and Remaining Open Items

**Settled:** identifier width, pattern, role letters, the Hub as an individually registered infrastructure family, the register as precondition of use, no reuse ever, product versus revision versus generation, the renames and their timing rule.

**Open — product work, not Platform decisions:** the migration passes for `AASM` and `AENU`; whether a Controller role letter is ever needed (none is, while Controllers stay internal to Modules per [EDR-001](./EDR-001-controller-module-separation.md) and `AAC` is discontinued).

## Affected Requirements / Documents

- [Naming and Identity](../04-naming-and-identity.md) — §3 introduction, `AES-NAME-001` (requirement, rationale, guidance), §5 (product versus revision).
- [Document Index](../document-index.md) — Family Identifier Register (new); AOID table (`AHUB`, `AEU` note).
- [Terminology §2](../02-terminology.md) — example identifiers in *Product Family*.
- [Worked Example: Choosing a Unit Interface Profile](../../examples/worked-example-unit-interface-profile-selection.md) — `ASU` → `ASPU`.
- [EDR-007](./EDR-007-module-control-interface-and-module-hub.md), [EDR-013](./EDR-013-mcl-cascading-and-path-addressing.md) — Hub identifier `AHUB`.
- `STANDARD.md`, `CHANGELOG.md` — indexing and release notes.
- All AES chapters, interface specifications, examples and earlier EDRs — `AEU` → `AENU`, `AAM` → `AASM` (mechanical). Hardware Design Guide, Firmware Style Guide, AENU-01 and AASM hardware and firmware — migration passes, later.

## Future Review Criteria

Revisit if: a family cannot be named readably within two function letters; a third role beside Module and Unit needs a letter; or the register's allocation becomes a bottleneck for a team larger than the maintainer.
