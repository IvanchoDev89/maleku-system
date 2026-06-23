# Contributing to Costa Rica Travel

Thank you for your interest in contributing to Costa Rica Travel! This document provides guidelines and instructions for contributing to the project.

---

## 🚀 Getting Started

### Prerequisites

- **Git** 2.30+
- **Docker** 20.10+ & Docker Compose
- **Node.js** 18+ (for frontend development)
- **Python** 3.11+ (for backend development)
- **Make** (optional, for convenience commands)

### Fork & Clone

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/costa-rica-travel.git
cd costa-rica-travel

# 3. Add upstream remote
git remote add upstream https://github.com/original-org/costa-rica-travel.git
```

---

## 📋 Development Setup

### Option 1: Docker (Recommended)

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Services will be available at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your settings
npm run dev
```

---

## 🌿 Branch Strategy

We follow **Git Flow** with these branch types:

| Branch | Purpose | From | Merge To |
|--------|---------|------|----------|
| `main` | Production code | - | - |
| `develop` | Development integration | - | main |
| `feature/*` | New features | develop | develop |
| `bugfix/*` | Bug fixes | develop | develop |
| `hotfix/*` | Urgent fixes | main | main + develop |
| `release/*` | Release preparation | develop | main |

### Creating a Feature Branch

```bash
# Ensure you're on develop and up to date
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/my-new-feature

# Work on your feature...
```

---

## 💻 Coding Standards

### Backend (Python/FastAPI)

#### Code Style
- Follow **PEP 8**
- Use **Black** formatter: `black backend/`
- Use **isort** for imports: `isort backend/`
- Maximum line length: 88 characters

```bash
# Format code
cd backend
black app/
isort app/
flake8 app/

# Run type checking
mypy app/
```

#### Code Structure
```python
# app/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas import ExampleCreate, ExampleResponse
from app.services import ExampleService

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(
    example_in: ExampleCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create new example.

    - **example_in**: Example data
    - Returns: Created example
    """
    service = ExampleService(db)
    return await service.create(example_in, user_id=current_user.id)
```

#### Documentation
- All endpoints must have docstrings
- Include request/response examples
- Document error scenarios

### Frontend (Vue/Nuxt)

#### Code Style
- Use **TypeScript** for all new code
- Follow **Vue 3 Style Guide**
- Use **ESLint** + **Prettier**

```bash
# Lint and format
cd frontend
npm run lint
npm run format
```

#### Component Structure
```vue
<!-- components/ExampleComponent.vue -->
<template>
  <div class="example">
    <h1>{{ title }}</h1>
    <slot />
  </div>
</template>

<script setup lang="ts">
// Imports
import { ref, computed } from 'vue'
import type { Example } from '~/types'

// Props & Emits
interface Props {
  title: string
  items: Example[]
}
const props = defineProps<Props>()

const emit = defineEmits<{
  select: [item: Example]
}>()

// Composables
const { user } = useAuth()

// Reactive state
const selected = ref<Example | null>(null)

// Computed
const hasItems = computed(() => props.items.length > 0)

// Methods
const handleSelect = (item: Example) => {
  selected.value = item
  emit('select', item)
}
</script>

<style scoped>
.example {
  @apply p-4 bg-white rounded-lg;
}
</style>
```

#### Naming Conventions
- Components: `PascalCase` (e.g., `UserProfile.vue`)
- Composables: `camelCase` with `use` prefix (e.g., `useAuth.ts`)
- Stores: `camelCase` (e.g., `userStore.ts`)
- Pages: `kebab-case` (e.g., `user-profile.vue`)

---

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with watch mode
pytest -f
```

#### Test Structure
```python
# tests/test_example.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_example(client: AsyncClient, db_session):
    """Test creating a new example."""
    response = await client.post(
        "/api/v1/examples/",
        json={"name": "Test Example", "value": 42}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Example"
    assert data["value"] == 42
```

### Frontend Testing

```bash
cd frontend

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

---

## 📝 Commit Messages

We follow **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |
| `ci` | CI/CD changes |
| `security` | Security fixes |

### Examples

```bash
# Good commits
git commit -m "feat(auth): add password reset flow"
git commit -m "fix(properties): correct price calculation in booking"
git commit -m "docs(api): add examples to search endpoint"
git commit -m "refactor(frontend): simplify booking store"
git commit -m "test(backend): add tests for vendor endpoints"

# Bad commits (don't do this)
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "asdf"
```

---

## 🔍 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console.logs or debug code
- [ ] Commit messages follow convention

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks**: CI runs tests and linting
2. **Code Review**: At least one approval required
3. **Testing**: Reviewer tests changes locally
4. **Merge**: Squash and merge to develop

---

## 🐛 Reporting Bugs

### Before Reporting
- Search existing issues
- Check if it's already fixed in develop
- Try to reproduce on latest version

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS 13.0]
- Browser: [e.g., Chrome 120]
- Node version: [e.g., 18.17]
- Python version: [e.g., 3.11.4]

**Additional Context**
Any other relevant information
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other approaches

**Additional context**
Mockups, examples, etc.
```

---

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something is broken |
| `enhancement` | New feature or request |
| `documentation` | Docs need improvement |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `priority:high` | Urgent |
| `backend` | Backend related |
| `frontend` | Frontend related |
| `database` | Database related |
| `security` | Security concern |

---

## 🔒 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, email: `security@costaricatravel.dev`

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or API keys
- Use `.env.example` for environment variables
- Validate all user inputs
- Use parameterized queries
- Keep dependencies updated

---

## 📚 Resources

### Documentation
- [Architecture](./ARCHITECTURE.md)
- [API Reference](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)

### Learning Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Nuxt.js Docs](https://nuxt.com/docs)
- [Vue.js Style Guide](https://vuejs.org/style-guide/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unethical conduct

### Enforcement

Violations can be reported to project maintainers. All complaints will be reviewed and investigated.

---

## 🙏 Recognition

Contributors will be:
- Listed in our README.md
- Mentioned in release notes
- Added to contributors page (coming soon)

Thank you for contributing to Costa Rica Travel! 🌴

---

<p align="center">
  <strong>Happy Coding! 🚀</strong>
</p>
