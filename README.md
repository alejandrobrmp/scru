# SCRU

Simple Cloudflare Record Updater — a lightweight CLI for keeping your Cloudflare `A` records in sync with your IPv4 address.

## Requirements

- **Python 3.11** or later
- **Linux** (the only supported platform)
- A **Cloudflare API token** with DNS edit permissions for your zone(s)

## Installation

```bash
pip install scru
```

### From source

```bash
git clone https://github.com/anomalyco/scru.git
cd scru
pip install .
```

## Quick Start

1. Set your Cloudflare API token as an environment variable:

   ```bash
   export CLOUDFLARE_API_TOKEN="your-token-here"
   ```

2. Create your config:

   ```bash
   scru config
   ```

   Follow the interactive prompts to select zones, records, and IP sources.

3. Run your updates:

   ```bash
   scru
   ```

   SCRU reads `~/.config/scru/config.yaml` and updates every configured record.

## Commands

### `scru`

Run mode — processes every configured record:

1. Resolves the IPv4 address from the configured source.
2. Fetches the current DNS record from Cloudflare.
3. Skips the record if nothing changed.
4. Updates the record if the IP, proxied flag, or TTL differs.

If no config file exists, `scru` prints a message and launches the config wizard automatically.

### `scru config`

Wizard mode — creates or edits your YAML configuration interactively:

- **New config** — guided prompts walk you through zone selection, record setup, source type, and optional proxied/TTL settings. Supports multiple records and zones. Use `b` to go back.
- **Edit existing** — lists your current records and lets you add, update, or delete entries.

## Configuration

Config lives at `~/.config/scru/config.yaml`. It is a YAML file with the following schema:

| Key | Type | Required | Description |
|---|---|---|---|
| `records` | `list` | yes | One or more DNS record configurations |

Your Cloudflare API token is read from the `CLOUDFLARE_API_TOKEN` environment variable — it is never stored in the config file.

Each record in `records`:

| Key | Type | Required | Description |
|---|---|---|---|
| `zone_id` | `string` | yes | Cloudflare zone ID (hex string) |
| `name` | `string` | yes | DNS record name (e.g. `home.example.com`) |
| `source` | `object` | yes | IP source configuration (see below) |
| `proxied` | `boolean` | no | Enable Cloudflare's orange-cloud proxying |
| `ttl` | `integer` | no | Time-to-live in seconds (ignored when `proxied` is on) |

### Source types

Each record's `source` object has a `type` field and type-specific fields:

#### Fixed

Hardcodes a static IPv4 address.

| Key | Type | Required |
|---|---|---|
| `type` | `"fixed"` | yes |
| `value` | `string` | yes — any valid IPv4 address |

#### Public

Detects your machine's public IPv4 using [ipify](https://api.ipify.org).

| Key | Type | Required |
|---|---|---|
| `type` | `"public"` | yes |

Set `SCRU_PUBLIC_IP_URL` to override the detection endpoint.

#### Custom

Runs a shell command and uses its stdout as the IPv4 address.

| Key | Type | Required |
|---|---|---|
| `type` | `"custom"` | yes |
| `command` | `string` | yes — the shell command to run |

Rules for custom sources:

- Stdout must be **exactly one valid IPv4 string**.
- The command times out after **10 seconds**.
- If the command fails, **only that record** is affected — others continue.

### Example config

```yaml
records:
  - zone_id: abc123def456
    name: home.example.com
    source:
      type: public
    proxied: true

  - zone_id: abc123def456
    name: api.example.com
    source:
      type: fixed
      value: 203.0.113.42
    ttl: 300

  - zone_id: xyz789uvw012
    name: vpn.example.org
    source:
      type: custom
      command: curl -s https://checkip.amazonaws.com
    proxied: false
    ttl: 120
```

## Cloudflare TTL and proxied behavior

- **Proxied records** (`proxied: true`) ignore TTL — Cloudflare enforces a fixed TTL of `1` when proxying is on. SCRU does not fight this and will not send a TTL value for proxied records.
- **Unproxied records** respect the configured TTL. If no TTL is set, Cloudflare's default is used.
- SCRU never overrides provider-enforced settings.

## Error behavior

- Failures are **isolated per record** — one failing record does not stop the others.
- Records that are **already up-to-date** (same IP, proxied flag, and TTL) are skipped with a `skipped (unchanged)` message.
- Config errors are reported with a short `config: failed` message.
- The Cloudflare API token is never logged or printed.

## Output

Each run produces one line per record:

```
home.example.com  updated
api.example.com   skipped (unchanged)
vpn.example.org   updated
```

States shown: `updated`, `skipped (unchanged)`, or `failed (reason)`.

## Examples

### End-to-end: update a single record using your public IP

1. Create the config with the wizard:

   ```bash
   $ export CLOUDFLARE_API_TOKEN="your-token"
   $ scru config
   ```

   ```
   Choose a zone:
     [1] example.com
   Zone: 1

   Choose a record:
     [1] example.com
     [2] home.example.com
   Record: 2

   Choose source type:
     [1] fixed   (static IP)
     [2] public  (detect from ipify)
     [3] custom  (run a command)
   Source type: 2

   Enable proxying (orange cloud)? [y/N]: y

   TTL (leave empty for default): [Enter]

   Add another record? [y/N]: n
   Config saved.
   ```

2. Run the update:

   ```bash
   $ scru
   home.example.com  updated
   ```

   On subsequent runs when nothing has changed:

   ```bash
   $ scru
   home.example.com  skipped (unchanged)
   ```