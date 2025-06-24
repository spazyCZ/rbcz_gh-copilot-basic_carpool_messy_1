# Testovacia dokumentácia - Parking Reservation System

## Prehľad

Tento dokument popisuje testovaciu stratégiu a implementáciu testov pre Parking Reservation System. Testy sú navrhnuté tak, aby pokryli všetky aspekty aplikácie vrátane dokumentovania existujúcich bezpečnostných problémov a chýb.

## Štruktúra testov

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest konfigurácia a fixtures
├── test_app.py              # Unit testy pre Flask aplikáciu
├── test_utils.py            # Unit testy pre utility funkcie
├── test_integration.py      # Integračné testy
├── test_performance.py      # Performance a load testy
└── test_security.py         # Bezpečnostné testy
```

## Kategórie testov

### 1. Unit testy (`test_app.py`, `test_utils.py`)
- **Účel**: Testovanie jednotlivých funkcií a komponentov
- **Pokrytie**: Flask routes, data handling, utility funkcie
- **Spustenie**: `pytest tests/test_app.py tests/test_utils.py`

### 2. Integračné testy (`test_integration.py`)
- **Účel**: Testovanie interakcií medzi komponentmi
- **Pokrytie**: Kompletné user workflows, data persistence, error scenarios
- **Spustenie**: `pytest tests/test_integration.py`

### 3. Performance testy (`test_performance.py`)
- **Účel**: Testovanie výkonu a škálovateľnosti
- **Pokrytie**: Response times, concurrent access, load testing
- **Spustenie**: `pytest tests/test_performance.py`

### 4. Bezpečnostné testy (`test_security.py`)
- **Účel**: Identifikácia a dokumentovanie bezpečnostných zraniteľností
- **Pokrytie**: Authentication, authorization, input validation, XSS, atď.
- **Spustenie**: `pytest tests/test_security.py`

## Spustenie testov

### Základné spustenie
```bash
# Všetky testy
pytest

# Konkrétna kategória
pytest tests/test_app.py

# S coverage reportom
pytest --cov=app --cov=utils --cov-report=html

# Pomocou Makefile
make test
make test-coverage
make test-security
```

### Použitie markerov
```bash
# Len rýchle testy
pytest -m "not slow"

# Len bezpečnostné testy
pytest -m security

# Len performance testy
pytest -m performance
```

## Dokumentované problémy

### Bezpečnostné zraniteľnosti
1. **Slabý secret key**: `app.secret_key = "123"`
2. **Hardcoded credentials**: Heslá v source kóde
3. **Plaintext password storage**: Heslá nie sú hashované
4. **Chýbajúca autentifikácia**: Kritické operácie bez overenia
5. **XSS vulnerability**: Neescapované user input
6. **No CSRF protection**: Chýba CSRF ochrana
7. **Information disclosure**: Debug routes v produkcii

### Funkcionálne problémy
1. **Double booking**: Možnosť rezervovať jedno miesto viackrát
2. **Race conditions**: Concurrent prístup bez synchronizácie
3. **No input validation**: Chýba validácia user input
4. **Poor error handling**: Nevhodné ošetrovanie chýb
5. **File corruption**: Možná korupcia dát pri concurrent prístupe

### Architektúrne problémy
1. **Monolithic structure**: Všetka logika v jednom súbore
2. **Global variables**: Používanie globálnych premenných
3. **No separation of concerns**: Zmiešaná logika a prezentácia
4. **Poor naming**: Zlé pomenovanie premenných a funkcií

## Fixtures a test data

### Dostupné fixtures
- `client`: Flask test client
- `authenticated_session`: Client s autentifikovanou session
- `mock_files`: Mock file paths pre testovanie
- `sample_data`: Vzorové dáta pre rezervácie
- `reset_global_data`: Reset globálnych premenných
- `temp_dir`: Dočasný adresár pre file operácie

### Ukážka použitia
```python
def test_example(client, sample_data, reset_global_data):
    # Test s clean state a sample data
    global data
    data.update(sample_data)
    
    response = client.get('/')
    assert response.status_code == 200
```

## Coverage target

**Aktuálny target**: 50% (nízky kvôli kvalite kódu)
**Dlhodobý cieľ**: 80%+ po refaktoringu

## Continuous Integration

Pre CI/CD použite:
```bash
make ci  # Spustí lint, security checks a testy s coverage
```

## Výstupy testov

### Coverage report
- HTML report: `htmlcov/index.html`
- Terminal output s missing lines

### Test report
- HTML report: `reports/test_report.html` (s `--html` parametrom)

### Security report
- Bandit output pre security issues
- Safety check pre známe vulnerabilities

## Odporúčania

### Pre vývojárov
1. Spúšťajte testy pred každým commit
2. Pridávajte testy pre nové features
3. Používajte security testy na identifikáciu problémov
4. Sledujte coverage metriky

### Pre refaktoring
1. Začnite s bezpečnostnými problémami
2. Rozdeľte monolitickú štruktúru
3. Pridajte input validation
4. Implementujte proper error handling
5. Zvýšte test coverage postupne

## Budúce rozšírenia

1. **API testy**: Ak sa pridá REST API
2. **Database testy**: Pri prechode na databázu
3. **UI testy**: Selenium/Playwright testy
4. **Contract testy**: Pre API endpoints
5. **Mutation testing**: Pre kvalitu testov

## Nástroje a dependencies

### Testovacie framework
- **pytest**: Hlavný testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-xdist**: Parallel test execution

### Code quality
- **flake8**: Linting
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking

### Security
- **bandit**: Security linter
- **safety**: Vulnerability checking

## Kontakt a podpora

Pre otázky ohľadom testov alebo pridávania nových testov, konzultujte tento dokument alebo sa obráťte na tím.
