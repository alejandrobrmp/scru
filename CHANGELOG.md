# Changelog

## 0.1.0 — 2026-06-25

### Added

- **DNS Update Engine**: update Cloudflare A records from IPv4 sources.
- **Fixed, Public (ipify), and Custom command** IP source types.
- **Multi-record and multi-zone** execution with per-record failure isolation.
- **Cloudflare update rules**: proxied/TTL normalization, skip-on-unchanged, proxied+TTL warning.
- **Interactive config wizard** (`scru config`) with new/edit modes, zone/record browsing, and back navigation.
- **CLI** with `scru` (run updates) and `scru config` (wizard) commands.
- **YAML config** at `~/.config/scru/config.yaml`.
- **CI/CD**: PR validation (unit + integration tests), release branch builds, master-merge releases.
- **README** with full user documentation.
