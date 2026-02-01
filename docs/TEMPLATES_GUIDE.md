# GitHub Templates Guide

This guide explains how to use the GitHub issue and pull request templates for PowerBI Ontology Extractor.

## 📋 Issue Templates

### Bug Report

**When to use**: Report bugs, unexpected behavior, or errors.

**Template**: `.github/ISSUE_TEMPLATE/bug_report.md`

**Includes**:
- Bug description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error logs section
- Sample files attachment

**Example scenarios**:
- Tool crashes when processing a .pbix file
- Incorrect ontology generation
- Schema drift not detected when it should be
- Export format validation fails

### Feature Request

**When to use**: Suggest new features or enhancements.

**Template**: `.github/ISSUE_TEMPLATE/feature_request.md`

**Includes**:
- Feature description
- Problem it solves
- Proposed solution
- Alternatives considered
- Use case
- Mockups/examples

**Example scenarios**:
- Add support for Power BI Service API
- New export format (e.g., GraphQL)
- Enhanced visualization options
- Performance improvements

### Question

**When to use**: Ask questions about usage, implementation, or concepts.

**Template**: `.github/ISSUE_TEMPLATE/question.md`

**Includes**:
- Question
- Context
- What you've tried checklist
- Code examples

**Example scenarios**:
- How to extract from Power BI Service?
- Best practices for schema bindings
- Integration with other tools
- Understanding ontology format

### Security Vulnerability

**When to use**: Report security vulnerabilities (prefer private reporting).

**Template**: `.github/ISSUE_TEMPLATE/security_vulnerability.md`

**Important**: 
- ⚠️ **DO NOT** create public issues for security vulnerabilities
- Use email or GitHub private reporting instead
- See [SECURITY.md](../SECURITY.md) for details

## 🔀 Pull Request Template

**Template**: `.github/PULL_REQUEST_TEMPLATE.md`

**Includes**:
- Description
- Related issue
- Type of change
- Checklist
- Screenshots
- Testing details

**Best practices**:
- Fill out all relevant sections
- Link to related issues
- Include test results
- Add screenshots for UI changes

## 🎯 Template Selection

When creating a new issue, GitHub will show you options:

1. **Bug Report** - For bugs and errors
2. **Feature Request** - For new features
3. **Question** - For questions
4. **Security Vulnerability** - For security issues (use sparingly)

## 📝 Filling Out Templates

### Bug Reports

**Be specific**:
- Include exact error messages
- Provide minimal reproduction steps
- Share relevant code snippets
- Attach sample files (sanitized)

**Don't**:
- Create duplicate issues (search first!)
- Include sensitive data in .pbix files
- Be vague about the problem

### Feature Requests

**Be clear**:
- Explain the problem you're solving
- Provide use cases
- Suggest implementation approach
- Consider alternatives

**Don't**:
- Request features that already exist
- Be too vague about requirements
- Ignore existing solutions

### Questions

**Be thorough**:
- Explain what you're trying to accomplish
- Show what you've tried
- Provide code examples
- Check documentation first

**Don't**:
- Ask questions answered in README
- Skip the "What I've Tried" section
- Be vague about your goal

## 🔗 Related Resources

- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Security Policy](../SECURITY.md) - Security reporting
- [Getting Started](getting_started.md) - Basic usage
- [GitHub Discussions](https://github.com/cloudbadal007/powerbi-ontology-extractor/discussions) - For general questions

## 💡 Tips

1. **Search first**: Check if your issue/question already exists
2. **Use templates**: Don't create blank issues
3. **Be patient**: Maintainers will respond as soon as possible
4. **Provide context**: More information is better than less
5. **Follow up**: Respond to maintainer questions promptly

---

**Need help?** Open a [Question](https://github.com/cloudbadal007/powerbi-ontology-extractor/issues/new?template=question.md) issue!
