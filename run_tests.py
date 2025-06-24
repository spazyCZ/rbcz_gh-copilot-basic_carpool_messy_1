#!/usr/bin/env python3
"""
Test runner script for the Parking Reservation System.
Provides an easy way to run different categories of tests.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description="Running command"):
    """Run a shell command and handle errors."""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed. Run: pip install -r requirements.txt")
        return False
    
    return True


def run_unit_tests(verbose=False):
    """Run unit tests."""
    cmd = ["pytest", "tests/test_app.py", "tests/test_utils.py"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running unit tests")


def run_integration_tests(verbose=False):
    """Run integration tests."""
    cmd = ["pytest", "tests/test_integration.py"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running integration tests")


def run_security_tests(verbose=False):
    """Run security tests."""
    cmd = ["pytest", "tests/test_security.py"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running security tests")


def run_performance_tests(verbose=False):
    """Run performance tests."""
    cmd = ["pytest", "tests/test_performance.py", "-m", "not slow"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running performance tests")


def run_all_tests(verbose=False):
    """Run all tests."""
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running all tests")


def run_tests_with_coverage(verbose=False):
    """Run tests with coverage report."""
    cmd = [
        "pytest", 
        "--cov=app", 
        "--cov=utils", 
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    if verbose:
        cmd.append("-v")
    return run_command(cmd, "Running tests with coverage")


def run_code_quality_checks():
    """Run code quality checks."""
    success = True
    
    # Flake8 linting
    success &= run_command(
        ["flake8", "app.py", "utils.py", "run.py", "config.py"],
        "Running flake8 linting"
    )
    
    # MyPy type checking
    success &= run_command(
        ["mypy", "app.py", "utils.py", "--ignore-missing-imports"],
        "Running mypy type checking"
    )
    
    return success


def run_security_checks():
    """Run security checks."""
    success = True
    
    # Bandit security linting
    success &= run_command(
        ["bandit", "-r", "app.py", "utils.py", "run.py"],
        "Running bandit security check"
    )
    
    # Safety vulnerability check
    success &= run_command(
        ["safety", "check"],
        "Running safety vulnerability check"
    )
    
    return success


def format_code():
    """Format code with black and isort."""
    success = True
    
    # Black formatting
    success &= run_command(
        ["black", "app.py", "utils.py", "run.py", "config.py", "tests/"],
        "Running black code formatting"
    )
    
    # Import sorting
    success &= run_command(
        ["isort", "app.py", "utils.py", "run.py", "config.py", "tests/"],
        "Running isort import sorting"
    )
    
    return success


def generate_reports():
    """Generate test and coverage reports."""
    success = True
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # HTML test report
    success &= run_command(
        ["pytest", "--html=reports/test_report.html", "--self-contained-html"],
        "Generating HTML test report"
    )
    
    # Coverage report
    success &= run_command(
        ["pytest", "--cov=app", "--cov=utils", "--cov-report=html:reports/coverage"],
        "Generating coverage report"
    )
    
    if success:
        print(f"\n📊 Reports generated in: {reports_dir.absolute()}")
        print(f"  - Test report: reports/test_report.html")
        print(f"  - Coverage report: reports/coverage/index.html")
    
    return success


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for Parking Reservation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit --verbose         # Run unit tests with verbose output
  python run_tests.py --coverage               # Run tests with coverage
  python run_tests.py --security               # Run security tests
  python run_tests.py --quality --format       # Check code quality and format
  python run_tests.py --ci                     # Run full CI pipeline
        """
    )
    
    # Test categories
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    
    # Code quality
    parser.add_argument("--quality", action="store_true", help="Run code quality checks")
    parser.add_argument("--security-check", action="store_true", help="Run security checks")
    parser.add_argument("--format", action="store_true", help="Format code")
    
    # Reports
    parser.add_argument("--reports", action="store_true", help="Generate reports")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--ci", action="store_true", help="Run full CI pipeline")
    
    args = parser.parse_args()
    
    # Check if dependencies are installed
    if not check_dependencies():
        sys.exit(1)
    
    success = True
    
    # If no specific test category is selected, show help
    if not any([args.all, args.unit, args.integration, args.security, 
                args.performance, args.coverage, args.quality, 
                args.security_check, args.format, args.reports, args.ci]):
        parser.print_help()
        return
    
    # Run CI pipeline
    if args.ci:
        print("🚀 Running full CI pipeline...")
        success &= run_code_quality_checks()
        success &= run_security_checks()
        success &= run_tests_with_coverage(args.verbose)
        success &= generate_reports()
    else:
        # Run individual test categories
        if args.unit:
            success &= run_unit_tests(args.verbose)
        
        if args.integration:
            success &= run_integration_tests(args.verbose)
        
        if args.security:
            success &= run_security_tests(args.verbose)
        
        if args.performance:
            success &= run_performance_tests(args.verbose)
        
        if args.all:
            success &= run_all_tests(args.verbose)
        
        if args.coverage:
            success &= run_tests_with_coverage(args.verbose)
        
        # Code quality checks
        if args.quality:
            success &= run_code_quality_checks()
        
        if args.security_check:
            success &= run_security_checks()
        
        if args.format:
            success &= format_code()
        
        if args.reports:
            success &= generate_reports()
    
    # Print summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 All operations completed successfully!")
    else:
        print("❌ Some operations failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
