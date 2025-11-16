# Test Commands Quick Reference

Quick reference for common test commands in the Songs-Gen project.

## Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with very verbose output (show all test names)
pytest -vv

# Run tests and stop on first failure
pytest -x

# Run tests with minimal output
pytest -q
```

## Coverage Commands

```bash
# Run tests with coverage report
pytest --cov=app

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Run by Test Type

```bash
# Unit tests only
pytest tests/unit
pytest -m unit

# Integration tests only
pytest tests/integration
pytest -m integration

# End-to-end tests only
pytest tests/e2e
pytest -m e2e

# All tests except slow ones
pytest -m "not slow"
```

## Run by Feature

```bash
# Authentication tests
pytest -m auth

# API tests
pytest -m api

# Database tests
pytest -m database

# Audio analysis tests
pytest -m audio

# Video generation tests
pytest -m video

# Service layer tests
pytest -m service
```

## Run Specific Files/Tests

```bash
# Run specific file
pytest tests/unit/test_auth.py

# Run specific class
pytest tests/unit/test_auth.py::TestPasswordHashing

# Run specific test
pytest tests/unit/test_auth.py::TestPasswordHashing::test_verify_password_success

# Run tests matching pattern
pytest -k "password"
pytest -k "auth and not logout"
```

## Parallel Execution

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run with 4 parallel workers
pytest -n 4

# Run with auto-detection of CPU cores
pytest -n auto
```

## Output Control

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Show summary of all test outcomes
pytest -ra

# Show only failures
pytest --tb=short

# Show full traceback
pytest --tb=long

# No traceback
pytest --tb=no
```

## Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on error
pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb

# Run last failed tests
pytest --lf

# Run last failed first, then others
pytest --ff

# Show which tests will run without executing
pytest --collect-only
```

## Watch Mode

```bash
# Install pytest-watch first
pip install pytest-watch

# Watch for changes and re-run tests
ptw

# Watch with clear screen
ptw --clear

# Watch with notifications
ptw --notify
```

## Combining Options

```bash
# Unit tests with coverage
pytest tests/unit --cov=app --cov-report=html

# Integration tests in parallel
pytest tests/integration -n 4

# Auth tests with verbose output
pytest -m auth -vv

# API tests excluding slow ones
pytest -m "api and not slow" -v

# All tests with coverage, stop on first failure
pytest --cov=app --cov-report=term-missing -x -v
```

## CI/CD Commands

```bash
# Full CI test suite
pytest --cov=app --cov-report=xml --cov-report=term -v

# Pre-commit check
pytest --cov=app --cov-report=term-missing -x

# Quality gate (must have 80% coverage)
pytest --cov=app --cov-fail-under=80
```

## Performance Profiling

```bash
# Install pytest-benchmark first
pip install pytest-benchmark

# Show slowest 10 tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Profile test execution
pytest --profile
```

## Useful Combinations

### Development Workflow

```bash
# Fast feedback loop (unit tests only, stop on first failure)
pytest tests/unit -x

# Before commit (all tests with coverage)
pytest --cov=app --cov-report=term-missing

# Full validation (parallel with coverage)
pytest -n 4 --cov=app --cov-report=html
```

### CI/CD Pipeline

```bash
# Stage 1: Fast unit tests
pytest tests/unit -v

# Stage 2: Integration tests
pytest tests/integration -v

# Stage 3: E2E tests
pytest tests/e2e -v

# Stage 4: Coverage report
pytest --cov=app --cov-report=xml --cov-fail-under=80
```

### Debugging Failed Tests

```bash
# Re-run only failed tests with debugger
pytest --lf --pdb

# Show local variables for failed test
pytest --lf -l -vv

# Verbose output with full traceback
pytest --lf -vv --tb=long
```

## Environment Variables

```bash
# Set test database URL
export TEST_DATABASE_URL="sqlite:///./test_custom.db"

# Run tests with custom environment
TEST_MODE=true pytest

# Disable warnings
PYTHONWARNINGS="ignore" pytest
```

## Test Data Management

```bash
# Clean test database
rm -f test.db

# Clean coverage data
rm -f .coverage
rm -rf htmlcov/

# Clean all test artifacts
rm -f test.db .coverage
rm -rf htmlcov/ .pytest_cache/

# Reset test environment
make clean-test  # If Makefile exists
```

## Common Workflows

### Quick Check (Before Commit)

```bash
pytest tests/unit -x -q
```

### Full Local Test

```bash
pytest --cov=app --cov-report=html -v
open htmlcov/index.html
```

### Debug Failing Test

```bash
pytest tests/unit/test_auth.py::test_failing_test -vv --pdb
```

### Test Specific Feature

```bash
# Test all authentication
pytest -m auth -v

# Test all API endpoints
pytest -m api -v

# Test complete pipeline
pytest tests/e2e/test_complete_pipeline.py -v
```

### Pre-Release Validation

```bash
# Run all tests in parallel with coverage
pytest -n 4 --cov=app --cov-report=html --cov-report=term-missing -v

# Check coverage threshold
pytest --cov=app --cov-fail-under=80

# Run only integration and e2e tests
pytest -m "integration or e2e" -v
```

## Troubleshooting Commands

### Fix Database Lock Issues

```bash
# Kill any running backend processes
pkill -f "uvicorn"

# Remove test database
rm -f test.db

# Re-run tests
pytest
```

### Fix Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/user/songs-gen/backend:$PYTHONPATH

# Or run from backend directory
cd /home/user/songs-gen/backend
pytest
```

### Clear Cache

```bash
# Clear pytest cache
pytest --cache-clear

# Remove __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove .pyc files
find . -type f -name "*.pyc" -delete
```

## Aliases (Add to .bashrc or .zshrc)

```bash
# Quick test aliases
alias pyt="pytest"
alias pyu="pytest tests/unit"
alias pyi="pytest tests/integration"
alias pye="pytest tests/e2e"
alias pytc="pytest --cov=app --cov-report=html"
alias pytv="pytest -vv"
alias pytf="pytest --lf"  # Run last failed
alias pytw="ptw"  # Watch mode
```

## Docker Commands

```bash
# Run tests in Docker container
docker-compose run backend pytest

# Run with coverage in Docker
docker-compose run backend pytest --cov=app --cov-report=html

# Run specific test in Docker
docker-compose run backend pytest tests/unit/test_auth.py

# Clean test database in Docker
docker-compose run backend rm -f test.db
```

---

**Pro Tips:**

1. Use `-x` to stop on first failure for fast feedback
2. Use `-vv` for maximum verbosity when debugging
3. Use `--lf` to re-run only failed tests
4. Use `-n auto` for parallel execution on multi-core systems
5. Use `--pdb` to drop into debugger on failures
6. Use `-k` to run tests matching a pattern
7. Use markers (`-m`) to run specific test categories
8. Use `--collect-only` to see which tests will run without executing them
9. Combine coverage with parallel execution: `pytest -n 4 --cov=app`
10. Use `pytest --durations=10` to find slow tests
