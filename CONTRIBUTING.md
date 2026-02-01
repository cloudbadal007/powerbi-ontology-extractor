# Contributing to PowerBI Ontology Extractor

Thank you for your interest in contributing! This project thrives on community contributions. Whether you're fixing bugs, adding features, improving documentation, or just asking questions, your contributions are welcome and appreciated.

## 🌟 Ways to Contribute

- 🐛 **Report Bugs**: Found a bug? [Open an issue](https://github.com/cloudbadal007/powerbi-ontology-extractor/issues/new?template=bug_report.md)
- 💡 **Suggest Features**: Have an idea? [Request a feature](https://github.com/cloudbadal007/powerbi-ontology-extractor/issues/new?template=feature_request.md)
- 📝 **Improve Documentation**: Fix typos, add examples, clarify explanations
- 🔧 **Submit Code**: Fix bugs, implement features, optimize performance
- ⭐ **Spread the Word**: Star the repo, share on social media, write blog posts
- 💬 **Answer Questions**: Help others in [Discussions](https://github.com/cloudbadal007/powerbi-ontology-extractor/discussions)
- 🧪 **Write Tests**: Improve test coverage, add edge cases
- 🌐 **Translate**: Help translate documentation to other languages

## 🚀 Getting Started

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/powerbi-ontology-extractor.git
cd powerbi-ontology-extractor

# Add upstream remote
git remote add upstream https://github.com/cloudbadal007/powerbi-ontology-extractor.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Or install manually
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### 3. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new branch for your work
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/improve-readme
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=powerbi_ontology --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_extractor.py

# Run specific test
pytest tests/test_extractor.py::TestPowerBIExtractor::test_extract_entities

# Run tests matching a pattern
pytest -k "dax"

# Run with verbose output
pytest -v

# Run only critical tests (e.g., $4.6M prevention)
pytest -m critical
```

**Coverage Requirements:**
- Overall coverage must be >85%
- Critical components (schema drift detection) must have 100% coverage
- New code should include tests

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black powerbi_ontology/ tests/ examples/

# Check code style with flake8
flake8 powerbi_ontology/ tests/

# Type checking with mypy
mypy powerbi_ontology/ --ignore-missing-imports

# Sort imports with isort
isort powerbi_ontology/ tests/ examples/

# Run all checks at once
pre-commit run --all-files
```

### Code Style Guidelines

- **Python**: Follow PEP 8
- **Line length**: 88 characters (black default)
- **Type hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for all public APIs
- **Imports**: Use isort for import sorting (group: stdlib, third-party, local)

**Example:**

```python
from typing import List, Optional

from powerbi_ontology.extractor import Entity, Property


def extract_entities(
    model: dict, 
    filter_type: Optional[str] = None
) -> List[Entity]:
    """Extract entities from Power BI semantic model.
    
    Args:
        model: The Power BI model dictionary containing tables
        filter_type: Optional filter for entity types (e.g., "dimension", "fact")
        
    Returns:
        List of extracted Entity objects
        
    Raises:
        ValueError: If model is invalid or missing required fields
        KeyError: If model structure is unexpected
        
    Example:
        >>> model = {"tables": [{"name": "Customer", "columns": []}]}
        >>> entities = extract_entities(model, filter_type="dimension")
        >>> len(entities)
        1
    """
    if not isinstance(model, dict):
        raise ValueError("Model must be a dictionary")
    
    # Implementation here
    pass
```

**Type Hints:**
- Always include return types
- Use `Optional[T]` for nullable values
- Use `List[T]`, `Dict[K, V]` from `typing` (Python <3.9) or built-in types (Python 3.9+)
- Use `Union[T, U]` for multiple possible types

**Docstrings:**
- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Add Examples for complex functions
- Document all public APIs

## 📝 Pull Request Process

### Before Submitting

- [ ] **Tests pass**: `pytest` runs without failures
- [ ] **Code is formatted**: `black` has been run
- [ ] **No linting errors**: `flake8` passes
- [ ] **Type hints added**: `mypy` passes (or errors are justified)
- [ ] **Documentation updated**: Docstrings, README, or docs updated as needed
- [ ] **CHANGELOG.md updated**: Added entry for your changes
- [ ] **Commit messages are clear**: Following conventional commits format
- [ ] **Branch is up to date**: Synced with upstream/main
- [ ] **No merge conflicts**: Resolved any conflicts

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**

```bash
feat(extractor): add support for Power BI version 2.0 models

Add detection and handling for newer Power BI schema versions.
Includes backward compatibility with version 1.0 models.

Closes #123
```

```bash
fix(schema_mapper): prevent $4.6M mistake with improved drift detection

Enhanced schema drift detection to catch column renames before
AI agents break. Adds heuristic matching for similar column names.

Fixes #456
```

```bash
docs(readme): add quick start example for Fabric IQ export

Improves onboarding experience with concrete example.
```

### Creating a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**:
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Title**: Use conventional commit format
   - Example: `feat(parser): add support for SWITCH statements`

4. **PR Description**: Include:
   - What changes you made and why
   - How to test the changes
   - Screenshots (if UI changes)
   - Related issues (use "Closes #123")

5. **Wait for Review**: 
   - Maintainers will review your PR
   - Address any feedback
   - Update PR as needed

### PR Review Process

1. **Automated Checks**: CI will run tests and checks
2. **Code Review**: At least one maintainer will review
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged

**What reviewers look for:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance considerations
- Backward compatibility
- Security implications

## 🎯 First-Time Contributors

### Good First Issues

Look for issues labeled:
- `good first issue` - Perfect for beginners
- `help wanted` - Community help needed
- `documentation` - Documentation improvements

### Getting Help

- **Questions?** Open a [Discussion](https://github.com/cloudbadal007/powerbi-ontology-extractor/discussions)
- **Stuck?** Ask in the issue or PR comments
- **Need clarification?** Don't hesitate to ask!

### Example First Contribution

Here's a simple example to get started:

1. **Find a typo** in the README
2. **Fork the repo**
3. **Create a branch**: `git checkout -b docs/fix-typo`
4. **Fix the typo**
5. **Commit**: `git commit -m "docs(readme): fix typo in installation section"`
6. **Push**: `git push origin docs/fix-typo`
7. **Open PR**

## 🧪 Testing Guidelines

### Writing Tests

- **Test all new features**: Every feature should have tests
- **Test edge cases**: Don't just test the happy path
- **Test error handling**: Verify errors are handled gracefully
- **Use descriptive names**: `test_extract_entities_with_missing_table` not `test1`

### Test Structure

```python
def test_feature_name_scenario():
    """Test description explaining what is being tested."""
    # Arrange: Set up test data
    extractor = PowerBIExtractor("test.pbix")
    
    # Act: Execute the code
    result = extractor.extract()
    
    # Assert: Verify the result
    assert result is not None
    assert len(result.entities) > 0
```

### Critical Tests

Some tests are marked as `critical` (e.g., the $4.6M prevention test):

```python
@pytest.mark.critical
def test_schema_drift_detection_prevents_4_6m_mistake():
    """Test that prevents the $4.6M logistics disaster."""
    # This test must always pass!
```

## 📚 Documentation Guidelines

### Code Documentation

- **Public APIs**: Must have docstrings
- **Complex logic**: Add inline comments explaining why
- **Examples**: Include usage examples in docstrings

### User Documentation

- **README.md**: Update for user-facing changes
- **docs/**: Add guides for new features
- **Examples**: Update examples/ directory

### Changelog

Update `CHANGELOG.md` with your changes:

```markdown
## [Unreleased]

### Added
- Support for Power BI version 2.0 models (#123)

### Fixed
- Schema drift detection now catches column renames (#456)
```

## 🔍 Code Review Checklist

Before requesting review, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] No hardcoded values or secrets
- [ ] Error messages are clear
- [ ] Logging is appropriate
- [ ] Performance is acceptable
- [ ] Backward compatibility maintained (if applicable)

## 🐛 Reporting Bugs

### Before Reporting

1. **Check existing issues**: Search for similar bugs
2. **Try latest version**: Update to the latest release
3. **Reproduce**: Ensure you can reproduce the bug

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Use file '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.10]
- Package version: [e.g., 0.1.0]

**Error message/logs**
```
Paste error here
```

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Use cases, examples, etc.
```

## 🤝 Community Guidelines

### Be Respectful

- Be kind and respectful to all contributors
- Welcome newcomers and help them learn
- Give constructive feedback
- Accept feedback gracefully

### Communication

- Use clear, concise language
- Be patient with questions
- Help others when you can
- Celebrate contributions!

## 📞 Getting Help

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bugs and feature requests
- **Email**: cloudpankaj@example.com
- **Twitter**: [@cloudpankaj](https://twitter.com/cloudpankaj)

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the project!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to PowerBI Ontology Extractor!** 🚀

Every contribution, no matter how small, makes a difference. We appreciate your time and effort!
