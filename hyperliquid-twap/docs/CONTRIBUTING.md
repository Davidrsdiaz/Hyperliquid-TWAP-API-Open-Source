# Contributing to Hyperliquid TWAP Data Service

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

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

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
