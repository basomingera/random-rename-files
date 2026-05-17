# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2026-05-17

### Added

- Undo rename (`-u`) restores original filenames from `.original_names.json` using SHA-256 content hashes.
- Mix naming (`-m`) prepends a random token to each original filename (e.g. `a7Kx_song.mp3`).
- `--dry-run` to preview renames without modifying files.
- `--debug` for verbose logging.
- Versioned mapping file format (`version` + `files`); legacy absolute-path mappings still load.
- Test suite in `tests/test_main.py` (pytest).
- Collision handling when a generated name already exists (`_1`, `_2`, … suffix).
- Re-run protection: refuses rename/mix if a mapping file already exists.

### Changed

- Replaced string path concatenation with `pathlib.Path`.
- `random_names()` returns a deterministic `list` instead of an unordered `set`.
- Extension handling uses `Path.suffix` / `.stem` (fixes multi-dot and extensionless names).
- File hashing reads in 64 KiB chunks instead of loading entire files into memory.
- Name length scales with file count and alphabet size to reduce collisions.
- Skips `.original_names.json` and this script (only when the script lives in the target directory).
- CLI uses `argparse` with `parse_known_args` while keeping legacy flag style (`-ra`, `../ -ra`).
- README updated for current behavior, options, and mapping file format.

### Fixed

- `.original_names.json` was renamed along with other files (basename vs full-path comparison bug).
- `exit(0)` at module level caused imports to terminate the process.
- Empty directories caused `math.log(0, …)` to raise `ValueError`.
- Second rename without undo could corrupt the mapping and make restore impossible.
- `check_flag()` contained unreachable logic (`len < 0`).
- Directory validation did not require a directory (`isdir`).

### Removed

- Hardcoded skip of `main.py` in arbitrary directories.

## [1.0.0] - 2018

### Added

- Basic random rename with letter, number, and alphanumeric formats.
- Stub undo and mix-naming entry points.
- `.original_names.json` mapping file (hash → path).
