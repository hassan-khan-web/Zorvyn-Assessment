# CI/CD Pipeline Documentation

## Overview

This project includes a comprehensive CI/CD pipeline that automatically checks code quality and test coverage on every push and pull request. The pipeline ensures:

- ✅ **Code Quality Rating**: Rated on a scale of 0-10 using Pylint
- ✅ **Test Coverage**: Minimum 72% required coverage
- ✅ **Linting**: Automated style checks with Ruff
- ✅ **All Tests Passing**: 27 automated tests must pass

---

## 🚀 CI/CD Pipeline Workflow

### Triggered On:
- Push to `main` branch
- Pull requests to `main` branch

### Pipeline Steps:

1. **Code Quality Check (Pylint)**
   - Analyzes Python code quality
   - Produces a rating: `Your code has been rated at 8.77/10`
   - Threshold: 7.50/10 minimum
   - Fails if below threshold

2. **Linting Check (Ruff)**
   - Fast Python linter
   - Checks for style and common errors
   - Reports number of issues found

3. **Test Execution with Coverage**
   - Runs all 27 tests
   - Measures code coverage
   - Required minimum: 72%
   - Fails if below threshold

4. **Reporting**
   - Generates quality report
   - Posts results to PR comments (for PRs)
   - Publishes to job summary
   - Uploads artifacts for download

---

## 📊 Output Example

### GitHub PR Comment:
```
# 📊 Code Quality & Test Coverage Report

## 📈 Code Quality Rating
**Your code has been rated at 8.77/10**

- Previous run: 8.50/10
- Change: +0.27
- Threshold: 7.50/10 ✅

## 🧪 Test Coverage
**Required test coverage of 72% reached. Total coverage: 89.23%**

- Status: ✅ PASSED
- Target: 72%
- Current: 89.23%
- Difference: +17.23%

## 🔍 Linting Results
- Ruff issues found: 0
- Status: ✅ No issues

## ✅ CI/CD Pipeline Status
- Build: ✅ PASSED
- Tests: ✅ PASSED (89.23% coverage)
- Code Quality: ✅ PASSED (Rating: 8.77/10)
- Linting: ✅ PASSED
```

---

## 🛠️ Local Development Setup

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Code Quality Checks Locally

#### Run Pylint for code quality rating:
```bash
pylint app
```
Expected output includes:
```
...
Your code has been rated at 8.77/10 (previous run: 8.50/10, +0.27)
```

#### Run Ruff for linting:
```bash
ruff check .
ruff format .  # auto-format code
```

#### Run tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

This generates an HTML coverage report at `htmlcov/index.html`

#### Run all checks combined:
```bash
# Quick check
ruff check .

# Code quality
pylint app

# Tests with coverage
pytest --cov=app --cov-report=term-missing
```

### View Coverage Report Locally
```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 📋 Configuration Files

### `.pylintrc`
- Pylint configuration
- Sets code quality rules
- Minimum rating: 7.50/10
- Max line length: 120 characters

### `pyproject.toml`
- Centralized tool configuration
- Coverage settings (threshold: 72%)
- Ruff and Black formatting rules
- Pytest configuration

### `requirements-dev.txt`
- Development-only dependencies
- Includes testing, coverage, and linting tools
- Install with: `pip install -r requirements-dev.txt`

### `.github/workflows/ci.yml`
- GitHub Actions workflow
- Runs on push and PR
- Generates reports and comments on PRs

---

## ✅ Quality Thresholds

| Metric | Threshold | Status |
|--------|-----------|--------|
| Code Quality Rating | 7.50/10 | ✅ Must Pass |
| Test Coverage | 72% | ✅ Must Pass |
| All Tests | 27/27 | ✅ Must Pass |
| Linting Issues | 0 | ⚠️ Warnings OK |

---

## 🔧 Customizing Thresholds

### Change Code Quality Threshold:

Edit `.pylintrc`:
```ini
[MASTER]
# Current: 7.5
fail_under=7.5  # Change this value
```

Edit `.github/workflows/ci.yml`:
```yaml
- run: python -m pylint app --fail-under=7.5  # Change this value
```

### Change Coverage Threshold:

Edit `pyproject.toml`:
```toml
[tool.coverage.report]
fail_under = 72  # Change this value
```

Edit `.github/workflows/ci.yml`:
```yaml
if (( $(echo "$COVERAGE < 72" | bc -l) )); then  # Change this value
```

---

## 🐛 Troubleshooting

### Pipeline Fails: "Coverage below 72%"
1. Run tests locally: `pytest --cov=app --cov-report=term-missing`
2. Find uncovered lines
3. Add tests for those lines
4. Commit and push

### Pipeline Fails: "Code quality below 7.50"
1. Run pylint: `pylint app`
2. Fix the reported issues
3. Re-run: `pylint app` to verify
4. Commit and push

### Pipeline Fails: "Linting issues found"
1. Run ruff: `ruff check .`
2. Auto-fix: `ruff format .`
3. Commit and push

---

## 📈 Monitoring Quality Over Time

The CI/CD pipeline tracks:
- Code quality trend (rating change from previous run)
- Coverage trend (vs. target of 72%)
- Number of linting issues

### View Artifacts:
1. Go to GitHub Actions workflow run
2. Click "Summary"
3. Scroll to "Artifacts" section
4. Download coverage reports or quality reports

---

## 🔗 Quick Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 📝 Summary

The CI/CD pipeline ensures:
- ✅ Code quality is maintained above 7.50/10
- ✅ At least 72% test coverage
- ✅ All 27 tests pass
- ✅ No critical linting issues

Run quality checks locally before pushing to catch issues early!
