# GitHub Actions Workflows

This project include three workflows de GitHub Actions for CI, Docker build, and CodeQL security analysis. Below is a detailed description of each workflow, their triggers, steps, and how to view results.

## Workflows Overview

### 1. CI Workflow (`ci.yml`)

**Purpose**: Run automated tests and code validation on every push or pull request.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`

**Steps**:
1. **Checkout code**: Downloads the repository code
2. **Python setup**: Installs Python 3.11 and 3.12 (version matrix)
3. **Install dependencies**: Installs dependencies from `requirements.txt`
4. **Install development tools**: Installs flake8 and pylint
5. **flake8 analysis**: 
   - Checks for critical syntax errors
   - Generates code quality statistics
6. **Import tests**: Verifies that main modules can be imported correctly
7. **Execution tests**: Runs the program with `--help` and `status` to verify basic functionality

**Badges**: 
```markdown
[![CI](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/ci.yml)
```

### 2. Docker Build Workflow (`docker.yml`)

**Purpose**: Build and verify the project's Docker image.

**Triggers**:
- Push to `main` or `develop` branches
- Push of tags with format `v*` (e.g., v1.0.0)
- Pull requests targeting `main` or `develop`

**Steps**:
1. **Checkout code**: Downloads the repository code
2. **Setup Docker Buildx**: Configures the Docker build environment
3. **Build Docker image**: Builds the image using the Dockerfile
4. **Test Docker image**: 
   - Verifies Python version
   - Lists installed packages

**Features**:
- Uses GitHub Actions cache to speed up builds
- Does not push the image to any registry (can be configured for releases)

**Badges**: 
```markdown
[![Docker Build](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/docker.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/docker.yml)
```

### 3. CodeQL Security Analysis (`codeql.yml`)

**Purpose**: Automated security analysis of Python code.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Every Monday at 00:00 UTC (scheduled)

**Steps**:
1. **Checkout repository**: Downloads the code
2. **Initialize CodeQL**: Configures analysis for Python
3. **CodeQL Analysis**: Scans code for vulnerabilities and quality issues

**Features**:
- Detects common security vulnerabilities
- Analyzes problematic code patterns
- Scheduled weekly execution for continuous monitoring
- Results appear in the repository's "Security" tab

**Required Permissions**:
- `actions: read`
- `contents: read`
- `security-events: write`

**Badges**: 
```markdown
[![CodeQL](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/codeql.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/codeql.yml)
```

## Additional Configuration

### Dependencies for CI
The CI workflow requires that `requirements.txt` is up to date with all project dependencies.

### Dockerfile
The Docker workflow uses the existing `Dockerfile` in the project root.

### pip Cache
Workflows use pip cache to speed up installations:
```yaml
cache: 'pip'
```

## View Results

Workflow results can be seen in:
1. The "Actions" tab of the repository
2. In each pull request (as checks)
3. The badges in the README.md

## Troubleshooting

### CI tests fail
- Verify that all dependencies are in `requirements.txt`
- Run locally: `pip install -r requirements.txt && python src/main.py --help`

### Docker build fails
- Verify that the Dockerfile is valid
- Build locally: `docker build -t ascii-generator .`

### CodeQL finds issues
- Check the "Security" tab → "Code scanning alerts"
- Review each alert and apply suggested fixes

## Maintenance

Update action versions periodically:
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `docker/build-push-action@v5`
- `github/codeql-action/*@v3`