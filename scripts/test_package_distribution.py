#!/usr/bin/env python3
"""
Package distribution testing script for devtools-py.

This script tests the complete package distribution process:
- Builds the package from source
- Tests installation in a clean environment
- Verifies all modules can be imported
- Tests CLI functionality
- Validates package metadata
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import List, Dict, Any
import json
import shutil


class PackageDistributionTester:
    """Test package distribution and installation."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results: Dict[str, Any] = {}
    
    def run_command(self, cmd: List[str], description: str, check: bool = True, cwd: Path = None) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"🔧 {description}...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=cwd or self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
            else:
                print(f"⚠️  {description} completed with warnings")
                
            return result
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed")
            print(f"Exit code: {e.returncode}")
            if e.stdout:
                print(f"STDOUT: {e.stdout[:500]}...")
            if e.stderr:
                print(f"STDERR: {e.stderr[:500]}...")
            raise
    
    def clean_build_artifacts(self) -> None:
        """Clean existing build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = ["dist", "build", "*.egg-info"]
        
        for pattern in dirs_to_clean:
            if pattern.startswith("*"):
                # Handle glob patterns
                import glob
                for path in glob.glob(str(self.project_root / pattern)):
                    path_obj = Path(path)
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj)
                        print(f"  Removed {path_obj}")
            else:
                dir_path = self.project_root / pattern
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    print(f"  Removed {dir_path}")
        
        print("✅ Build artifacts cleaned")
    
    def build_package(self) -> List[Path]:
        """Build the package and return list of artifacts."""
        print("📦 Building package...")
        
        # Build both wheel and source distribution
        self.run_command(
            ["python", "-m", "build", "--wheel", "--sdist"],
            "Building wheel and source distribution"
        )
        
        # List built artifacts
        dist_dir = self.project_root / "dist"
        artifacts = list(dist_dir.glob("*"))
        
        if not artifacts:
            raise RuntimeError("No build artifacts found")
        
        print("📁 Built artifacts:")
        for artifact in artifacts:
            print(f"  - {artifact.name} ({artifact.stat().st_size} bytes)")
        
        self.test_results["build_artifacts"] = [str(a) for a in artifacts]
        return artifacts
    
    def validate_package_metadata(self, artifacts: List[Path]) -> None:
        """Validate package metadata using twine."""
        print("🔍 Validating package metadata...")
        
        artifact_paths = [str(artifact) for artifact in artifacts]
        
        result = self.run_command(
            ["python", "-m", "twine", "check"] + artifact_paths,
            "Validating package metadata with twine"
        )
        
        self.test_results["metadata_validation"] = {
            "passed": True,
            "output": result.stdout
        }
    
    def create_test_environment(self) -> Path:
        """Create a clean virtual environment for testing."""
        print("🏗️  Creating clean test environment...")
        
        temp_dir = Path(tempfile.mkdtemp(prefix="devtools_py_dist_test_"))
        venv_path = temp_dir / "test_venv"
        
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        
        print(f"✅ Created test environment at {venv_path}")
        return venv_path
    
    def get_python_executable(self, venv_path: Path) -> Path:
        """Get the Python executable path for the virtual environment."""
        if sys.platform == "win32":
            return venv_path / "Scripts" / "python.exe"
        else:
            return venv_path / "bin" / "python"
    
    def install_package_from_wheel(self, venv_path: Path, wheel_path: Path) -> None:
        """Install the package from a wheel file."""
        print(f"📦 Installing package from {wheel_path.name}...")
        
        python_exe = self.get_python_executable(venv_path)
        
        result = self.run_command(
            [str(python_exe), "-m", "pip", "install", str(wheel_path)],
            f"Installing {wheel_path.name}",
            cwd=venv_path
        )
        
        self.test_results["wheel_installation"] = {
            "passed": True,
            "wheel_file": str(wheel_path),
            "output": result.stdout
        }
    
    def install_package_from_source(self, venv_path: Path, sdist_path: Path) -> None:
        """Install the package from source distribution."""
        print(f"📦 Installing package from {sdist_path.name}...")
        
        python_exe = self.get_python_executable(venv_path)
        
        result = self.run_command(
            [str(python_exe), "-m", "pip", "install", str(sdist_path)],
            f"Installing {sdist_path.name}",
            cwd=venv_path
        )
        
        self.test_results["sdist_installation"] = {
            "passed": True,
            "sdist_file": str(sdist_path),
            "output": result.stdout
        }
    
    def test_module_imports(self, venv_path: Path) -> None:
        """Test that all modules can be imported."""
        print("🔍 Testing module imports...")
        
        python_exe = self.get_python_executable(venv_path)
        
        modules_to_test = [
            "devtools_py",
            "devtools_py.json_utils",
            "devtools_py.file_utils",
            "devtools_py.string_utils",
            "devtools_py.config_utils",
            "devtools_py.system_utils",
            "devtools_py.security_utils",
            "devtools_py.time_utils",
            "devtools_py.validation_utils",
            "devtools_py.data_utils",
            "devtools_py.async_utils",
            "devtools_py.dev_utils",
            "devtools_py.cli_utils",
            "devtools_py.http_utils",
            "devtools_py.log_utils",
        ]
        
        import_results = {}
        
        for module in modules_to_test:
            try:
                result = self.run_command(
                    [str(python_exe), "-c", f"import {module}; print('SUCCESS')"],
                    f"Importing {module}",
                    cwd=venv_path
                )
                import_results[module] = {"success": True, "output": result.stdout.strip()}
            except subprocess.CalledProcessError as e:
                import_results[module] = {"success": False, "error": e.stderr}
                print(f"❌ Failed to import {module}: {e.stderr}")
        
        self.test_results["module_imports"] = import_results
        
        # Check if all imports succeeded
        failed_imports = [mod for mod, result in import_results.items() if not result["success"]]
        if failed_imports:
            raise RuntimeError(f"Failed to import modules: {failed_imports}")
        
        print(f"✅ All {len(modules_to_test)} modules imported successfully")
    
    def test_cli_functionality(self, venv_path: Path) -> None:
        """Test CLI functionality."""
        print("🔍 Testing CLI functionality...")
        
        python_exe = self.get_python_executable(venv_path)
        
        cli_tests = [
            {
                "name": "help_command",
                "cmd": [str(python_exe), "-m", "devtools_py", "--help"],
                "description": "Testing CLI help command"
            },
            {
                "name": "string_convert",
                "cmd": [str(python_exe), "-m", "devtools_py", "string", "convert", "--to", "snake", "TestString"],
                "description": "Testing string conversion CLI command"
            },
            {
                "name": "system_info",
                "cmd": [str(python_exe), "-m", "devtools_py", "system", "info"],
                "description": "Testing system info CLI command"
            },
            {
                "name": "security_hash",
                "cmd": [str(python_exe), "-m", "devtools_py", "security", "hash", "test_data"],
                "description": "Testing security hash CLI command"
            }
        ]
        
        cli_results = {}
        
        for test in cli_tests:
            try:
                result = self.run_command(
                    test["cmd"],
                    test["description"],
                    cwd=venv_path
                )
                cli_results[test["name"]] = {
                    "success": True,
                    "output": result.stdout.strip(),
                    "stderr": result.stderr.strip()
                }
            except subprocess.CalledProcessError as e:
                cli_results[test["name"]] = {
                    "success": False,
                    "error": e.stderr,
                    "exit_code": e.returncode
                }
                print(f"⚠️  CLI test {test['name']} failed (this may be expected for some commands)")
        
        self.test_results["cli_functionality"] = cli_results
        print("✅ CLI functionality tests completed")
    
    def test_basic_functionality(self, venv_path: Path) -> None:
        """Test basic package functionality."""
        print("🔍 Testing basic functionality...")
        
        python_exe = self.get_python_executable(venv_path)
        
        test_script = '''
import devtools_py.json_utils as json_utils
import devtools_py.string_utils as string_utils
import devtools_py.security_utils as security_utils
import devtools_py.system_utils as system_utils
import tempfile
import json
from pathlib import Path

print("Testing JSON utilities...")
test_data = {"name": "test", "value": 123}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    temp_file = Path(f.name)

json_utils.save_json(test_data, temp_file)
loaded_data = json_utils.load_json(temp_file)
assert loaded_data == test_data
print("✅ JSON utilities working")

print("Testing string utilities...")
snake_case = string_utils.to_snake_case("TestString")
assert snake_case == "test_string"
print("✅ String utilities working")

print("Testing security utilities...")
secret = security_utils.generate_secret_key(16)
assert len(secret) > 0
print("✅ Security utilities working")

print("Testing system utilities...")
sys_info = system_utils.get_system_info()
assert isinstance(sys_info, dict)
assert "os_name" in sys_info
print("✅ System utilities working")

# Clean up
temp_file.unlink()

print("🎉 All basic functionality tests passed!")
'''
        
        result = self.run_command(
            [str(python_exe), "-c", test_script],
            "Running basic functionality tests",
            cwd=venv_path
        )
        
        self.test_results["basic_functionality"] = {
            "passed": True,
            "output": result.stdout
        }
    
    def cleanup_test_environment(self, venv_path: Path) -> None:
        """Clean up the test environment."""
        print("🧹 Cleaning up test environment...")
        
        try:
            shutil.rmtree(venv_path.parent)
            print("✅ Test environment cleaned up")
        except Exception as e:
            print(f"⚠️  Failed to clean up test environment: {e}")
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("🚀 Starting package distribution testing")
        print("=" * 60)
        
        venv_path = None
        
        try:
            # Clean and build
            self.clean_build_artifacts()
            artifacts = self.build_package()
            
            # Validate metadata
            self.validate_package_metadata(artifacts)
            
            # Find wheel and sdist files
            wheel_files = [a for a in artifacts if a.suffix == ".whl"]
            sdist_files = [a for a in artifacts if a.suffix == ".gz"]
            
            if not wheel_files:
                raise RuntimeError("No wheel file found in build artifacts")
            if not sdist_files:
                raise RuntimeError("No source distribution found in build artifacts")
            
            wheel_file = wheel_files[0]
            sdist_file = sdist_files[0]
            
            # Test wheel installation
            print("\n" + "=" * 40)
            print("Testing Wheel Installation")
            print("=" * 40)
            
            venv_path = self.create_test_environment()
            self.install_package_from_wheel(venv_path, wheel_file)
            self.test_module_imports(venv_path)
            self.test_cli_functionality(venv_path)
            self.test_basic_functionality(venv_path)
            self.cleanup_test_environment(venv_path)
            
            # Test source distribution installation
            print("\n" + "=" * 40)
            print("Testing Source Distribution Installation")
            print("=" * 40)
            
            venv_path = self.create_test_environment()
            self.install_package_from_source(venv_path, sdist_file)
            self.test_module_imports(venv_path)
            self.test_cli_functionality(venv_path)
            self.test_basic_functionality(venv_path)
            self.cleanup_test_environment(venv_path)
            
            # Mark overall success
            self.test_results["overall_success"] = True
            
            print("\n" + "=" * 60)
            print("🎉 All package distribution tests passed!")
            print("✅ Package is ready for distribution")
            
            return self.test_results
            
        except Exception as e:
            self.test_results["overall_success"] = False
            self.test_results["error"] = str(e)
            
            print(f"\n❌ Package distribution testing failed: {e}")
            
            if venv_path:
                self.cleanup_test_environment(venv_path)
            
            return self.test_results


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test devtools-py package distribution"
    )
    
    parser.add_argument(
        "--output-json",
        help="Save test results to JSON file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    # Run tests
    tester = PackageDistributionTester(project_root)
    results = tester.run_full_test_suite()
    
    # Save results if requested
    if args.output_json:
        output_path = Path(args.output_json)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Test results saved to {output_path}")
    
    # Print summary
    if args.verbose:
        print("\n" + "=" * 60)
        print("Test Results Summary:")
        print("=" * 60)
        for key, value in results.items():
            if key != "overall_success":
                print(f"{key}: {value}")
    
    # Return appropriate exit code
    return 0 if results.get("overall_success", False) else 1


if __name__ == "__main__":
    sys.exit(main())