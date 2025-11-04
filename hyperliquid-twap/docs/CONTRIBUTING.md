# Contributing to Hyperliquid TWAP Data Service

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192.svg)](https://www.postgresql.org)

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

**Version**: Production-Ready v2.0

---

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/hyperliquid-twap.git
   cd hyperliquid-twap
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Database**
   ```bash
   docker compose up -d db
   python -m src.db.init
   ```

## Code Style

This project uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **Type hints** for all function signatures

Before submitting:

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Run tests
pytest
```

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clear, concise commit messages
   - Add tests for new features
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   pytest -v
   black src/ tests/
   ruff check src/ tests/
   ```

4. **Submit PR**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use meaningful test names
- Include both unit and integration tests

Example test structure:

```python
def test_feature_name():
    """Clear description of what is being tested."""
    # Arrange
    # Act
    # Assert
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Include type hints in function signatures
- Provide examples for new API endpoints

## Questions?

- Open an issue for discussion
- Check existing documentation
- Review closed issues for similar questions

## Testing

See [../README.md#-testing](../README.md#-testing) for comprehensive testing guide including:
- Running tests with pytest
- Code coverage reports
- Test fixtures and sample data
- CI/CD integration

## Troubleshooting Development Issues

For common development issues, see [../README.md#-troubleshooting](../README.md#-troubleshooting).

Quick tips:
- Database connection issues: Check `DATABASE_URL` format
- Import errors: Ensure you're in project root
- Test failures: Run `python tests/create_sample_data.py` first

---

## See Also

- 📖 [Main Documentation](../README.md)
- 🚀 [Quick Start Guide](../QUICKSTART.md)
- 📚 [API Reference](API.md)
- 🔧 [Testing Guide](../README.md#-testing)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
