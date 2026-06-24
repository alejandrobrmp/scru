from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from .config import (
    Config,
    RecordConfig,
    SourceConfig,
    load_config,
    save_config,
)
from .constants import CONFIG_PATH, CLOUDFLARE_API_TOKEN_ENV_VAR
from .helpers import config_exists


def _setup_encoding() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _clear_screen() -> None:
    print("\033[2J\033[H", end="")


def _breadcrumb(
    mode: str,
    zone_name: str | None = None,
    record_name: str | None = None,
) -> None:
    width = shutil.get_terminal_size().columns
    box_width = min(width - 1, 80)

    if box_width >= 60:
        parts = [f"  {mode}  "]
        if zone_name:
            parts.append(f"·  {zone_name}  ")
        if record_name:
            parts.append(f"·  {record_name}  ")
        line = "".join(parts).rstrip()
        line = line[: box_width - 2]
        print("╔" + "═" * box_width + "╗")
        print("║" + line.ljust(box_width) + "║")
        print("╚" + "═" * box_width + "╝")
    else:
        print("╔" + "═" * box_width + "╗")
        print("║" + f"  {mode}".ljust(box_width) + "║")
        if zone_name:
            print("║" + f"  zone: {zone_name}".ljust(box_width) + "║")
        if record_name:
            print("║" + f"  record: {record_name}".ljust(box_width) + "║")
        print("╚" + "═" * box_width + "╝")


def _section_header(title: str, width: int = 60) -> None:
    remaining = width - len(title) - 1
    left = max(remaining // 2, 0)
    right = max(remaining - left, 0)
    print(f"{'─' * left} {title} {'─' * right}")


def _source_summary(source: SourceConfig) -> str:
    if source.type == "fixed":
        return f"fixed: {source.value}"
    if source.type == "custom":
        return f"custom: {source.command}"
    return "public"


def _record_summary_line(record: RecordConfig, zone_name: str) -> str:
    source_str = _source_summary(record.source)
    proxied_str = "yes" if record.proxied else "no"
    ttl_str = str(record.ttl) if record.ttl is not None else "auto"
    return f"{record.name} @ {zone_name}   ({source_str}  | proxied: {proxied_str} | ttl: {ttl_str})"


def _config_source_page(
    input_func: Callable[[str], str],
    *,
    current_source: SourceConfig | None = None,
) -> SourceConfig:
    default_choice = "2"
    if current_source and current_source.type == "fixed":
        default_choice = "1"
    elif current_source and current_source.type == "custom":
        default_choice = "3"

    print()
    print("Source type:")
    print("  1. fixed   — enter an IP manually")
    print("  2. public  — use my current public IP")
    print("  3. custom  — run a command")

    choice = input_func(f"Select (1-3) [{default_choice}]: ").strip() or default_choice

    if choice == "1":
        default_value = current_source.value if current_source and current_source.type == "fixed" else ""
        prompt = f"Fixed IPv4: " if not default_value else f"Fixed IPv4 [{default_value}]: "
        value = input_func(prompt).strip()
        if not value and default_value:
            value = default_value
        return SourceConfig(type="fixed", value=value)

    if choice == "3":
        default_cmd = current_source.command if current_source and current_source.type == "custom" else ""
        prompt = f"Command: " if not default_cmd else f"Command [{default_cmd}]: "
        command = input_func(prompt).strip()
        if not command and default_cmd:
            command = default_cmd
        return SourceConfig(type="custom", command=command)

    return SourceConfig(type="public")


def _config_proxied_ttl_page(
    input_func: Callable[[str], str],
    *,
    current_proxied: bool | None = None,
    current_ttl: int | None = None,
) -> tuple[bool | None, int | None]:
    if current_proxied is not None:
        default_proxied = "y" if current_proxied else "n"
        proxied_input = input_func(f"Proxied? (y/n) [{default_proxied}]: ").strip().lower() or default_proxied
    else:
        proxied_input = input_func("Proxied? (y/n) [n]: ").strip().lower() or "n"

    proxied: bool | None = True if proxied_input == "y" else False if proxied_input == "n" else None

    if current_ttl is not None:
        ttl_input = input_func(f"TTL in seconds (blank=omit) [{current_ttl}]: ").strip()
        if not ttl_input:
            ttl = current_ttl
        else:
            ttl = int(ttl_input) if ttl_input else None
    else:
        ttl_input = input_func("TTL in seconds (blank=omit): ").strip()
        ttl = int(ttl_input) if ttl_input else None

    if proxied and ttl is not None:
        print("⚠ warning: ttl is ignored for proxied records")

    return proxied, ttl


def new(
    *,
    config_path: Path | None = None,
    input_func: Callable[[str], str] = input,
) -> None:
    _setup_encoding()
    if CLOUDFLARE_API_TOKEN_ENV_VAR not in os.environ:
        print(f"\u2718 {CLOUDFLARE_API_TOKEN_ENV_VAR} is not set \u2014 set it and try again.")
        return

    from .cloudflare import CloudflareClient

    path = CONFIG_PATH if config_path is None else config_path
    client = CloudflareClient()

    records: list[RecordConfig] = []
    zone_cache: dict[str, str] = {}

    def _fetch_zones() -> list[Mapping[str, Any]]:
        return client.list_all_zones()

    def _fetch_records(zone_id: str) -> list[Mapping[str, Any]]:
        return client.list_all_records(zone_id)

    while True:
        _clear_screen()
        _breadcrumb("NEW")

        zones = _fetch_zones()
        if not zones:
            print("No zones found in this account.")
            break

        print()
        _section_header("Select zone")
        print()
        for i, zone in enumerate(zones, 1):
            name = zone.get("name", "?")
            zid = zone.get("id", "?")
            print(f"  {i}. {name}   ({zid})")

        zone_input = input_func(f"Select zone (1-{len(zones)}) [1]: ").strip() or "1"
        try:
            idx = int(zone_input) - 1
            if idx < 0 or idx >= len(zones):
                print(f"Invalid selection: {zone_input}")
                continue
        except ValueError:
            print(f"Invalid selection: {zone_input}")
            continue

        zone = zones[idx]
        zone_id = str(zone["id"])
        zone_name = str(zone["name"])
        zone_cache[zone_id] = zone_name

        _clear_screen()
        _breadcrumb("NEW", zone_name=zone_name)

        records_list = _fetch_records(zone_id)
        print()
        _section_header("Select record")
        print()
        if records_list:
            for i, record in enumerate(records_list, 1):
                print(f"  {i}. {record.get('name', '?')}")
        else:
            print("  (no A records found)")

        rec_input = input_func(
            f"Select record (1-{len(records_list)}) or type a new name: " if records_list
            else "Type a new name: "
        ).strip()

        try:
            idx = int(rec_input) - 1
            if 0 <= idx < len(records_list):
                record_name = str(records_list[idx]["name"])
            else:
                record_name = rec_input
        except ValueError:
            record_name = rec_input

        _clear_screen()
        _breadcrumb("NEW", zone_name=zone_name, record_name=record_name)

        source = _config_source_page(input_func)

        _clear_screen()
        _breadcrumb("NEW", zone_name=zone_name, record_name=record_name)

        proxied, ttl = _config_proxied_ttl_page(input_func)

        _clear_screen()
        _breadcrumb("NEW", zone_name=zone_name, record_name=record_name)

        record = RecordConfig(
            zone_id=zone_id,
            name=record_name,
            source=source,
            proxied=proxied,
            ttl=ttl,
        )
        records.append(record)

        print()
        print(f"  Record: {_record_summary_line(record, zone_name)}")

        again = input_func("\nAdd another record? (y/N): ").strip().lower()
        if again != "y":
            break

    if records:
        save_config(path, Config(records=records))
        print(f"\n✔ Config saved to {path}")


def edit(
    *,
    config_path: Path | None = None,
    input_func: Callable[[str], str] = input,
) -> None:
    _setup_encoding()
    if CLOUDFLARE_API_TOKEN_ENV_VAR not in os.environ:
        print(f"\u2718 {CLOUDFLARE_API_TOKEN_ENV_VAR} is not set \u2014 set it and try again.")
        return

    from .cloudflare import CloudflareClient

    path = CONFIG_PATH if config_path is None else config_path
    config = load_config(path)
    client = CloudflareClient()

    zone_cache: dict[str, str] = {}

    def _get_zone_name(zid: str) -> str:
        if zid not in zone_cache:
            try:
                zones = client.list_all_zones()
                for z in zones:
                    zone_cache[str(z["id"])] = str(z["name"])
            except Exception:
                pass
        return zone_cache.get(zid, zid)

    for r in config.records:
        _get_zone_name(r.zone_id)

    while True:
        _clear_screen()
        _breadcrumb("EDIT")

        print()
        if config.records:
            _section_header("Configured records")
            print()
            for i, record in enumerate(config.records, 1):
                zname = _get_zone_name(record.zone_id)
                print(f"  {i}. {_record_summary_line(record, zname)}")
        else:
            print("  No records")

        print()
        _section_header("Menu")
        print()
        print("  a      Add a new record")
        if config.records:
            print("  u <n>  Update record <n>")
            print("  d <n>  Delete record <n>")
        print("  q      Save and quit")

        cmd = input_func("> ").strip()

        if cmd == "q":
            save_config(path, config)
            if config.records:
                print(f"\u2714 Config saved to {path}")
            else:
                print(f"\u2714 Config saved (no records) to {path}")
            return

        if cmd == "a":
            _clear_screen()
            _breadcrumb("EDIT")

            zones = client.list_all_zones()
            if not zones:
                print("\nNo zones found in this account.")
                input_func("Press Enter to continue...")
                continue
            for z in zones:
                zone_cache[str(z["id"])] = str(z["name"])

            print()
            _section_header("Add record — Select zone")
            print()
            for i, zone in enumerate(zones, 1):
                name = zone.get("name", "?")
                zid = zone.get("id", "?")
                print(f"  {i}. {name}   ({zid})")

            zone_input = input_func(f"Select zone (1-{len(zones)}) [1]: ").strip() or "1"
            try:
                idx = int(zone_input) - 1
                if idx < 0 or idx >= len(zones):
                    continue
            except ValueError:
                continue

            zone = zones[idx]
            zone_id = str(zone["id"])
            zone_name = str(zone["name"])

            _clear_screen()
            _breadcrumb("EDIT", zone_name=zone_name)

            records_list = client.list_all_records(zone_id)
            print()
            _section_header("Add record — Select record")
            print()
            if records_list:
                for i, rec in enumerate(records_list, 1):
                    print(f"  {i}. {rec.get('name', '?')}")
            else:
                print("  (no A records found)")

            rec_input = input_func(
                f"Select record (1-{len(records_list)}) or type a new name: " if records_list
                else "Type a new name: "
            ).strip()

            try:
                idx = int(rec_input) - 1
                if 0 <= idx < len(records_list):
                    record_name = str(records_list[idx]["name"])
                else:
                    record_name = rec_input
            except ValueError:
                record_name = rec_input

            _clear_screen()
            _breadcrumb("EDIT", zone_name=zone_name, record_name=record_name)

            source = _config_source_page(input_func)

            _clear_screen()
            _breadcrumb("EDIT", zone_name=zone_name, record_name=record_name)

            proxied, ttl = _config_proxied_ttl_page(input_func)

            config.records.append(RecordConfig(
                zone_id=zone_id,
                name=record_name,
                source=source,
                proxied=proxied,
                ttl=ttl,
            ))
            continue

        if cmd.startswith("d "):
            try:
                n = int(cmd.split()[1]) - 1
                if 0 <= n < len(config.records):
                    config.records.pop(n)
                continue
            except (ValueError, IndexError):
                continue

        if cmd.startswith("u "):
            try:
                n = int(cmd.split()[1]) - 1
                if 0 <= n < len(config.records):
                    record = config.records[n]
                    zone_name = _get_zone_name(record.zone_id)

                    _clear_screen()
                    _breadcrumb("EDIT", zone_name=zone_name, record_name=record.name)

                    source = _config_source_page(input_func, current_source=record.source)

                    _clear_screen()
                    _breadcrumb("EDIT", zone_name=zone_name, record_name=record.name)

                    proxied, ttl = _config_proxied_ttl_page(
                        input_func,
                        current_proxied=record.proxied,
                        current_ttl=record.ttl,
                    )

                    config.records[n] = RecordConfig(
                        zone_id=record.zone_id,
                        name=record.name,
                        source=source,
                        proxied=proxied,
                        ttl=ttl,
                    )
                continue
            except (ValueError, IndexError):
                continue


def main(
    *,
    config_path: Path | None = None,
    new_handler: Callable[..., None] = new,
    edit_handler: Callable[..., None] = edit,
) -> None:
    print("config:", config_path)
    if config_exists(config_path):
        edit_handler(config_path=config_path)
        return

    new_handler(config_path=config_path)
