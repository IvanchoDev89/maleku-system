# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Costa Rica Travel seriously. If you believe you have
found a security vulnerability, please **do not** open a public issue.

Instead, report it privately by emailing:

**security@costaricatravel.dev**

You should receive a response within 48 hours. If you do not, please follow up
to ensure we received your original message.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected endpoints/components
- Any proof of concept (if available)

### Policy

- We will acknowledge receipt within 48 hours
- We will provide an estimated timeline for a fix
- We will notify you when the fix is deployed
- We do not currently offer a bug bounty program

## Security Measures

- **Authentication**: JWT with access + refresh tokens, token blacklisting
- **Rate Limiting**: 60 req/min per IP, 5 login attempts per 15 min
- **Password Hashing**: bcrypt (11 rounds)
- **SQL Injection**: Prevented by SQLAlchemy ORM + parameterized queries
- **XSS**: Auto-escaped by Vue.js/Nuxt template rendering
- **CORS**: Explicitly whitelisted origins only
- **CSRF**: Token-based protection on state-changing endpoints
- **Audit Logging**: All admin and sensitive actions logged
- **Soft Delete**: All entities use `deleted_at` instead of hard deletes
- **Secrets**: Environment variables only, never committed to repo

## Disclosure Policy

We follow a 90-day disclosure window. After a fix is deployed, we will work
with the reporter to coordinate public disclosure.
