import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import main  # noqa: E402


@pytest.fixture
def work_dir(tmp_path):
    (tmp_path / "one.txt").write_text("first", encoding="utf-8")
    (tmp_path / "two.txt").write_text("second", encoding="utf-8")
    return tmp_path


def test_random_names_unique_and_ordered_length():
    names = main.random_names(5, 4, "a")
    assert len(names) == 5
    assert len(set(names)) == 5
    assert all(len(name) == 4 for name in names)


def test_compute_name_size_grows_with_count():
    small = main.compute_name_size(10, "a")
    large = main.compute_name_size(10_000, "a")
    assert large >= small


def test_file_hash_stable(work_dir):
    path = work_dir / "one.txt"
    assert main.file_hash(path) == main.file_hash(path)


def test_rename_and_undo_round_trip(work_dir):
    main.rename_files(work_dir, "a")
    assert not (work_dir / "one.txt").exists()
    assert (work_dir / main.ORIGINAL_NAMES).is_file()

    main.undo_rename(work_dir)
    assert (work_dir / "one.txt").is_file()
    assert (work_dir / "two.txt").is_file()
    assert not (work_dir / main.ORIGINAL_NAMES).exists()


def test_rename_refuses_if_mapping_exists(work_dir):
    main.rename_files(work_dir, "a")
    with pytest.raises(SystemExit) as exc:
        main.rename_files(work_dir, "a")
    assert exc.value.code == 4


def test_mix_naming_keeps_original_in_name(work_dir):
    main.mix_naming(work_dir, "l")
    names = {p.name for p in work_dir.iterdir() if p.is_file() and p.name != main.ORIGINAL_NAMES}
    assert any("one" in name for name in names)
    assert any("two" in name for name in names)


def test_load_mapping_legacy_absolute_paths(work_dir):
    legacy = {"abc123": str(work_dir / "song.mp3")}
    path = work_dir / main.ORIGINAL_NAMES
    path.write_text(json.dumps(legacy), encoding="utf-8")
    assert main.load_mapping(work_dir) == {"abc123": "song.mp3"}


def test_main_dry_run_leaves_files_unchanged(work_dir):
    assert main.main([str(work_dir), "-ra", "--dry-run"]) == 0
    assert (work_dir / "one.txt").exists()
    assert not (work_dir / main.ORIGINAL_NAMES).exists()


def test_empty_directory_exits_cleanly(tmp_path):
    assert main.main([str(tmp_path), "-ra"]) == 0
    assert not (tmp_path / main.ORIGINAL_NAMES).exists()
