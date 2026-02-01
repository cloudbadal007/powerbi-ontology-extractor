# Release Process

This document outlines the process for releasing new versions of PowerBI Ontology Extractor.

## Versioning

We use [Semantic Versioning](https://semver.org/) (SemVer):
- **Format**: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **MAJOR**: Breaking changes that are not backwards compatible
- **MINOR**: New features that are backwards compatible
- **PATCH**: Bug fixes that are backwards compatible

### Version Examples

- `0.1.0` → `0.1.1`: Bug fix (patch)
- `0.1.1` → `0.2.0`: New feature (minor)
- `0.2.0` → `1.0.0`: Breaking change (major)

### Pre-1.0.0 Versions

During the `0.x.x` phase:
- Minor versions may include breaking changes
- Patch versions are for bug fixes only
- Breaking changes should be clearly documented

## Release Checklist

### Pre-Release

Before creating a release, ensure:

- [ ] **All tests passing**: `pytest` runs successfully
- [ ] **Code quality checks pass**: `black`, `flake8`, `mypy`, `isort`
- [ ] **Test coverage maintained**: >85% coverage
- [ ] **Documentation updated**: README, API docs, guides
- [ ] **CHANGELOG.md updated**: All changes documented
- [ ] **Version bumped**: In `setup.py` and `powerbi_ontology/__init__.py`
- [ ] **GitHub milestone completed**: All issues closed or moved
- [ ] **Breaking changes documented**: Migration guide if needed
- [ ] **Dependencies reviewed**: Check for security updates
- [ ] **Examples tested**: All examples work with new version
- [ ] **CI/CD passing**: All GitHub Actions workflows pass

## Release Steps

### 1. Update Version

Update version in two places:

**In `setup.py`:**
```python
setup(
    name="powerbi-ontology-extractor",
    version="0.2.0",  # Update this
    ...
)
```

**In `powerbi_ontology/__init__.py`:**
```python
__version__ = "0.2.0"  # Update this
```

### 2. Update CHANGELOG.md

Add a new section at the top (after `[Unreleased]`):

```markdown
## [0.2.0] - 2025-02-15

### Added
- New feature X
- New feature Y

### Changed
- Improved performance for large .pbix files

### Fixed
- Bug fix Z
- Schema drift detection edge case

### Security
- Updated dependencies to address vulnerabilities
```

**Important**: 
- Use the current date
- Link to GitHub compare: `[0.2.0]: https://github.com/cloudbadal007/powerbi-ontology-extractor/compare/v0.1.0...v0.2.0`
- Move items from `[Unreleased]` to the new version

### 3. Commit Changes

```bash
# Stage all changes
git add setup.py powerbi_ontology/__init__.py CHANGELOG.md

# Commit with conventional commit message
git commit -m "chore: bump version to 0.2.0"

# Push to main branch
git push origin main
```

### 4. Create Git Tag

Create an annotated tag:

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release version 0.2.0

- Added feature X
- Added feature Y
- Fixed bug Z
- See CHANGELOG.md for full details"

# Push tag to remote
git push origin v0.2.0
```

**Tag naming**: Always use `v` prefix (e.g., `v0.2.0`)

### 5. GitHub Release (Automatic)

The GitHub Actions workflow (`.github/workflows/release.yml`) will automatically:

1. Detect the new tag
2. Build the package
3. Create a GitHub release
4. Attach build artifacts
5. Generate release notes

**Manual alternative** (if needed):
- Go to: https://github.com/cloudbadal007/powerbi-ontology-extractor/releases/new
- **Tag**: `v0.2.0`
- **Title**: `Release v0.2.0`
- **Description**: Copy from CHANGELOG.md for this version
- **Attach assets**: Built automatically by workflow

### 6. Publish to PyPI (Optional)

If publishing to PyPI:

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (requires PYPI_API_TOKEN secret)
twine upload dist/*
```

**Note**: PyPI publishing is configured in `.github/workflows/release.yml` but commented out. Uncomment and set `PYPI_API_TOKEN` secret to enable.

### 7. Announce Release

Share the release:

- [ ] **Medium Article**: Write blog post for major releases
- [ ] **Twitter/X**: Announce with link to release
- [ ] **LinkedIn**: Professional announcement
- [ ] **GitHub Discussions**: Post in announcements category
- [ ] **Relevant Communities**: Reddit, Discord, etc. (if applicable)

**Example announcement**:
```markdown
🚀 PowerBI Ontology Extractor v0.2.0 is now available!

✨ New features:
- Feature X
- Feature Y

🐛 Bug fixes:
- Fixed bug Z

📦 Install: pip install powerbi-ontology-extractor==0.2.0

🔗 Release notes: [link]
```

## Post-Release

After the release:

- [ ] **Monitor GitHub Issues**: Watch for new issues related to release
- [ ] **Update Documentation Site**: If you have a docs site
- [ ] **Close GitHub Milestone**: Mark milestone as completed
- [ ] **Thank Contributors**: Acknowledge contributors in release notes
- [ ] **Update Examples**: Ensure examples work with new version
- [ ] **Monitor Downloads**: Track package downloads (PyPI stats)
- [ ] **Gather Feedback**: Collect user feedback

## Hotfix Process

For critical bugs in production that need immediate fixes:

### Steps

1. **Create hotfix branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/0.1.1
   ```

2. **Fix the bug**:
   - Write test first (if possible)
   - Fix the issue
   - Add test coverage
   - Update CHANGELOG.md

3. **Bump PATCH version**:
   - Update `setup.py` and `__init__.py`
   - Update CHANGELOG.md

4. **Test thoroughly**:
   ```bash
   pytest
   pytest tests/test_affected_module.py
   ```

5. **Commit and tag**:
   ```bash
   git commit -m "fix: critical bug in schema drift detection"
   git tag -a v0.1.1 -m "Hotfix v0.1.1: Fix critical schema drift bug"
   git push origin hotfix/0.1.1
   git push origin v0.1.1
   ```

6. **Create release**: Follow normal release process

7. **Merge back**:
   ```bash
   git checkout main
   git merge hotfix/0.1.1
   git push origin main
   
   git checkout develop
   git merge hotfix/0.1.1
   git push origin develop
   ```

8. **Delete hotfix branch**:
   ```bash
   git branch -d hotfix/0.1.1
   git push origin --delete hotfix/0.1.1
   ```

## Release Communication

### Major Releases (1.0.0, 2.0.0, etc.)

- 📝 **Blog post**: Detailed Medium article
- 🐦 **Social media**: Twitter/X, LinkedIn
- 📧 **Email**: Newsletter (if applicable)
- 💬 **Communities**: Reddit, Discord, forums
- 📺 **Video**: Demo video (optional)

### Minor Releases (0.2.0, 0.3.0, etc.)

- 🐦 **Social media**: Twitter/X, LinkedIn
- 📝 **Release notes**: GitHub release notes
- 💬 **Communities**: Quick announcement

### Patch Releases (0.1.1, 0.1.2, etc.)

- 📝 **Release notes**: GitHub release notes only
- 🔔 **GitHub notification**: Automatic for watchers

## Release Schedule

We don't have a fixed release schedule, but aim for:

- **Major releases**: As needed (breaking changes)
- **Minor releases**: Every 1-3 months (new features)
- **Patch releases**: As needed (bug fixes, security)

## Rollback Procedure

If a release has critical issues:

1. **Identify the issue**: Document the problem
2. **Create hotfix**: Follow hotfix process
3. **Communicate**: Inform users about the issue and fix
4. **Update PyPI**: If published, yank the broken version:
   ```bash
   twine yank powerbi-ontology-extractor==0.2.0 --reason "Critical bug"
   ```

## Version History

Track major milestones:

- `0.1.0` - Initial release (2025-01-31)
- `0.0.1` - Project initialization (2025-01-15)

## Questions?

If you have questions about the release process:

- Open an issue with the `question` label
- Check existing [GitHub Discussions](https://github.com/cloudbadal007/powerbi-ontology-extractor/discussions)
- Contact maintainers

---

**Remember**: Quality over speed. It's better to delay a release than to release broken code! 🚀
