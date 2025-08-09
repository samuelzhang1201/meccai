#!/usr/bin/env python3
"""Setup script for development environment."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"📦 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up MeccaAI development environment\n")

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run from project root.")
        sys.exit(1)

    steps = [
        ("uv sync --dev", "Installing dependencies"),
        ("uv run pre-commit install", "Installing pre-commit hooks"),
        ("mkdir -p logs data", "Creating directories"),
        ("cp .env.example .env", "Creating environment file (if not exists)"),
    ]

    success_count = 0
    for cmd, desc in steps:
        if run_command(cmd, desc):
            success_count += 1
        print()

    print(f"✨ Setup completed! ({success_count}/{len(steps)} steps successful)")

    if success_count == len(steps):
        print("\n🎉 Development environment is ready!")
        print("📝 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. Run 'uv run pytest' to run tests")
        print("   3. Run 'uv run meccaai --chat' to start chatting")
    else:
        print("\n⚠️  Some setup steps failed. Please check the errors above.")


if __name__ == "__main__":
    main()
