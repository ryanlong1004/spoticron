#!/usr/bin/env python3
"""
Test script to verify the export command fix works correctly.
This tests the main scenarios from issue #2.
"""

import subprocess
import tempfile
from pathlib import Path


def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, check=False)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"


def test_export_help():
    """Test that export help shows the new options."""
    print("Testing export help...")

    _, stdout, _ = run_command("python spoticron.py export --help")  # Check that help includes new options
    required_options = [
        "--format [json|csv]",
        "--output TEXT",
        "--data-type",
        "--days INTEGER",
    ]

    success = all(option in stdout for option in required_options)

    if success:
        print("✅ Export help shows all new options")
    else:
        print("❌ Export help missing some options")
        print(f"Output: {stdout}")

    return success


def test_export_with_no_args():
    """Test that export works with no arguments (main issue from #2)."""
    print("Testing export with no arguments...")

    code, stdout, stderr = run_command("python spoticron.py export")

    # Should either succeed with live data or fail with helpful message
    success = "Live data exported successfully!" in stdout or "No stored data found" in stdout

    if success:
        print("✅ Export with no args provides useful feedback")
    else:
        print("❌ Export with no args failed unexpectedly")
        print(f"Exit code: {code}")
        print(f"Output: {stdout}")
        print(f"Error: {stderr}")

    return success


def test_export_with_custom_output():
    """Test export with custom output filename."""
    print("Testing export with custom output...")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_export.json"

        _, stdout, _ = run_command(f"python spoticron.py export -o {output_file}")

        # Check if file was created or helpful error given
        success = (
            output_file.exists() or "Failed to collect fresh data" in stdout or "No active Spotify session" in stdout
        )

        if success:
            print("✅ Export with custom output works")
            if output_file.exists():
                print(f"   Created file: {output_file} ({output_file.stat().st_size} bytes)")
        else:
            print("❌ Export with custom output failed")
            print(f"Output: {stdout}")

        return success


def test_export_data_type_warnings():
    """Test that data type options show appropriate warnings."""
    print("Testing data type option warnings...")

    _, stdout, _ = run_command("python spoticron.py export -t listening-history")

    success = "not yet implemented" in stdout

    if success:
        print("✅ Data type filter shows appropriate warning")
    else:
        print("❌ Data type filter warning missing")
        print(f"Output: {stdout}")

    return success


def main():
    """Run all tests."""
    print("🧪 Testing export command fix (Issue #2)")
    print("=" * 50)

    tests = [
        test_export_help,
        test_export_with_no_args,
        test_export_with_custom_output,
        test_export_data_type_warnings,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Export command fix is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. The fix may need additional work.")
        return 1


if __name__ == "__main__":
    exit(main())
