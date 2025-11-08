#!/usr/bin/env python3
"""
Setup verification script for the Hate Speech Moderation System.

This script verifies that all components are properly configured
and ready for deployment.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path


def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True


def check_required_files():
    """Check that all required files are present."""
    required_files = [
        "src/main.py",
        "src/config/settings.py",
        "src/config/database.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        "README.md",
        ".env.example"
    ]

    print("\nChecking required files:")
    all_present = True

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False

    return all_present


def check_python_imports():
    """Check that critical Python modules can be imported."""
    print("\nChecking Python imports:")

    critical_modules = [
        ("src.config.settings", "Settings"),
        ("src.config.database", "Database manager"),
        ("src.models.user", "User models"),
        ("src.models.message", "Message models"),
        ("src.models.conversation", "Conversation models"),
        ("src.services.toxicity_detector", "Toxicity detector"),
        ("src.services.embedding_service", "Embedding service"),
        ("src.services.moderation_service", "Moderation service"),
        ("src.services.user_service", "User service"),
        ("src.main", "Main application")
    ]

    all_importable = True

    for module_name, description in critical_modules:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - NOT FOUND")
                all_importable = False
        except ImportError as e:
            print(f"❌ {description} - IMPORT ERROR: {e}")
            all_importable = False
        except Exception as e:
            print(f"⚠️ {description} - WARNING: {e}")

    return all_importable


def check_docker_files():
    """Check Docker configuration files."""
    print("\nChecking Docker configuration:")

    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.dev.yml"
    ]

    all_valid = True

    for docker_file in docker_files:
        if Path(docker_file).exists():
            print(f"✅ {docker_file}")
        else:
            print(f"❌ {docker_file} - MISSING")
            all_valid = False

    return all_valid


def check_database_scripts():
    """Check database initialization scripts."""
    print("\nChecking database scripts:")

    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("❌ scripts directory - MISSING")
        return False

    init_script = scripts_dir / "init-mongo.js"
    if init_script.exists():
        print("✅ MongoDB initialization script")
        return True
    else:
        print("❌ MongoDB initialization script - MISSING")
        return False


def check_monitoring():
    """Check monitoring configuration."""
    print("\nChecking monitoring configuration:")

    monitoring_dir = Path("monitoring")
    if not monitoring_dir.exists():
        print("❌ monitoring directory - MISSING")
        return False

    prometheus_config = monitoring_dir / "prometheus.yml"
    grafana_datasource = monitoring_dir / "grafana/datasources/prometheus.yml"

    monitoring_ok = True

    if prometheus_config.exists():
        print("✅ Prometheus configuration")
    else:
        print("❌ Prometheus configuration - MISSING")
        monitoring_ok = False

    if grafana_datasource.exists():
        print("✅ Grafana datasource configuration")
    else:
        print("❌ Grafana datasource configuration - MISSING")
        monitoring_ok = False

    return monitoring_ok


def check_tests():
    """Check test suite."""
    print("\nChecking test suite:")

    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ tests directory - MISSING")
        return False

    test_files = [
        "tests/conftest.py",
        "tests/unit/test_toxicity_detector.py",
        "tests/unit/test_embedding_service.py",
        "tests/integration/test_api_endpoints.py"
    ]

    tests_ok = True

    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} - MISSING")
            tests_ok = False

    return tests_ok


def check_documentation():
    """Check documentation."""
    print("\nChecking documentation:")

    doc_files = [
        "README.md",
        "examples/basic_usage.py"
    ]

    docs_ok = True

    for doc_file in doc_files:
        if Path(doc_file).exists():
            print(f"✅ {doc_file}")
        else:
            print(f"❌ {doc_file} - MISSING")
            docs_ok = False

    return docs_ok


def check_environment_file():
    """Check if .env file exists or needs to be created."""
    print("\nChecking environment configuration:")

    if Path(".env").exists():
        print("✅ .env file exists")
    else:
        print("⚠️ .env file - MISSING (copy from .env.example)")
        print("   Run: cp .env.example .env")


def run_syntax_check():
    """Run syntax check on all Python files."""
    print("\nRunning syntax check:")

    python_files = list(Path(".").rglob("*.py"))
    syntax_ok = True

    for py_file in python_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {py_file}")
            else:
                print(f"❌ {py_file} - SYNTAX ERROR")
                print(f"   {result.stderr}")
                syntax_ok = False
        except Exception as e:
            print(f"❌ {py_file} - ERROR: {e}")
            syntax_ok = False

    return syntax_ok


def main():
    """Run all verification checks."""
    print("🔍 Hate Speech Moderation System - Setup Verification")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_required_files),
        ("Python Imports", check_python_imports),
        ("Docker Configuration", check_docker_files),
        ("Database Scripts", check_database_scripts),
        ("Monitoring", check_monitoring),
        ("Test Suite", check_tests),
        ("Documentation", check_documentation),
        ("Syntax Check", run_syntax_check),
        ("Environment", check_environment_file)
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} - ERROR: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {check_name}")

    print(f"\nResults: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! The system is ready for deployment.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Run: docker-compose up -d")
        print("3. Verify with: curl http://localhost:8000/health")
        print("4. View API docs: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️ {total - passed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())