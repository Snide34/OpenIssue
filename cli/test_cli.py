#!/usr/bin/env python3
"""
Quick test script for OpenIssue CLI
"""
import subprocess
import sys
import json
from pathlib import Path

def test_cli_installation():
    """Test that CLI can be imported and run"""
    try:
        # Test import
        from openissue.cli import main
        print("✅ CLI module imports successfully")
        
        # Test version command
        result = subprocess.run([
            sys.executable, "-m", "openissue.cli", "version"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Version command works")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ Version command failed: {result.stderr}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_scan_command():
    """Test scan command on current directory"""
    try:
        # Create a test directory with a simple package.json
        test_dir = Path(__file__).parent / "test_project"
        test_dir.mkdir(exist_ok=True)
        
        # Create a simple package.json for testing
        package_json = test_dir / "package.json"
        package_json.write_text(json.dumps({
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "lodash": "4.17.20"  # Older version that might have vulnerabilities
            }
        }, indent=2))
        
        print(f"📁 Created test project in {test_dir}")
        
        # Run scan command
        result = subprocess.run([
            sys.executable, "-m", "openissue.cli", "scan", str(test_dir), "--json"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode in [0, 1]:  # 0 = no vulns, 1 = vulns found
            print("✅ Scan command executed successfully")
            
            # Try to parse JSON output
            try:
                scan_results = json.loads(result.stdout)
                total = scan_results.get("total", 0)
                print(f"   Found {total} vulnerabilities")
                
                if scan_results.get("severity_counts"):
                    for severity, count in scan_results["severity_counts"].items():
                        if count > 0:
                            print(f"   {severity}: {count}")
                
            except json.JSONDecodeError:
                print("⚠️  Could not parse JSON output, but command ran")
                print(f"   Output: {result.stdout[:200]}...")
        else:
            print(f"❌ Scan command failed: {result.stderr}")
            return False
        
        # Cleanup
        if package_json.exists():
            package_json.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ Scan test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing OpenIssue CLI...")
    print("=" * 50)
    
    tests = [
        ("CLI Installation", test_cli_installation),
        ("Scan Command", test_scan_command),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CLI is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)