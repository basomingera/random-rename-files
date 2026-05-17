# random-rename-files

This Python 3 script gives random names to files within a folder and writes a JSON mapping file so you can restore the original names later.

Imagine having a music car player without a random-play option: one way to deal with it is to give the files random names every time they are copied to a USB stick.

## Requirements

- Python 3.8+ (uses `pathlib` and modern type hints)
- No third-party dependencies

## Usage

```text
python src/main.py [directory] [-options] [--dry-run] [--debug]
```

Examples:

```text
python src/main.py ../ -ra
python src/main.py -u
python src/main.py . -m --dry-run
```

## Options

Options are two types: **actions** and **formats**. Combine them in one flag group (e.g. `-ra`, `-ul`).

### Actions (default: `r`)

| Flag | Description |
|------|-------------|
| `r` | Rename files to random names |
| `u` | Undo renaming using `.original_names.json` |
| `m` | Mix naming: prepend a random token to each original filename |

### Formats (default: `a`)

| Flag | Description |
|------|-------------|
| `n` | Numeric random names |
| `a` | Alphanumeric random names |
| `l` | Letters only |

### Extra flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Show planned renames without changing files |
| `--debug` | Verbose logging |

## Mapping file

Renaming and mix-naming create `.original_names.json` in the target directory. It stores a SHA-256 hash of each file’s contents mapped to its original basename, so undo works even after files are renamed.

Run undo (`-u`) before renaming again. A second rename without undo is rejected to avoid losing track of original names.

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Tests

```text
pip install pytest
pytest
```
