#!/usr/bin/env python3
"""Rename files in a directory to random names, with undo and mixed naming."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import random
import string
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

__version__ = "2.0.0"

ORIGINAL_NAMES = ".original_names.json"
MAPPING_VERSION = 1
MIN_NAME_SIZE = 4
ACTIONS = frozenset("rum")
FORMATS = frozenset("nal")


def configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def alphabet_for_format(fmt: str) -> str:
    if fmt == "l":
        return string.ascii_letters
    if fmt == "n":
        return string.digits
    return string.ascii_letters + string.digits


def file_hash(path: Path, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def compute_name_size(count: int, fmt: str) -> int:
    if count <= 0:
        return MIN_NAME_SIZE
    alphabet_size = len(alphabet_for_format(fmt))
    needed = count * 100
    size = MIN_NAME_SIZE
    while alphabet_size**size < needed:
        size += 1
    return size


def random_names(count: int, name_size: int, fmt: str) -> list[str]:
    """Generate unique random name stems of fixed length."""
    alphabet = alphabet_for_format(fmt)
    max_unique = len(alphabet) ** name_size
    if count > max_unique:
        raise ValueError(
            f"Cannot generate {count} unique {fmt!r} names of length {name_size}; "
            f"maximum is {max_unique}."
        )

    generated: set[str] = set()
    while len(generated) < count:
        generated.add("".join(random.choice(alphabet) for _ in range(name_size)))
    return list(generated)


def mapping_file_path(directory: Path) -> Path:
    return directory / ORIGINAL_NAMES


def normalize_mapping_entry(value: str) -> str:
    """Support legacy mappings that stored absolute paths."""
    return Path(value).name


def load_mapping(directory: Path) -> dict[str, str]:
    path = mapping_file_path(directory)
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "files" in data:
        raw = data["files"]
    else:
        raw = data
    return {key: normalize_mapping_entry(val) for key, val in raw.items()}


def save_mapping(directory: Path, files: dict[str, str]) -> None:
    payload = {"version": MAPPING_VERSION, "files": files}
    path = mapping_file_path(directory)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def script_path_if_inside(directory: Path) -> Path | None:
    try:
        resolved_script = Path(__file__).resolve()
        resolved_script.relative_to(directory.resolve())
        return resolved_script
    except ValueError:
        return None


def should_skip(path: Path, directory: Path, skip_script: Path | None) -> bool:
    if not path.is_file():
        return True
    if path.name == ORIGINAL_NAMES:
        return True
    if skip_script is not None and path.resolve() == skip_script.resolve():
        return True
    return False


def list_target_files(directory: Path) -> list[Path]:
    skip_script = script_path_if_inside(directory)
    return sorted(
        p
        for p in directory.iterdir()
        if not should_skip(p, directory, skip_script)
    )


def resolve_directory(path: Path) -> Path:
    directory = path.resolve()
    if not directory.is_dir():
        logger.error("%s is not a valid directory.", directory)
        sys.exit(3)
    return directory


def unique_target_name(
    directory: Path, stem: str, suffix: str, reserved: set[str]
) -> str:
    candidate = f"{stem}{suffix}" if suffix else stem
    if candidate not in reserved and not (directory / candidate).exists():
        reserved.add(candidate)
        return candidate

    counter = 1
    while True:
        candidate = f"{stem}_{counter}{suffix}" if suffix else f"{stem}_{counter}"
        if candidate not in reserved and not (directory / candidate).exists():
            reserved.add(candidate)
            return candidate
        counter += 1


def rename_files(directory: Path, fmt: str, *, dry_run: bool = False) -> None:
    directory = resolve_directory(directory)
    logger.info("Renaming files in %s with format %s", directory, fmt)

    if mapping_file_path(directory).exists():
        logger.error(
            "Mapping file %s already exists. Run undo (-u) before renaming again.",
            ORIGINAL_NAMES,
        )
        sys.exit(4)

    files = list_target_files(directory)
    if not files:
        logger.info("No files to rename in %s.", directory)
        return

    mapping = {file_hash(path): path.name for path in files}
    name_size = compute_name_size(len(files), fmt)
    stems = random_names(len(files), name_size, fmt)
    reserved = {p.name for p in directory.iterdir() if p.is_file()}

    if dry_run:
        planned_names: set[str] = set(reserved)
        for path, stem in zip(files, stems):
            target_name = unique_target_name(directory, stem, path.suffix, planned_names)
            logger.info("[dry-run] %s -> %s", path.name, target_name)
        return

    save_mapping(directory, mapping)
    reserved = {p.name for p in directory.iterdir() if p.is_file()}

    for path, stem in zip(files, stems):
        target_name = unique_target_name(directory, stem, path.suffix, reserved)
        target = directory / target_name
        path.rename(target)
        logger.info("%s -> %s", mapping[file_hash(target)], target_name)


def undo_rename(directory: Path, *, dry_run: bool = False) -> None:
    directory = resolve_directory(directory)
    logger.info("Restoring original names in %s", directory)

    mapping = load_mapping(directory)
    if not mapping:
        logger.error("No mapping file (%s) found in %s.", ORIGINAL_NAMES, directory)
        sys.exit(4)

    skip_script = script_path_if_inside(directory)
    restored = 0

    for path in sorted(directory.iterdir()):
        if should_skip(path, directory, skip_script):
            continue
        digest = file_hash(path)
        original_name = mapping.get(digest)
        if original_name is None:
            logger.warning("No mapping for %s (hash %s...).", path.name, digest[:12])
            continue
        if path.name == original_name:
            continue
        target = directory / original_name
        if target.exists() and target != path:
            logger.error(
                "Cannot restore %s to %s: target already exists.",
                path.name,
                original_name,
            )
            sys.exit(5)
        if dry_run:
            logger.info("[dry-run] %s -> %s", path.name, original_name)
        else:
            path.rename(target)
            logger.info("%s -> %s", path.name, original_name)
        restored += 1

    if restored == 0 and not dry_run:
        logger.info("No files needed restoring.")
        return

    if not dry_run:
        mapping_file_path(directory).unlink(missing_ok=True)
        logger.info("Removed %s.", ORIGINAL_NAMES)


def mix_naming(directory: Path, fmt: str, *, dry_run: bool = False) -> None:
    """Prepend a random token to each filename while preserving the original name."""
    directory = resolve_directory(directory)
    logger.info("Mix-renaming files in %s with format %s", directory, fmt)

    if mapping_file_path(directory).exists():
        logger.error(
            "Mapping file %s already exists. Run undo (-u) before mix-renaming again.",
            ORIGINAL_NAMES,
        )
        sys.exit(4)

    files = list_target_files(directory)
    if not files:
        logger.info("No files to mix-rename in %s.", directory)
        return

    mapping = {file_hash(path): path.name for path in files}
    name_size = max(MIN_NAME_SIZE, math.ceil(math.log10(max(len(files), 10))))
    stems = random_names(len(files), name_size, fmt)
    reserved = {p.name for p in directory.iterdir() if p.is_file()}

    for path, stem in zip(files, stems):
        mixed_stem = f"{stem}_{path.stem}"
        target_name = unique_target_name(directory, mixed_stem, path.suffix, reserved)
        if dry_run:
            logger.info("[dry-run] %s -> %s", path.name, target_name)
            continue
        path.rename(directory / target_name)
        logger.info("%s -> %s", mapping[file_hash(directory / target_name)], target_name)

    if not dry_run:
        save_mapping(directory, mapping)


def parse_action_format(flag_parts: list[str]) -> tuple[str, str]:
    action = "r"
    fmt = "a"
    for part in flag_parts:
        if not part.startswith("-"):
            raise ValueError(f"Invalid flag group: {part!r}")
        for char in part[1:]:
            if char in ACTIONS:
                action = char
            elif char in FORMATS:
                fmt = char
            else:
                raise ValueError(f"Unknown flag character: {char!r}")
    return action, fmt


def split_positional_args(argv: list[str]) -> tuple[Path, list[str]]:
    directory = Path(".")
    flag_parts: list[str] = []
    for arg in argv:
        if arg.startswith("-"):
            flag_parts.append(arg)
        else:
            directory = Path(arg)
    if not flag_parts:
        flag_parts = ["-ra"]
    return directory, flag_parts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rename files with random names and restore them later.",
        epilog="Examples: python main.py ../ -ra | python main.py -u --dry-run",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned renames without changing files.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, positional_and_flags = parser.parse_known_args(argv)
    configure_logging(args.debug)

    directory, flag_parts = split_positional_args(positional_and_flags)
    try:
        action, fmt = parse_action_format(flag_parts)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    directory = resolve_directory(directory)

    if action == "r":
        rename_files(directory, fmt, dry_run=args.dry_run)
    elif action == "u":
        undo_rename(directory, dry_run=args.dry_run)
    elif action == "m":
        mix_naming(directory, fmt, dry_run=args.dry_run)
    else:
        logger.error("Unknown action: %s", action)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
