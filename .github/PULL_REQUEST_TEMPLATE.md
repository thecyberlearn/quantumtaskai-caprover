# Pull Request

## Description
<!-- Provide a clear and concise description of what this PR does -->

## Type of Change
<!-- Mark the relevant option with an "x" -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 🎨 UI/UX improvement (changes to user interface or experience)
- [ ] 🔧 Refactoring (code change that neither fixes a bug nor adds a feature)
- [ ] 📚 Documentation update
- [ ] 🚀 Performance improvement
- [ ] 🔐 Security improvement
- [ ] 🤖 New AI agent (marketplace agent addition)
- [ ] ⚡ Breaking change (fix or feature that would cause existing functionality to not work as expected)

## Agent Development (if applicable)
<!-- For new agents or agent modifications -->
- [ ] Agent type: Webhook / API
- [ ] Agent category: ________________
- [ ] Price: _______ AED
- [ ] N8N workflow configured (webhook agents)
- [ ] BaseAgent catalog entry created
- [ ] Component-based template implemented
- [ ] Dynamic pricing using {{ agent.price }}
- [ ] Standardized toast messages

## Testing Checklist
<!-- Mark completed items with an "x" -->
- [ ] Tested locally with `python manage.py runserver`
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Database migrations tested (if applicable)
- [ ] Tested with different user permission levels
- [ ] Mobile/responsive design tested
- [ ] Cross-browser compatibility verified
- [ ] Agent functionality tested end-to-end (if applicable)

## Security Checklist
<!-- Mark completed items with an "x" -->
- [ ] No hardcoded secrets or API keys
- [ ] Input validation implemented
- [ ] Authentication/authorization properly handled
- [ ] CSRF protection in place for forms
- [ ] File upload validation (if applicable)
- [ ] XSS prevention measures implemented
- [ ] SQL injection prevention (using Django ORM)

## Deployment Readiness
<!-- Mark completed items with an "x" -->
- [ ] Environment variables documented
- [ ] Static files optimization completed
- [ ] Database migration strategy confirmed
- [ ] Rollback plan prepared
- [ ] Documentation updated
- [ ] CLAUDE.md updated (if needed)

## Code Quality
<!-- Mark completed items with an "x" -->
- [ ] Code follows project conventions
- [ ] Functions and variables properly named
- [ ] No duplicate code
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Performance considerations addressed

## Branch Strategy
<!-- Mark the target branch -->
- [ ] `development` ← Feature/bug fix
- [ ] `staging` ← Ready for staging deployment and testing
- [ ] `main` ← Ready for production deployment (requires approval)

## Related Issues
<!-- Link to related issues -->
Fixes #(issue_number)
Closes #(issue_number)
Related to #(issue_number)

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Additional Notes
<!-- Any additional information, deployment notes, or special considerations -->

---

## For Reviewers

### Review Checklist
- [ ] Code quality and conventions followed
- [ ] Security considerations addressed
- [ ] Testing coverage adequate
- [ ] Documentation complete and accurate
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Deployment requirements understood

### Agent Review (if applicable)
- [ ] Agent follows established patterns
- [ ] Component-based template architecture used
- [ ] Proper error handling and user feedback
- [ ] Marketplace integration complete
- [ ] Pricing and wallet validation correct

### Security Review
- [ ] No security vulnerabilities introduced
- [ ] Authentication and authorization correct
- [ ] Input validation comprehensive
- [ ] File handling secure (if applicable)
- [ ] Payment processing secure (if applicable)