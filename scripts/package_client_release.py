#!/usr/bin/env python3
"""Package a native client executable and its setup guide."""
import argparse
import tarfile
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--platform", required=True)
    args = parser.parse_args()

    if not args.binary.is_file():
        parser.error(f"client executable not found: {args.binary}")

    repo_root = Path(__file__).resolve().parents[1]
    client_readme = repo_root / "client" / "README.md"
    setup_guide = repo_root / "docs" / "client-setup.md"
    license_file = repo_root / "LICENSE"
    dist_dir = args.binary.parent
    dist_dir.mkdir(parents=True, exist_ok=True)

    if args.platform.startswith("windows-"):
        output = dist_dir / f"middlemdm-client-{args.platform}.zip"
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(args.binary, args.binary.name)
            archive.write(client_readme, "README.md")
            archive.write(setup_guide, "SETUP.md")
            archive.write(license_file, "LICENSE")
            archive.write(repo_root / "client" / "install_service.bat", "install_service.bat")
    else:
        output = dist_dir / f"middlemdm-client-{args.platform}.tar.gz"
        with tarfile.open(output, "w:gz") as archive:
            archive.add(args.binary, args.binary.name)
            archive.add(client_readme, "README.md")
            archive.add(setup_guide, "SETUP.md")
            archive.add(license_file, "LICENSE")

    print(output)


if __name__ == "__main__":
    main()
