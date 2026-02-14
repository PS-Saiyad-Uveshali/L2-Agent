"""Setup script for Level 3 Claude Agent SDK implementation."""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"  ✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e}")
        if e.stderr:
            print(f"  Error output: {e.stderr}")
        return False


def main():
    """Run the setup process."""
    print("=" * 60)
    print("L2 WIZARD - LEVEL 3 SETUP")
    print("=" * 60)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return 1
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(".venv"):
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return 1
    else:
        print("\n▶ Virtual environment already exists")
        print("  ✓ Skipping creation")
    
    # Determine activation command based on OS
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        print("  ⚠ Warning: pip upgrade failed, continuing anyway")
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return 1
    
    # Check for API key
    print("\n" + "=" * 60)
    print("CONFIGURATION CHECK")
    print("=" * 60)
    
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("\n✓ ANTHROPIC_API_KEY is set")
    else:
        print("\n⚠ ANTHROPIC_API_KEY is not set")
        print("\nTo use the agent, you need to set your Anthropic API key:")
        print("\nOn Windows (PowerShell):")
        print("  $env:ANTHROPIC_API_KEY='your-key-here'")
        print("\nOn Linux/Mac:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nGet your API key from: https://console.anthropic.com/")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"\n1. Activate the virtual environment:")
    print(f"   {activate_cmd}")
    print("\n2. Set your API key (if not already set)")
    print("\n3. Run the agent:")
    print(f"   {python_cmd} agent.py")
    print("\n4. Run tests:")
    print(f"   {python_cmd} test_agent.py")
    print("\n" + "=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
