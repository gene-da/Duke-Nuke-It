#!/usr/bin/env python3
import os
import sys
from pathlib import Path

CHUNK_SIZE = 1024 * 1024  # 1 MiB chunks


def destroy_file(path: Path):
    """Overwrite the file with random data, flush it, then delete it."""
    if not path.is_file():
        return

    try:
        size = path.stat().st_size
    except OSError as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return

    # Overwrite contents with random bytes
    try:
        with open(path, "r+b", buffering=0) as f:
            remaining = size
            while remaining > 0:
                chunk = min(CHUNK_SIZE, remaining)
                f.write(os.urandom(chunk))
                remaining -= chunk
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[ERROR] Failed to overwrite {path}: {e}")

    # Delete the file
    try:
        path.unlink()
        print(f"[OK] Destroyed: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to delete {path}: {e}")


def destroy_directory(target: Path, recursive=True):
    """Destroy all files in the directory, then remove empty folders."""
    if not target.exists() or not target.is_dir():
        print(f"[ERROR] Not a valid directory: {target}")
        sys.exit(1)

    # Walk bottom-up so folders can be safely removed
    for root, dirs, files in os.walk(target, topdown=False):
        root_path = Path(root)

        # Wipe & delete each file
        for name in files:
            destroy_file(root_path / name)

        # Attempt to remove subdirectories
        for name in dirs:
            sub = root_path / name
            try:
                sub.rmdir()
            except OSError:
                pass

    # Remove the top-level directory itself
    try:
        target.rmdir()
        print(f"[OK] Removed directory: {target}")
    except OSError as e:
        print(f"[WARN] Could not remove {target}: {e}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()

    print("WARNING: This will corrupt, overwrite, delete all files in:")
    print(f"  {target}")
    print("Then remove the directory itself.")
    confirm = input("Type EXACTLY 'NUKE' to continue: ")

    if confirm != "NUKE":
        print("Aborted.")
        sys.exit(0)

    destroy_directory(target)
    print("Done. Directory obliterated.")


if __name__ == "__main__":
    main()
