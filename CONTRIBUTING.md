# Contributing to Metis

Thank you for your interest in contributing to Metis!

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](https://github.com/your-repo/metis/blob/main/CODE_OF_CONDUCT.md). Please report unacceptable behavior to maintainer@example.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Describe the behavior you observed vs. what you expected
- Include screenshots if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- Detailed description of the proposed feature
- Explain why this would be useful to most users
- List any alternative solutions you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Write a clear commit message
7. Push your changes to your fork
8. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/metis.git
cd metis

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/metis
```

## Code Style

We use:
- **Ruff** for linting
- **mypy** for type checking
- **Black** for formatting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/metis
```

## Project Structure

```
metis/
├── src/metis/          # Main source code
│   ├── cli/            # CLI interface
│   ├── fetchers/       # URL content fetching
│   ├── processors/     # Content processing
│   ├── storage/       # Obsidian storage
│   └── config/         # Configuration
├── tests/             # Test files
└── docs/              # Documentation
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` code style changes
- `refactor:` code refactoring
- `test:` test changes
- `chore:` maintenance

Example:
```
feat(fetcher): add WeChat public account support

- Add WeChat authentication setup command
- Implement Playwright-based content extraction
- Handle verification pages automatically
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
