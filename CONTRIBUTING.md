# Contributing to Flowby

Thank you for your interest in contributing to Flowby! 🌸

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

---

## 📜 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/flowby.git
cd flowby

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

---

## 🔄 Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_lexer.py

# Run with coverage
pytest --cov=flowby --cov-report=html

# Run linter
flake8 src/flowby/
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add support for new feature"

# Follow conventional commits format:
# - feat: new feature
# - fix: bug fix
# - docs: documentation changes
# - test: adding or updating tests
# - refactor: code refactoring
# - chore: maintenance tasks
```

---

## 📏 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where applicable

```python
# Good
def parse_expression(self, tokens: List[Token]) -> Expression:
    """Parse an expression from the token stream."""
    ...

# Avoid
def parse_expression(self,tokens):
    ...
```

### Naming Conventions

- Classes: `PascalCase` (e.g., `LexerToken`, `ASTNode`)
- Functions/methods: `snake_case` (e.g., `parse_statement`, `get_next_token`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_DEPTH`, `DEFAULT_TIMEOUT`)
- Private members: prefix with `_` (e.g., `_internal_state`)

### Documentation

- Add docstrings to all public classes and methods
- Use Google-style docstrings

```python
def parse_function_definition(self) -> FunctionDefNode:
    """Parse a function definition statement.

    Args:
        None

    Returns:
        FunctionDefNode: AST node representing the function definition

    Raises:
        ParserError: If function syntax is invalid
    """
    ...
```

---

## 🧪 Testing Guidelines

### Test Structure

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Grammar tests: `tests/grammar_alignment/`

### Writing Tests

```python
import pytest
from flowby.lexer import Lexer

def test_lexer_tokenizes_identifier():
    """Test that lexer correctly tokenizes identifiers."""
    lexer = Lexer("let username = 'alice'")
    tokens = lexer.tokenize()

    assert tokens[0].type == "LET"
    assert tokens[1].type == "IDENTIFIER"
    assert tokens[1].value == "username"
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

---

## 📤 Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Update docs/ for new features
   - Add CHANGELOG.md entry

2. **Create Pull Request**
   - Push your branch to GitHub
   - Create PR against `main` branch
   - Fill out the PR template
   - Link related issues

3. **PR Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests
   - [ ] Updated documentation

   ## Related Issues
   Fixes #123
   ```

4. **Code Review**
   - Address reviewer feedback
   - Keep PR focused and small
   - Squash commits if requested

---

## 🏗️ Project Structure

```
flowby/
├── src/flowby/              # Core source code
│   ├── lexer.py             # Tokenization
│   ├── parser.py            # Parsing
│   ├── interpreter.py       # Execution
│   ├── ast_nodes.py         # AST definitions
│   └── ...
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── grammar_alignment/   # Grammar tests
├── examples/                # Example .flow scripts
├── docs/                    # Documentation
└── grammar/                 # Language specification
```

---

## 💡 Contribution Ideas

- **Bug Fixes**: Check [open issues](https://github.com/flowby/flowby/issues)
- **New Features**: See [feature requests](https://github.com/flowby/flowby/labels/enhancement)
- **Documentation**: Improve docs, add examples
- **Performance**: Optimize interpreter speed
- **Tooling**: IDE plugins, syntax highlighters

---

## 📞 Community

- **GitHub Discussions**: Ask questions, share ideas
- **Discord**: Real-time chat with contributors
- **Issues**: Report bugs, request features

---

## ✅ Checklist for Contributors

Before submitting your PR:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
- [ ] CHANGELOG.md updated

---

Thank you for contributing to Flowby! 🌸
