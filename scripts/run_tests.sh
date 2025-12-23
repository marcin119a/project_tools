#!/bin/zsh

# Run tests with coverage
pytest --cov=./ --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=./ --cov-report=html

echo "Test and coverage report completed. Check the 'htmlcov' directory for the HTML report."
