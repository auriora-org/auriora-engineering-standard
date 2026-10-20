# AURIORA UIF-I2C-6 Unit Interface Profile — Withdrawn

**Profile Identifier:** `UIF-I2C-6`
**Version:** `0.1`
**Status:** Withdrawn as of AES `0.14.0` (2026-10-20)

`UIF-I2C-6` was the Unit Interface Profile for Passive Units — six positions on a 1.00 mm JST SH connector carrying `UIF_PWR_VIN`, `GND`, an I²C discovery and functional bus, `UIF_PWR_EN` and `UIF_READY` — in AES `0.2.0` to `0.13.0`.

It is withdrawn by [EDR-017](../edr/EDR-017-unit-link-profile-and-family-consolidation.md), together with the Passive execution model: every Unit now contains a controller and is connected over the Platform's single Unit Interface Profile, [`UIF-RS485-4`](./uif-rs485-4.md). A board without a controller and without a reusable contract is a Module subassembly, or an internal sensor of a Unit.

The full `UIF-I2C-6` `0.1` Draft specification is preserved in the repository history and in the last AES release that carried it: [`v0.13.0`](https://github.com/auriora-org/auriora-engineering-standard/tree/v0.13.0/docs/interfaces/uif-i2c-6.md). No Released Unit or host implemented it. The identifier is reserved and is not reused.
