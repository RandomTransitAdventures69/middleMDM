#!/usr/bin/env python3
"""Create a platform-labeled source installer bundle for the Flask server."""
import argparse
import re
import subprocess
import tarfile
from pathlib import Path


PACKAGE_FILES = (
    "LICENSE",
    "docs/server-package.md",
    "docs/server-setup.md",
    "docs/security.md",
)
PACKAGE_SCRIPTS = {
    "scripts/server-package-install.sh": "install.sh",
    "scripts/server-package-run.sh": "run.sh",
}


def tracked_server_files(repo_root):
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "server"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return [Path(path) for path in result.stdout.decode().split("\0") if path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", args.platform):
        parser.error("--platform may contain only lowercase letters, digits, and hyphens")

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f"middlemdm-server-{args.platform}"
    archive_path = output_dir / f"{archive_name}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as archive:
        for relative_path in tracked_server_files(repo_root):
            archive.add(
                repo_root / relative_path,
                arcname=f"{archive_name}/{relative_path.as_posix()}",
            )
        for relative_path in PACKAGE_FILES:
            archive.add(
                repo_root / relative_path,
                arcname=f"{archive_name}/" + (
                    "README.md" if relative_path == "docs/server-package.md" else relative_path
                ),
            )
        for source_path, archive_pathname in PACKAGE_SCRIPTS.items():
            source = repo_root / source_path
            info = archive.gettarinfo(str(source), arcname=f"{archive_name}/{archive_pathname}")
            info.mode = 0o755
            with source.open("rb") as source_file:
                archive.addfile(info, source_file)

    print(archive_path)


if __name__ == "__main__":
    main()
