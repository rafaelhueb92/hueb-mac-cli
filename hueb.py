#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class CleanupTarget:
    name: str
    path: Path
    enabled: bool = True


def run_command(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr.strip() or result.stdout.strip() or "command failed"
    return result.stdout.strip()


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def path_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file() or path.is_symlink():
        try:
            return path.lstat().st_size
        except OSError:
            return 0
    total = 0
    for root, _, files in os.walk(path, onerror=lambda _: None):
        root_path = Path(root)
        for name in files:
            fp = root_path / name
            try:
                total += fp.lstat().st_size
            except OSError:
                continue
    return total


def remove_path(path: Path) -> int:
    if not path.exists() and not path.is_symlink():
        return 0
    reclaimed = path_size(path)
    try:
        if path.is_symlink() or path.is_file():
            path.unlink(missing_ok=True)
        else:
            shutil.rmtree(path)
    except OSError:
        return 0
    return reclaimed


def default_cleanup_targets() -> List[CleanupTarget]:
    home = Path.home()
    return [
        CleanupTarget("user_cache", home / "Library" / "Caches"),
        CleanupTarget("user_logs", home / "Library" / "Logs"),
        CleanupTarget("trash", home / ".Trash"),
        CleanupTarget("xcode_derived_data", home / "Library" / "Developer" / "Xcode" / "DerivedData"),
    ]


def parse_targets(raw: str | None, all_targets: Iterable[CleanupTarget]) -> List[CleanupTarget]:
    targets = list(all_targets)
    if not raw:
        return targets
    selected = {item.strip() for item in raw.split(",") if item.strip()}
    unknown = sorted(selected.difference({t.name for t in targets}))
    if unknown:
        raise ValueError(f"Unknown targets: {', '.join(unknown)}")
    return [t for t in targets if t.name in selected]


def print_system_status() -> None:
    vm_stat = run_command(["vm_stat"])
    mem_line = run_command(["sysctl", "-n", "hw.memsize"])
    disk_usage = shutil.disk_usage(Path.home())
    uptime = run_command(["uptime"])
    top_cpu = run_command(["ps", "-Ao", "%cpu,%mem,comm", "-r"])

    print("Mac Performance Status")
    print("-" * 24)
    try:
        mem_total = int(mem_line)
        print(f"Total Memory: {format_bytes(mem_total)}")
    except ValueError:
        print(f"Total Memory: {mem_line}")

    print(f"Disk Free: {format_bytes(disk_usage.free)} / {format_bytes(disk_usage.total)}")
    print(f"Uptime: {uptime}")
    print("vm_stat:")
    print(vm_stat)
    print("Top CPU/MEM processes:")
    top_lines = top_cpu.splitlines()[:8]
    for line in top_lines:
        print(line)


def scan_cleanup(targets: List[CleanupTarget]) -> int:
    total = 0
    print("Cleanup Scan")
    print("-" * 12)
    for target in targets:
        size = path_size(target.path)
        total += size
        print(f"{target.name:20} {format_bytes(size):>12}  {target.path}")
    print("-" * 12)
    print(f"Potential reclaim: {format_bytes(total)}")
    return total


def execute_cleanup(targets: List[CleanupTarget], dry_run: bool) -> None:
    if dry_run:
        print("Dry-run mode enabled. No files will be removed.")
        scan_cleanup(targets)
        return

    reclaimed = 0
    print("Executing cleanup")
    print("-" * 16)
    for target in targets:
        size_before = path_size(target.path)
        removed = remove_path(target.path)
        reclaimed += removed
        if size_before == 0:
            status = "skipped"
        elif removed > 0:
            status = "removed"
        else:
            status = "failed"
        print(f"{target.name:20} {status:>8}  {format_bytes(removed):>12}")
    print("-" * 16)
    print(f"Total reclaimed: {format_bytes(reclaimed)}")


def find_named_folders(base_path: Path, names: set[str]) -> List[Path]:
    matches: List[Path] = []
    if not base_path.exists() or not base_path.is_dir():
        return matches
    for root, dirs, _ in os.walk(base_path, onerror=lambda _: None):
        root_path = Path(root)
        for dirname in list(dirs):
            if dirname in names:
                matches.append(root_path / dirname)
    return sorted(matches)


def ask_yes_no(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def clean_found_folders(base_path: Path, names: set[str], dry_run: bool) -> None:
    matches = find_named_folders(base_path, names)
    if not matches:
        print(f"No matching folders found in {base_path}")
        return

    print("Found folders")
    print("-" * 13)
    total = 0
    for folder in matches:
        size = path_size(folder)
        total += size
        print(f"{format_bytes(size):>12}  {folder}")
    print("-" * 13)
    print(f"Total size: {format_bytes(total)}")

    if dry_run:
        print("Dry-run mode enabled. No folders will be removed.")
        return

    reclaimed = 0
    for folder in matches:
        if ask_yes_no(f"Delete folder {folder}?"):
            removed = remove_path(folder)
            reclaimed += removed
            print(f"removed  {format_bytes(removed):>12}  {folder}")
        else:
            print(f"skipped               {folder}")
    print(f"Total reclaimed: {format_bytes(reclaimed)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hueb", description="Hueb Mac optimization CLI")
    root_