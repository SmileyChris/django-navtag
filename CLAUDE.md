# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is `django-navtag`, a Django template tag library for handling navigation item selection in templates. It provides a simple way to manage active states in navigation menus across template inheritance hierarchies.

## Project Structure

- `django_navtag/templatetags/navtag.py` - Core implementation (Nav class and template tags)
- `django_navtag/tests/test_navtag.py` - Test suite
- `django_navtag/tests/settings.py` - Django test settings

## Common Commands

### Development Setup
```bash
# Install with development dependencies (requires pip >= 23.1)
pip install -e ".[dev]"

# Or using the dependency-groups syntax (pip >= 24.1)
pip install -e . --dependency-groups=dev
```

### Running Tests
```bash
# Run tests with pytest
pytest

# Run with coverage
pytest --cov

# Run full test matrix across Python/Django versions
tox

# Run specific environment
tox -e py39-django32
```

### Code Quality
```bash
# Check README formatting
tox -e readme

# Run coverage checks (100% for tests, 90% for main code)
tox -e coverage
```

### Release Process
- Uses zest.releaser for version management
- Current version: 3.3.dev0
- Tag signing is enabled

## Key Implementation Details

### Nav Class (`django_navtag/templatetags/navtag.py`)
The Nav class is the core of the library, providing:
- Hierarchical navigation state management via dictionary structure
- Special comparison operators (`__eq__`, `__contains__`)
- Pattern matching with `!` syntax for children-only matching
- Active path tracking via `get_active_path()`

### Template Tags
1. **`{% nav %}`** - Sets active navigation items
   - Supports hierarchical paths (e.g., `about_menu.info`)
   - Custom context variable names with `for`
   - Text output customization
   
2. **`{% navlink %}`** - Renders links/spans based on navigation state
   - Automatically switches between `<a>` and `<span>` elements
   - Supports special patterns and alternate nav variables

### Testing
- Uses pytest with pytest-django
- Test templates in `django_navtag/templates/navtag_tests/`
- Django settings module: `django_navtag.tests.settings`

## Python/Django Support
- Python: 3.8-3.12
- Django: 3.2, 4.2, 5.0, 5.1