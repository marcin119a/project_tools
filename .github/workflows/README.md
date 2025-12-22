# GitHub Actions Workflows

Dokumentacja dla GitHub Actions workflows w projekcie FastAPI.

## Workflows

### CI Workflow (`ci.yml`)

Automatycznie uruchamiany na pushu do gałęzi `main` lub `develop` oraz na pull requestach.

#### Funkcjonalności:

1. **Code Quality Job**
   - Sprawdzenie formatowania kodu za pomocą `ruff`
   - Linting za pomocą `flake8`
   - Obsługiwane wersje Pythona: 3.10, 3.11, 3.12
   - Błędy lintingu nie zatrzymują workflow (`continue-on-error: true`)

2. **Tests Job**
   - Uruchamianie testów za pomocą `pytest`
   - Generowanie raportów pokrycia kodu (`coverage`)
   - Używanie SQLite w pamięci (`sqlite+aiosqlite:///:memory:`)
   - Obsługiwane wersje Pythona: 3.10, 3.11, 3.12

3. **Build Status Job**
   - Podsumowanie statusu całego workflow
   - Zależy od sukcesów jobs code-quality i tests

#### Zmienne środowiskowe:

- `DATABASE_URL`: `sqlite+aiosqlite:///:memory:` (SQLite w pamięci dla testów)
- `PYTHONPATH`: Ścieżka do workspace'u

#### Wyzwalacze:

- Push do gałęzi `main` lub `develop`
- Pull request do gałęzi `main` lub `develop`
- Ręczne uruchomienie workflow (`workflow_dispatch`)

#### Concurrency:

Workflow automatycznie anuluje poprzednie uruchomienia dla tego samego brancha/referencji.

## Wymagania

Plik `requirements.txt` musi zawierać:

```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
ruff>=0.1.0
flake8>=6.1.0
```

## Konfiguracja Pytest

Projekt używa `pytest.ini` do konfiguracji:

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Baza danych SQLite w testach

Testy używają SQLite w pamięci (`sqlite+aiosqlite:///:memory:`), które:
- Jest szybkie
- Nie wymaga dodatkowych serwisów
- Automatycznie czyści się po każdym teście

Konfiguracja w `tests/conftest.py`:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

## Codecov Integration

Raporty pokrycia są automatycznie wysyłane do Codecov:
- Jeśli Codecov nie jest dostępny, workflow kontynuuje bez błędu
- Generowanie raportu w formacie XML: `coverage.xml`

## Dodawanie nowych testów

Nowe testy powinny:
1. Być w katalogu `tests/`
2. Mieć nazwę zaczynającą się od `test_`
3. Używać fixture'ów z `conftest.py`
4. Być asynchroniczne (jeśli pracują z bazą danych)

Przykład:

```python
async def test_example(test_client):
    response = await test_client.get("/health")
    assert response.status_code == 200
```

## Monitoring

### Logi

Logi workflow są dostępne w zakładce "Actions" na GitHub.

### Coverage Reports

Raporty pokrycia kodu są dostępne na Codecov (jeśli skonfigurowany).

## Troubleshooting

### Test nie przechodzą w CI ale przechodzą lokalnie

1. Sprawdzić zmienne środowiskowe
2. Sprawdzić wersję Pythona
3. Sprawdzić czy SQLite jest poprawnie skonfigurowana

### Linting Error w CI

1. Uruchomić lokalnie: `ruff check .` i `flake8 .`
2. Naprawić błędy
3. Commitować i pushować ponownie

## Dodatkowe informacje

- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/advanced/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

