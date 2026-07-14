# Unit Interface Profile Specifications

**Status:** Per-profile status stated in each file (both profiles are currently Draft)
**Depends On:** [Interfaces and Versioning](../05-interfaces-and-versioning.md), [EEPROM Metadata](../06-eeprom-metadata.md)

This directory holds the concrete, versioned **Unit Interface Profile** specifications. The profile-independent rules — the `UIF_` signal set, `UIF_READY` semantics, the discovery and activation sequence, and profile versioning — live in [Interfaces and Versioning](../05-interfaces-and-versioning.md) ([AES-IF-008](../05-interfaces-and-versioning.md#aes-if-008-versioned-unit-interface-profiles)). The files here define the parts that are specific to one profile: connector, pinout, electrical limits and timing.

Each profile is versioned independently. A Released Unit and its host declare the profile identifier and version they implement in EEPROM metadata ([AES-EEPROM-008](../06-eeprom-metadata.md#aes-eeprom-008-execution-model-profile-and-api-metadata)).

| Profile | File | Status | Intended for |
|---|---|---|---|
| `AURIORA UIF-I2C-6` | [uif-i2c-6.md](./uif-i2c-6.md) | Draft | Passive Units and simple I²C-based Units |
| AURIORA Managed SPI Profile | [managed-spi.md](./managed-spi.md) | Draft | Managed Units requiring a high-level SPI API |
