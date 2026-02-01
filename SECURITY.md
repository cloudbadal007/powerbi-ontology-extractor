# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note**: We recommend always using the latest version for the best security posture.

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow responsible disclosure practices.

### ⚠️ DO NOT

- ❌ Open a public GitHub issue
- ❌ Discuss in public forums or social media
- ❌ Share with others before we've addressed it
- ❌ Create a public pull request that exposes the vulnerability

### ✅ DO

1. **Email Security Team**: Send details to `security@example.com` or `cloudpankaj@example.com`
   - Use a descriptive subject line: `[SECURITY] Vulnerability in [component]`
   
2. **Include the Following Information**:
   - Description of the vulnerability
   - Steps to reproduce (if applicable)
   - Potential impact and severity assessment
   - Affected versions
   - Suggested fix or mitigation (if any)
   - Proof of concept (if available, but be careful not to include exploits)

3. **Response Timeline**:
   - **Initial response**: Within 48 hours
   - **Status update**: Within 7 days
   - **Fix timeline**: Depends on severity
     - Critical: As soon as possible (typically within 7 days)
     - High: Within 30 days
     - Medium: Within 90 days
     - Low: Next scheduled release

### What to Expect

- ✅ We'll acknowledge your email within 48 hours
- ✅ We'll investigate and provide a detailed response
- ✅ We'll work on a fix and notify you when it's ready
- ✅ We'll credit you in the security advisory (unless you prefer anonymity)
- ✅ We'll coordinate public disclosure timing with you

### Severity Classification

We use the following severity levels:

- **Critical**: Remote code execution, data breach, authentication bypass
- **High**: Privilege escalation, sensitive data exposure
- **Medium**: Information disclosure, denial of service
- **Low**: Minor information leakage, best practice violations

## Security Best Practices for Users

When using PowerBI Ontology Extractor:

### Installation & Updates
- ✅ **Keep the package updated**: Regularly update to the latest version
- ✅ **Use virtual environments**: Isolate dependencies
- ✅ **Pin dependency versions**: Use `requirements.txt` with specific versions in production

### Data Handling
- ✅ **Review .pbix files**: May contain sensitive business data - review before processing
- ✅ **Sanitize test data**: Remove sensitive information from sample files
- ✅ **Secure file storage**: Protect .pbix files and exported ontologies
- ✅ **Access controls**: Apply appropriate permissions to exported files

### Validation & Deployment
- ✅ **Validate exported ontologies**: Review before deploying to production
- ✅ **Use schema validation**: Enable schema drift detection to prevent failures
- ✅ **Test in staging**: Always test in non-production environments first
- ✅ **Review business rules**: Verify extracted business rules are correct

### Production Usage
- ✅ **Enable audit logging**: Log all operations in production
- ✅ **Monitor for drift**: Regularly check for schema changes
- ✅ **Limit permissions**: Use least privilege principle for AI agents
- ✅ **Review contracts**: Regularly audit semantic contracts for AI agents

### Network & Infrastructure
- ✅ **Use secure connections**: When connecting to data sources
- ✅ **Encrypt sensitive data**: At rest and in transit
- ✅ **Implement rate limiting**: For API endpoints (if applicable)
- ✅ **Regular backups**: Backup ontologies and configurations

## Known Security Considerations

### 1. .pbix Files Contain Sensitive Data

**Risk**: Power BI .pbix files may contain sensitive business data, credentials, or proprietary information.

**Mitigation**:
- Review .pbix files before processing
- Remove sensitive data from sample files before sharing
- Use data masking or anonymization for test environments
- Apply access controls to .pbix files

**Recommendation**: Never commit .pbix files to version control or share them publicly.

### 2. Schema Drift Can Cause AI Agent Failures

**Risk**: Schema changes in data sources can cause AI agents to fail or produce incorrect results.

**Mitigation**:
- Use schema validation feature (`SchemaMapper.validate_binding()`)
- Enable drift detection (`SchemaMapper.detect_drift()`)
- Implement monitoring and alerting for schema changes
- Test schema bindings before deploying agents

**Recommendation**: Always validate schema bindings in CI/CD pipelines.

### 3. Exported Ontologies May Reveal Business Logic

**Risk**: Exported ontologies contain business rules and data structures that may be sensitive.

**Mitigation**:
- Apply access controls to exported ontology files
- Review exported ontologies before sharing
- Use encryption for sensitive ontology files
- Implement version control for ontology changes

**Recommendation**: Treat exported ontologies as sensitive business assets.

### 4. DAX Formulas May Contain Sensitive Logic

**Risk**: DAX measures may encode proprietary business logic or calculations.

**Mitigation**:
- Review extracted business rules before exporting
- Sanitize business rules in test environments
- Apply access controls to business rule definitions

### 5. Semantic Contracts Define Agent Permissions

**Risk**: Incorrectly configured semantic contracts may grant excessive permissions to AI agents.

**Mitigation**:
- Follow least privilege principle
- Regularly audit semantic contracts
- Use role-based access control
- Validate contracts before deployment

**Recommendation**: Review and test semantic contracts in staging before production.

## Dependency Security

We regularly update dependencies to address security vulnerabilities:

- **Automated scanning**: GitHub Dependabot monitors dependencies
- **Manual reviews**: Regular security audits of dependencies
- **Quick updates**: Critical security updates are applied immediately

To check for known vulnerabilities in dependencies:

```bash
pip install safety
safety check
```

## Security Updates

Security updates are released as:
- **Patch releases**: For critical and high severity issues (e.g., 0.1.1)
- **Minor releases**: For medium severity issues (e.g., 0.2.0)
- **Security advisories**: Published on GitHub Security Advisories

Subscribe to security advisories:
- Watch the repository for security alerts
- Check GitHub Security Advisories: https://github.com/cloudbadal007/powerbi-ontology-extractor/security/advisories

## Security Features

This project includes several security features:

- ✅ **Schema drift detection**: Prevents the $4.6M mistake scenario
- ✅ **Input validation**: Validates .pbix file structure
- ✅ **Error handling**: Graceful error handling without information leakage
- ✅ **Type checking**: Static type analysis with mypy
- ✅ **Code quality**: Automated security scanning with CodeQL
- ✅ **Dependency review**: Automated dependency vulnerability scanning

## Compliance

This tool may process sensitive data. Consider:

- **GDPR**: If processing EU personal data
- **HIPAA**: If processing healthcare data
- **SOC 2**: For enterprise deployments
- **Data residency**: Where data is processed and stored

**Note**: This tool does not store or transmit data to external services by default. Review your deployment configuration for compliance requirements.

## Security Contact

For security-related inquiries:

- **Email**: security@example.com or cloudpankaj@example.com
- **PGP Key**: [Link to PGP key if available]
- **GitHub Security**: Use GitHub's private vulnerability reporting (if enabled)

## Acknowledgments

We thank security researchers and contributors who help improve the security of this project. Contributors will be acknowledged in security advisories (unless they prefer anonymity).

---

**Thank you for helping keep PowerBI Ontology Extractor secure!** 🔒

Your responsible disclosure helps protect all users of this tool.
