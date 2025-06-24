# Makefile for Parking Reservation System Testing

.PHONY: help install test test-unit test-integration test-security test-performance test-coverage test-report clean lint format check security

# Default target
help:
	@echo "Available targets:"
	@echo "  install           - Install dependencies"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-security     - Run security tests only"
	@echo "  test-performance  - Run performance tests only"
	@echo "  test-coverage     - Run tests with coverage report"
	@echo "  test-report       - Generate HTML test report"
	@echo "  lint              - Run code linting"
	@echo "  format            - Format code"
	@echo "  check             - Run all code quality checks"
	@echo "  security          - Run security checks"
	@echo "  clean             - Clean test artifacts"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	pytest

# Run specific test categories
test-unit:
	pytest tests/test_app.py tests/test_utils.py -m "not slow"

test-integration:
	pytest tests/test_integration.py

test-security:
	pytest tests/test_security.py

test-performance:
	pytest tests/test_performance.py -m "not slow"

# Run tests with coverage
test-coverage:
	pytest --cov=app --cov=utils --cov-report=html --cov-report=term

# Generate HTML test report
test-report:
	pytest --html=reports/test_report.html --self-contained-html

# Run tests in parallel (faster execution)
test-parallel:
	pytest -n auto

# Run only smoke tests (basic functionality)
test-smoke:
	pytest -m smoke

# Code quality checks
lint:
	flake8 app.py utils.py run.py config.py
	mypy app.py utils.py --ignore-missing-imports

format:
	black app.py utils.py run.py config.py tests/
	isort app.py utils.py run.py config.py tests/

check: lint
	@echo "Running code quality checks..."

# Security checks
security:
	bandit -r app.py utils.py run.py
	safety check

# Performance benchmarks
benchmark:
	pytest tests/test_performance.py --benchmark-only

# Clean artifacts
clean:
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -f .coverage
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Create reports directory
reports:
	mkdir -p reports

# Continuous integration target
ci: install lint security test-coverage

# Development setup
dev-setup: install
	@echo "Development environment setup complete"
	@echo "Run 'make test' to run all tests"
	@echo "Run 'make help' to see all available commands"
