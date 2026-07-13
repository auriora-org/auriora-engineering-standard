# AURIORA Engineering Standard

The AURIORA Engineering Standard (AES) is the constitutional engineering reference for the AURIORA Platform: it defines the architectural vocabulary (Product Families, Modules, Controllers, Units, Host Interfaces, Unit Interfaces), naming and identity principles, interface and compatibility rules, the maturity model, and minimum release expectations.

AES is a compact constitution designed for a small team — currently one or two developers — doing disciplined open engineering. It scales requirements by **maturity level** (Experimental, Active Development, Released) instead of applying release-grade process to prototypes. The guiding principle: *create enough documentation to understand, continue, test and reproduce the work, but never require documentation whose maintenance costs more than the risk it reduces.*

Start with [STANDARD.md](./STANDARD.md).

## Reading Order

1. [STANDARD.md](./STANDARD.md) — scope, requirement language, maturity model, conformance, foundation rules
2. [Principles](./docs/01-principles.md)
3. [Terminology](./docs/02-terminology.md)
4. [Architecture](./docs/03-architecture.md)
5. [Naming and Identity](./docs/04-naming-and-identity.md)
6. [Interfaces and Versioning](./docs/05-interfaces-and-versioning.md)
7. [EEPROM Metadata](./docs/06-eeprom-metadata.md)
8. [Maturity and Release](./docs/07-maturity-and-release.md)
9. [Decisions and Governance](./docs/08-decisions-and-governance.md)
10. [Review Checklists](./docs/09-review-checklists.md)
11. [Document Index](./docs/document-index.md)
12. [Worked Example](./examples/worked-example-module-lifecycle.md)

## Companion Standards and Guides

AES defines *what* must be true; the companions define *how* work is done in their domain. Where a companion and AES conflict, AES prevails.

- [AURIORA Hardware Design Guide](https://github.com/auriora-org/auriora-hardware-design-guide) (`AHDG`) — how hardware is designed
- [AURIORA Firmware Style Guide](https://github.com/auriora-org/auriora-firmware-style-guide) (`AFSG`) — how embedded firmware is designed and written
- [AURIORA Software Style Guide](https://github.com/auriora-org/auriora-software-style-guide) (`ASSG`) — how host-side software is designed and written
- [AURIORA Documentation Standard](https://github.com/auriora-org/auriora-documentation-standard) (`ADS`) — how documentation is written and maintained

## Requirement Language

- `MUST` / `SHALL` — mandatory when applicable; most requirements are scoped to an artifact type and maturity level
- `SHOULD` — recommended default; engineering judgment may justify another approach, with no formal exception record required
- `MAY` — optional

Deviations from applicable MUSTs need a concise note in the project's design documentation; formal exception records are reserved for Released artifacts and platform-wide deviations. See [STANDARD.md §2](./STANDARD.md#2-requirement-language).

## Repository Status

This repository is a Markdown source of truth. Generated PDFs or websites are derived from these files and are never canonical.

## Versioning and Changes

Released AES versions are recorded in the [CHANGELOG](./CHANGELOG.md) and tagged in version control per [AES-GOV-011](./docs/08-decisions-and-governance.md#aes-gov-011-standard-change-record). Feedback and change proposals follow the [contributing policy](./CONTRIBUTING.md).

## License

This documentation is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](./LICENSE).
