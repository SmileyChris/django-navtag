#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "keyring",
# ]
# ///
"""Deploy package to PyPI."""

import argparse
import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd, shell=True, check=check, capture_output=capture_output, text=True
    )
    if capture_output:
        return result.stdout.strip()
    else:
        return result


def check_uv_installed():
    """Check if uv is installed."""
    if shutil.which("uv") is None:
        print("Error: 'uv' is not installed. Please install it first.")
        print("Visit: https://github.com/astral-sh/uv#installation")
        sys.exit(1)
    print("✓ uv is installed")


def ensure_uv_env_vars():
    """Ensure required UV environment variables are set."""
    required_vars = {
        "UV_KEYRING_PROVIDER": "subprocess",
        "UV_PUBLISH_USERNAME": "__token__",
    }

    vars_to_set = {}
    for var, value in required_vars.items():
        if os.environ.get(var) != value:
            vars_to_set[var] = value
            os.environ[var] = value

    if not vars_to_set:
        print("✓ UV environment variables already configured")
        return

    print("Setting UV environment variables for this session...")
    for var, value in vars_to_set.items():
        print(f"  {var}={value}")

    # Detect shell and update config file
    shell = os.environ.get("SHELL", "").split("/")[-1]
    home = Path.home()

    shell_configs = {
        "bash": home / ".bashrc",
        "zsh": home / ".zshrc",
        "fish": home / ".config/fish/config.fish",
    }

    config_file = shell_configs.get(shell)
    if not config_file or not config_file.exists():
        # Try to find which one exists
        for shell_name, path in shell_configs.items():
            if path.exists():
                config_file = path
                shell = shell_name
                break

    if config_file and config_file.exists():
        print(f"\nUpdating {config_file.name}...")

        with open(config_file, "r") as f:
            content = f.read()

        # Check if variables are already in the file
        lines_to_add = []
        for var, value in vars_to_set.items():
            if f"export {var}=" not in content:
                lines_to_add.append(f"export {var}={value}")

        if lines_to_add:
            with open(config_file, "a") as f:
                f.write("\n# UV configuration for PyPI publishing\n")
                for line in lines_to_add:
                    f.write(f"{line}\n")
            print(f"✓ Added UV environment variables to {config_file.name}")
            print(
                f"  Note: Restart your shell or run 'source {config_file}' to apply changes"
            )
        else:
            print(f"✓ UV environment variables already in {config_file.name}")
    else:
        print("\n⚠️  Could not detect shell configuration file")
        print("Please manually add these to your shell configuration:")
        for var, value in vars_to_set.items():
            print(f"  export {var}={value}")


def ensure_keyring():
    """Ensure keyring is installed and configured."""
    # keyring will be automatically installed by uv due to script dependencies
    import keyring

    # Check if token is already in keyring
    try:
        existing_token = keyring.get_password(
            "https://upload.pypi.org/legacy/", "__token__"
        )
        if existing_token:
            print("✓ PyPI token already configured in keyring")
            return
    except Exception:
        pass

    # Try to get token from .pypirc
    pypirc_path = Path.home() / ".pypirc"
    token = None

    if pypirc_path.exists():
        config = configparser.ConfigParser()
        config.read(pypirc_path)

        # Try to find token in various sections
        for section in ["pypi", "pypirc"]:
            if section in config:
                if "password" in config[section]:
                    password = config[section]["password"]
                    if password.startswith("pypi-"):
                        token = password
                        break

    if token:
        print("Found PyPI token in .pypirc, adding to keyring...")
        run_command(
            f"keyring set 'https://upload.pypi.org/legacy/' __token__ <<< '{token}'",
            shell=True,
        )
        print("✓ PyPI token configured in keyring")
    else:
        print("\nNo PyPI token found in .pypirc")
        print("Please manually set your token with:")
        print("  keyring set 'https://upload.pypi.org/legacy/' __token__")
        print("\nYou can find your token at: https://pypi.org/manage/account/token/")
        sys.exit(1)


def check_git_status():
    """Ensure git working directory is clean."""
    status = run_command("git status --porcelain", capture_output=True)
    if status:
        print("\nError: Git working directory is not clean!")
        print("Please commit or stash your changes first.")
        print("\nUncommitted changes:")
        print(status)
        sys.exit(1)
    print("✓ Git working directory is clean")


def run_tests():
    """Run full test suite with tox in parallel."""
    print("\nRunning tests with tox (parallel)...")
    result = run_command("uv run tox -p auto", check=False)
    if result.returncode != 0:
        print("\nError: Tests failed!")
        sys.exit(1)
    print("✓ All tests passed")


def get_current_version():
    """Get current version from pyproject.toml."""
    output = run_command("uv version --short", capture_output=True)
    return output.strip()


def determine_bump_type(current_version):
    """Ask user for version bump type."""
    print(f"\nCurrent version: {current_version}")

    try:
        if "dev" in current_version:
            print("\nThis is a development version.")
            choice = input("Release as stable version? [Y/n]: ").strip().lower()
            if choice in ["", "y", "yes"]:
                return "stable"

        # For both dev versions (if user said no) and stable versions
        print("\nSelect version bump type:")
        print("1. Major (X.0.0)")
        print("2. Minor (x.Y.0)")
        print("3. Patch (x.y.Z)")

        while True:
            choice = input("Enter choice [1-3]: ").strip()
            if choice == "1":
                return "major"
            elif choice == "2":
                return "minor"
            elif choice == "3":
                return "patch"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    except KeyboardInterrupt:
        return None


def bump_version(bump_type):
    """Bump version using uv."""
    print(f"Bumping {bump_type} version...")
    run_command(f"uv version --bump {bump_type}")

    new_version = get_current_version()
    print(f"✓ Version bumped to: {new_version}")
    return new_version


def commit_version(version):
    """Commit version bump."""
    print("\nCommitting version bump...")
    run_command("git add pyproject.toml")
    run_command(f'git commit -m "Bump version to {version}"')
    print("✓ Version bump committed")


def build_package():
    """Build the package."""
    print("\nBuilding package...")
    # Clean up old builds
    run_command("rm -rf dist/ build/ *.egg-info", check=False)
    result = run_command("uv build --no-build-logs", check=False)
    if result.returncode != 0:
        print("\nError: Package build failed!")
        sys.exit(1)
    print("✓ Package built successfully")


def publish_package():
    """Publish package to PyPI."""
    print("\n" + "=" * 60)
    print("READY TO PUBLISH TO PYPI")
    print("=" * 60)

    # Show what will be uploaded
    dist_files = sorted(Path("dist").glob("*"))
    print("\nFiles to be uploaded:")
    for f in dist_files:
        if f.is_file() and f.name not in [".gitignore", ".DS_Store"]:
            print(f"  - {f.name}")

    print("\nThis will upload the package to PyPI (production)!")
    confirm = input("Are you sure you want to continue? [y/N]: ").strip().lower()

    if confirm != "y":
        print("\nPublish cancelled.")
        return False

    print("\nPublishing to PyPI...")
    run_command("uv publish")
    print("\n✓ Package published successfully!")
    return True


def create_git_tag(version):
    """Create and push git tag."""
    tag_name = f"v{version}"
    print(f"\nCreating git tag {tag_name}...")
    run_command(f"git tag -s {tag_name} -m 'Release version {version}'")
    print(f"✓ Git tag {tag_name} created")

    # Get current branch name
    current_branch = run_command("git branch --show-current", capture_output=True)

    push_tag = (
        input(
            f"\nPush branch '{current_branch}' and tag '{tag_name}' to origin? [Y/n]: "
        )
        .strip()
        .lower()
    )
    if push_tag in ["", "y", "yes"]:
        print("Pushing branch and tag to origin...")
        run_command(f"git push origin {current_branch} {tag_name}")
        print(f"✓ Branch '{current_branch}' and tag '{tag_name}' pushed to origin")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy package to PyPI")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["tag", "bump"],
        help="Command to run (e.g., 'tag', 'bump')",
    )
    parser.add_argument("--version", help="Version to tag (for 'tag' command)")
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch", "stable"],
        help="Version bump type (for 'bump' command)",
    )
    args = parser.parse_args()

    # Change to project directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Handle tag command
    if args.command == "tag":
        check_uv_installed()
        check_git_status()
        version = args.version or get_current_version()
        create_git_tag(version)
        print(f"\n✅ Tag v{version} created successfully!")
        return

    # Handle bump command
    if args.command == "bump":
        check_uv_installed()
        check_git_status()
        current_version = get_current_version()

        if args.type:
            bump_type = args.type
        else:
            bump_type = determine_bump_type(current_version)
            if bump_type is None:
                print("\nBump cancelled.")
                return

        new_version = bump_version(bump_type)
        commit_version(new_version)
        print(f"\n✅ Version bumped to {new_version} and committed!")
        return

    # Full deployment flow
    check_uv_installed()
    ensure_uv_env_vars()
    ensure_keyring()
    check_git_status()
    run_tests()

    current_version = get_current_version()
    bump_type = determine_bump_type(current_version)

    if bump_type is None:
        print("\nDeployment cancelled.")
        return

    new_version = bump_version(bump_type)
    commit_version(new_version)
    build_package()

    if publish_package():
        create_git_tag(new_version)
        print("\n✅ Deployment completed successfully!")
    else:
        print("\n⚠️  Package built but not published.")
        print("You can manually publish later with: uv publish")


if __name__ == "__main__":
    main()
