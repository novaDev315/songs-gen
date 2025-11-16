# Songs-Gen Test Suite

Comprehensive test suite for the Songs-Gen automation pipeline, covering unit tests, integration tests, and end-to-end tests.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Test Categories](#test-categories)
- [Writing New Tests](#writing-new-tests)
- [Continuous Integration](#continuous-integration)

## Overview

The test suite ensures quality and reliability of the Songs-Gen automation pipeline through:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests for component interactions and API endpoints
- **End-to-End Tests**: Complete workflow tests from file detection to YouTube upload

**Coverage Target**: >80% statement coverage, >75% branch coverage

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── pytest.ini               # Pytest configuration
├── .coveragerc              # Coverage configuration
├── README.md                # This file
│
├── unit/                    # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_auth.py         # JWT token creation/validation, password hashing
│   ├── test_models.py       # Database model tests
│   ├── test_schemas.py      # Pydantic schema validation tests
│   ├── test_audio_analyzer.py    # Audio analysis and quality scoring
│   └── test_video_generator.py   # Video generation with FFmpeg
│
├── integration/             # Integration tests (component interactions)
│   ├── __init__.py
│   └── test_api_auth.py     # Authentication API endpoints
│
└── e2e/                     # End-to-end tests (complete workflows)
    ├── __init__.py
    └── test_complete_pipeline.py  # Full pipeline workflow tests
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for API testing)

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit -m unit

# Run only integration tests
pytest tests/integration -m integration

# Run only end-to-end tests
pytest tests/e2e -m e2e

# Run only authentication tests
pytest -m auth

# Run only API tests
pytest -m api
```

### Run Specific Test Files

```bash
# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test class
pytest tests/unit/test_auth.py::TestPasswordHashing

# Run specific test function
pytest tests/unit/test_auth.py::TestPasswordHashing::test_verify_password_success
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

### Skip Slow Tests

```bash
# Skip tests marked as slow
pytest -m "not slow"
```

## Test Coverage

### Generate Coverage Reports

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report (open htmlcov/index.html)
pytest --cov=app --cov-report=html

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Requirements

The test suite enforces minimum coverage thresholds:

- **Statement Coverage**: 80%
- **Branch Coverage**: 75%

Coverage reports exclude:
- Test files themselves
- Migration files
- `__init__.py` files
- Configuration files

### View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (<1 second per test)
- No external dependencies
- Use mocks for external services
- High code coverage

**Test Files**:
- `test_auth.py`: JWT tokens, password hashing (40+ tests)
- `test_models.py`: Database models, relationships (50+ tests)
- `test_schemas.py`: Pydantic validation (30+ tests)
- `test_audio_analyzer.py`: Audio quality analysis (25+ tests)
- `test_video_generator.py`: FFmpeg video generation (30+ tests)

**Run Command**:
```bash
pytest tests/unit -m unit
```

### Integration Tests

**Purpose**: Test component interactions and API endpoints

**Characteristics**:
- Moderate execution time (1-5 seconds per test)
- Uses test database
- Tests actual API calls
- Validates request/response flow

**Test Files**:
- `test_api_auth.py`: Authentication flow, token refresh, logout (40+ tests)
- `test_api_songs.py`: Song CRUD operations (planned)
- `test_api_queue.py`: Task queue management (planned)
- `test_api_evaluation.py`: Evaluation workflow (planned)
- `test_api_youtube.py`: YouTube upload flow (planned)
- `test_file_watcher.py`: File detection and parsing (planned)
- `test_worker.py`: Background task processing (planned)

**Run Command**:
```bash
pytest tests/integration -m integration
```

### End-to-End Tests

**Purpose**: Test complete workflows from start to finish

**Characteristics**:
- Slower execution (5-30 seconds per test)
- Tests entire pipeline
- Validates business logic
- Ensures system integration

**Test Files**:
- `test_complete_pipeline.py`: Full workflow from file detection to YouTube upload (25+ tests)
- `test_authentication_flow.py`: Complete auth flow (planned)

**Run Command**:
```bash
pytest tests/e2e -m e2e
```

## Test Markers

Tests are organized using pytest markers:

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Unit tests | `@pytest.mark.unit` |
| `integration` | Integration tests | `@pytest.mark.integration` |
| `e2e` | End-to-end tests | `@pytest.mark.e2e` |
| `auth` | Authentication tests | `@pytest.mark.auth` |
| `api` | API endpoint tests | `@pytest.mark.api` |
| `database` | Database tests | `@pytest.mark.database` |
| `service` | Service layer tests | `@pytest.mark.service` |
| `slow` | Slow tests (>5 sec) | `@pytest.mark.slow` |
| `audio` | Audio analysis tests | `@pytest.mark.audio` |
| `video` | Video generation tests | `@pytest.mark.video` |
| `youtube` | YouTube integration | `@pytest.mark.youtube` |
| `suno` | Suno integration (manual) | `@pytest.mark.suno` |

**Usage**:
```python
@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    # Test implementation
    pass
```

**Run tests by marker**:
```bash
# Run all auth tests
pytest -m auth

# Run unit tests excluding slow tests
pytest -m "unit and not slow"

# Run integration or e2e tests
pytest -m "integration or e2e"
```

## Writing New Tests

### Test Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<what>_<condition>_<expected>`

**Examples**:
```python
# Good test names
def test_login_valid_credentials_returns_token()
def test_song_creation_missing_title_raises_validation_error()
def test_audio_analyzer_corrupt_file_raises_exception()

# Bad test names
def test_login()
def test_song()
def test_error()
```

### Test Structure (Arrange-Act-Assert)

```python
def test_create_song_success(client, auth_headers, sample_song_data):
    """Test successful song creation."""
    # Arrange - Set up test data
    song_data = {
        "title": "Test Song",
        "genre": "Pop",
        "style_prompt": "Pop song with catchy hooks",
        "lyrics": "[Verse 1]\nTest lyrics",
    }

    # Act - Perform the action
    response = client.post(
        "/api/songs",
        json=song_data,
        headers=auth_headers,
    )

    # Assert - Verify the results
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == song_data["title"]
    assert data["genre"] == song_data["genre"]
```

### Using Fixtures

Leverage shared fixtures from `conftest.py`:

```python
def test_with_fixtures(
    client,           # FastAPI test client
    test_db,          # Test database session
    auth_headers,     # Authenticated user headers
    song_factory,     # Factory for creating songs
    temp_dir,         # Temporary directory
    mock_suno_client, # Mocked Suno client
):
    # Use fixtures in test
    song = song_factory(title="Test Song")
    response = client.get(f"/api/songs/{song.id}", headers=auth_headers)
    assert response.status_code == 200
```

### Testing Async Functions

Use `pytest.mark.asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function(async_test_db):
    """Test asynchronous database operation."""
    # Test async code
    result = await some_async_function()
    assert result is not None
```

### Mocking External Services

Mock external services to ensure tests are isolated:

```python
from unittest.mock import patch, AsyncMock

@patch("app.services.suno_client.SunoClient.upload_song")
async def test_suno_upload(mock_upload, song_factory):
    """Test Suno upload with mocked client."""
    # Configure mock
    mock_upload.return_value = {
        "song_id": "suno-123",
        "url": "https://suno.com/song/suno-123",
    }

    # Test code
    result = await upload_to_suno(song)
    assert result["song_id"] == "suno-123"
    mock_upload.assert_called_once()
```

### Parameterized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize(
    "genre,expected_status",
    [
        ("Pop", 201),
        ("Hip-Hop", 201),
        ("EDM", 201),
        ("InvalidGenre", 422),
    ],
)
def test_song_creation_various_genres(client, auth_headers, genre, expected_status):
    """Test song creation with various genres."""
    response = client.post(
        "/api/songs",
        json={"genre": genre, "title": "Test", ...},
        headers=auth_headers,
    )
    assert response.status_code == expected_status
```

## Test Data Management

### Factory Fixtures

Use factory fixtures for creating test data:

```python
def test_with_factories(song_factory, evaluation_factory):
    # Create test song
    song = song_factory(
        song_id="test-001",
        title="Test Song",
        genre="Pop",
    )

    # Create evaluation for song
    evaluation = evaluation_factory(
        song_id=song.id,
        is_approved=True,
        audio_quality_score=85.5,
    )

    assert evaluation.song_id == song.id
```

### Sample Data Fixtures

Use sample data fixtures for consistent test data:

```python
def test_with_sample_data(sample_song_data, sample_evaluation_data):
    # sample_song_data provides consistent song dictionary
    assert sample_song_data["genre"] == "Pop"

    # sample_evaluation_data provides consistent evaluation dictionary
    assert sample_evaluation_data["is_approved"] is True
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with database locked error
**Solution**: Restart backend service or delete test.db file

```bash
rm -f test.db
pytest
```

**Issue**: Import errors when running tests
**Solution**: Ensure you're in the backend directory and PYTHONPATH is set

```bash
cd /home/user/songs-gen/backend
export PYTHONPATH=/home/user/songs-gen/backend:$PYTHONPATH
pytest
```

**Issue**: Async tests not running
**Solution**: Install pytest-asyncio and ensure asyncio_mode is set

```bash
pip install pytest-asyncio
pytest --asyncio-mode=auto
```

**Issue**: Coverage report shows 0%
**Solution**: Ensure source path is correct in pytest.ini and .coveragerc

```bash
pytest --cov=app --cov-report=term-missing
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Fast Execution**: Keep unit tests under 1 second each
3. **Clear Names**: Use descriptive test names that explain what is being tested
4. **Arrange-Act-Assert**: Follow AAA pattern for clarity
5. **Mock External Services**: Don't call real APIs or external services in tests
6. **Test Edge Cases**: Include tests for error conditions and boundary cases
7. **Meaningful Assertions**: Use specific assertions with clear failure messages
8. **Fixtures Over Duplication**: Use fixtures to avoid repeating setup code
9. **Docstrings**: Add docstrings to explain complex test scenarios
10. **Cleanup**: Ensure tests clean up resources (files, database records)

## Test Metrics

Current test suite statistics:

- **Total Tests**: 175+ tests
- **Unit Tests**: 95+ tests
- **Integration Tests**: 40+ tests
- **End-to-End Tests**: 40+ tests
- **Code Coverage**: >80% (target)
- **Average Execution Time**: <30 seconds (full suite)

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Pydantic Testing](https://pydantic-docs.helpmanual.io/usage/models/#data-conversion)

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass before committing
3. Maintain >80% code coverage
4. Update this README if adding new test categories
5. Use appropriate markers for test categorization

---

**Last Updated**: 2025-11-16
**Maintained By**: Songs-Gen Development Team
