# Argparse Interface Package Tester
# Used to test built packages by running the `argui` demo in a fresh environment.

# MARK: Imports
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# MARK: Functions
def run(cmd, cwd=None, env=None):
    print(f"Running: {cmd}")

    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)

def selectPackage(distDir) -> Path:
    pkgs = (list(distDir.glob("*.whl")) or list(distDir.glob("*.tar.gz")))
    pkgCount = len(pkgs)

    if pkgCount == 0:
        print("No built package found. Run `uv build`.")
        sys.exit(1)

    selected: Optional[int] = None
    while (selected is None) or (selected < 0) or (selected >= pkgCount):
        print("Available packages:")
        for i, pkg in enumerate(pkgs):
            print(f"\t[{i}] {pkg.name}")

        try:
            selected = int(input("\nSelect a package to test: "))
        except ValueError:
            selected = None

    return pkgs[selected]

def main():
    # Prepare paths
    root = Path(__file__).parent.resolve()
    distDir = root / "dist"
    testDir = root / "testEnv"

    # Build the package
    # run("uv build") # Do this manually?

    # Select a package
    package = selectPackage(distDir)

    # Prepare test directory
    if testDir.exists():
        shutil.rmtree(testDir)

    testDir.mkdir()

    # Copy built package
    packageDest = shutil.copy(package, testDir)

    # Create test.py
    testScript = testDir / "test.py"
    testScript.write_text("import argui\nargui.runDemo()\n")

    # Create virtual environment
    run("uv venv .venv", cwd=testDir)

    # Executables
    pythonExe = "python"
    pipExe = "pip"

    # # Find the built package
    # pkgs = list(testDir.glob("*.whl")) or list(testDir.glob("*.tar.gz"))
    # if not pkgs:
    #     print("No built package found in: ", testDir)
    #     sys.exit(1)

    # Install the package
    run(f'"{pipExe}" install "{packageDest}"', cwd=testDir)

    # Run test script
    run(f'"{pythonExe}" test.py --gui', cwd=testDir)

    # Report
    print("\n\n")
    print("="*69)
    print("If the demo ran successfully, the package works!")
    print("="*69)

    # Clean up
    shutil.rmtree(testDir)

# MARK: Execution
if __name__ == "__main__":
    main()
