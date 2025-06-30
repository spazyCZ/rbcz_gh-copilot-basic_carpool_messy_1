# Zadávací dokumentace - Parking Reservations System

## 1. Requirements/Features

### 1.1 Funkční požadavky

#### Správa rezervací parkovacích míst
- **Zobrazení rezervací**: Uživatel může zobrazit seznam všech rezervovaných parkovacích míst
- **Vytvoření rezervace**: Uživatel může vytvořit novou rezervaci pro konkrétní parkovací místo
- **Úprava rezervace**: Uživatel může upravit existující rezervaci (změna jména rezervujícího)
- **Zrušení rezervace**: Uživatel může zrušit existující rezervaci
- **Prevence dvojitých rezervací**: Systém neumožní rezervovat již obsazené místo

#### Autentizace a autorizace
- **Přihlášení uživatele**: Jednoduchá autentizace pomocí uživatelského jména a hesla
- **Ochrana proti neoprávněnému přístupu**: Pouze přihlášení uživatelé mohou spravovat rezervace
- **Odhlášení**: Uživatel se může bezpečně odhlásit ze systému

#### Webové rozhraní
- **Responzivní design**: Aplikace funguje na různých zařízeních (desktop, tablet, mobil)
- **Uživatelsky přívětivé rozhraní**: Moderní UI s Bootstrap frameworkem
- **Flash zprávy**: Informování uživatele o úspěšných operacích nebo chybách
- **Formulářová validace**: Kontrola vstupních dat jak na straně klienta, tak serveru

#### REST API
- **GET /api/reservations**: Získání seznamu všech rezervací
- **POST /api/reservations**: Vytvoření nové rezervace
- **GET /api/reservations/<place>**: Získání konkrétní rezervace
- **PUT /api/reservations/<place>**: Aktualizace existující rezervace
- **DELETE /api/reservations/<place>**: Smazání rezervace
- **GET /api/reservations/<place>/availability**: Kontrola dostupnosti místa

### 1.2 Nefunkční požadavky

#### Výkon
- Rychlá odezva aplikace (< 1 sekunda pro běžné operace)
- Podpora současného přístupu více uživatelů

#### Bezpečnost
- Validace všech vstupních dat
- Ochrana proti CSRF útokům
- Bezpečné ukládání přihlašovacích údajů
- Ochrana před XSS útoky

#### Použitelnost
- Intuitivní uživatelské rozhraní
- Konzistentní design napříč aplikací
- Dostupnost (základní podpora screen readerů)

#### Maintainability
- Modulární architektura (MVC pattern)
- Komplexní testovací pokrytí
- Dokumentace kódu a API
- Logování aplikačních událostí

## 2. Database Model

### 2.1 Entita: ParkingReservation

```python
class ParkingReservation:
    place: str              # Identifikátor parkovacího místa (např. "A1", "B-02")
    name: str               # Jméno osoby, která si rezervuje místo
    reservation_date: date  # Datum rezervace
    created_at: datetime    # Časové razítko vytvoření rezervace
```

### 2.2 Datové typy a omezení

| Pole | Typ | Omezení | Popis |
|------|-----|---------|-------|
| `place` | String | 1-20 znaků, alfanumerické + pomlčka/podtržítko | Jedinečný identifikátor parkovacího místa |
| `name` | String | 2-50 znaků, písmena + mezery + tečka/pomlčka/apostrof | Jméno rezervujícího |
| `reservation_date` | Date | Dnešní datum nebo budoucí | Datum, na které je místo rezervováno |
| `created_at` | DateTime | Automaticky generováno | Časové razítko vytvoření |

### 2.3 Validační pravidla

#### Parkovací místo (place)
- **Pattern**: `^[A-Za-z0-9_-]{1,20}$`
- **Příklady platných hodnot**: "A1", "B-02", "SPOT_15", "VIP1"
- **Jedinečnost**: Každé místo může mít pouze jednu aktivní rezervaci

#### Jméno (name)
- **Pattern**: `^[A-Za-z\s\.\-\']{2,50}$`
- **Příklady platných hodnot**: "Jan Novák", "O'Connor", "Dr. Smith"

#### Datum rezervace (reservation_date)
- **Omezení**: Nesmí být v minulosti
- **Formát**: ISO 8601 (YYYY-MM-DD)

### 2.4 Datové úložiště

#### Současné řešení (JSON)
- **Soubor**: `parking_data.json`
- **Struktura**:
```json
{
  "A1": {
    "place": "A1",
    "name": "Jan Novák",
    "reservation_date": "2025-06-30",
    "created_at": "2025-06-30T14:04:36.220248"
  },
  "B2": {
    "place": "B2", 
    "name": "Marie Svobodová",
    "reservation_date": "2025-07-01",
    "created_at": "2025-06-30T15:30:00.123456"
  }
}
```

#### Doporučené budoucí řešení
- **SQLite** pro development
- **PostgreSQL** pro production
- **Migrace** pomocí Flask-Migrate

## 3. Technology Stack

### 3.1 Backend

#### Core Framework
- **Flask 2.3+**: Hlavní webový framework
- **Python 3.9+**: Programovací jazyk

#### Flask Extensions
- **Flask-WTF**: Formuláře a CSRF ochrana
- **Flask-Login**: Správa uživatelských sessions (pro budoucí rozšíření)
- **Flask-Talisman**: Bezpečnostní hlavičky HTTP
- **Werkzeug**: WSGI utilities (součást Flasku)

#### Data Layer
- **JSON**: Současné datové úložiště
- **SQLite/PostgreSQL**: Doporučené pro budoucí verze
- **SQLAlchemy**: ORM pro databázové operace (připraveno pro migraci)

### 3.2 Frontend

#### UI Framework
- **Bootstrap 5.3**: Responzivní CSS framework
- **Bootstrap Icons**: Sada ikon
- **jQuery 3.x**: JavaScript knihovna (volitelně)

#### Templates
- **Jinja2**: Template engine (součást Flasku)
- **HTML5**: Sémantické značkování
- **CSS3**: Vlastní styly

### 3.3 Development & Testing

#### Testing Framework
- **pytest**: Testovací framework
- **pytest-flask**: Flask-specifické testovací utility
- **coverage**: Měření pokrytí kódu testy

#### Code Quality
- **Black**: Formátování kódu
- **Flake8**: Linting
- **isort**: Organizace importů
- **Type hints**: Python type annotations

#### Development Tools
- **Flask Development Server**: Lokální development
- **python-dotenv**: Správa environment proměnných
- **Werkzeug Debugger**: Debugging nástroj

### 3.4 Deployment

#### Production Server
- **Gunicorn**: WSGI HTTP Server
- **Nginx**: Reverse proxy (doporučeno)

#### Environment Management
- **virtualenv/venv**: Izolace Python prostředí
- **pip**: Správa závislostí
- **requirements.txt**: Seznam závislostí

#### Configuration
- **.env files**: Environment-specific konfigurace
- **Config classes**: Objektově orientovaná konfigurace

### 3.5 Security

#### Authentication & Authorization
- **Flask-Session**: Session management
- **Bcrypt/Argon2**: Password hashing (pro budoucí verze)
- **CSRF Protection**: Flask-WTF

#### Input Validation
- **WTForms**: Formulářová validace
- **Custom validators**: Specifické validační pravidla
- **HTML escaping**: Automatické v Jinja2

### 3.6 Monitoring & Logging

#### Logging
- **Python logging**: Standardní logging knihovna
- **RotatingFileHandler**: Rotace log souborů
- **Structured logging**: JSON formát pro produkci

#### Error Handling
- **Custom exception classes**: Specifické výjimky aplikace
- **Error handlers**: Flask error handling
- **User-friendly error pages**: Vlastní error templates

### 3.7 Architecture Pattern

#### Design Patterns
- **MVC (Model-View-Controller)**: Separace concerns
- **Service Layer**: Business logika
- **Repository Pattern**: Datová vrstva (připraveno)
- **Factory Pattern**: Vytváření Flask aplikace

#### Project Structure
```
project/
├── app/                    # Hlavní aplikační balíček
│   ├── __init__.py        # Application factory
│   ├── models/            # Datové modely
│   ├── routes/            # Route blueprints (controllers)
│   ├── services/          # Business logika
│   └── utils/             # Utility funkce
├── config/                # Konfigurační nastavení
├── templates/             # Jinja2 templates
├── static/                # Statické soubory
├── tests/                 # Unit testy
└── run.py                 # Entry point
```

### 3.8 Dependencies

#### Production Dependencies
```
Flask>=2.3.0
Werkzeug>=2.3.0
```

#### Development Dependencies
```
pytest>=7.0.0
pytest-flask>=1.2.0
black>=23.0.0
flake8>=6.0.0
```

## 4. Doporučené priority implementace

### 4.1 High Priority

#### 1. Uživatelský management s rolemi
- **Registrace a přihlašování**: Plnohodnotný user management systém
- **Role-based access control**: Admin, Manager, User role
- **Profil uživatele**: Editace osobních údajů a kontaktů
- **Password management**: Reset hesla, změna hesla

**Implementace:**
```python
# models/user.py
class User:
    id: str
    username: str
    email: str
    password_hash: str
    role: str  # 'user', 'admin', 'manager'
    is_active: bool
    created_at: datetime
    last_login: datetime
```

#### 2. Časové rezervace (start/end time)
- **Hodinové rezervace**: Místo celodenních rezervací
- **Flexible booking**: Možnost rezervace na konkrétní časové úseky
- **Conflict detection**: Prevence překrývajících se rezervací
- **Automatic expiration**: Automatické uvolnění prošlých rezervací

**Rozšíření modelu:**
```python
class ParkingReservation:
    # ...existing fields...
    start_time: datetime
    end_time: datetime
    status: str  # 'active', 'cancelled', 'expired', 'completed'
```

#### 3. Email notifikace
- **Confirmation emails**: Potvrzení vytvoření/změny rezervace
- **Reminders**: Připomínky před začátkem rezervace
- **Cancellation notices**: Notifikace o zrušení
- **System notifications**: Upozornění na změny v systému

**Integrace:**
- Flask-Mail pro odesílání emailů
- Template-based email content
- Asynchronní odesílání (Celery doporučeno)

#### 4. Audit logging
- **Complete audit trail**: Sledování všech změn v systému
- **User actions**: Kdo, kdy, co udělal
- **System events**: Přihlášení, odhlášení, chyby
- **Data changes**: Před/po hodnotách při úpravách

**Implementace:**
```python
class AuditLog:
    id: str
    user_id: str
    action: str           # 'create', 'update', 'delete', 'login'
    resource_type: str    # 'reservation', 'user', 'parking_spot'
    resource_id: str
    old_values: dict
    new_values: dict
    timestamp: datetime
    ip_address: str
```

#### 5. Enhanced security
- **Password hashing**: Bcrypt/Argon2 pro secure ukládání hesel
- **Rate limiting**: Ochrana proti brute force útokům
- **Session security**: Secure session management
- **Input validation**: Comprehensive data validation

**Security stack:**
```python
# requirements.txt additions
flask-limiter>=3.0.0      # Rate limiting
flask-bcrypt>=1.0.0       # Password hashing
flask-talisman>=1.1.0     # Security headers
python-decouple>=3.8      # Secure config management
```

### 4.2 Medium Priority

#### 1. Reporting a analytics
- **Usage statistics**: Využití parkovacích míst
- **User analytics**: Statistiky uživatelů
- **Peak time analysis**: Analýza špičkových hodin
- **Export capabilities**: CSV/Excel export dat

#### 2. Pokročilé vyhledávání
- **Advanced filters**: Filtrování podle data, uživatele, statusu
- **Date range searches**: Vyhledávání v časových rozmezích
- **Building/floor filtering**: Filtrování podle lokace
- **Quick search**: Rychlé vyhledávání podle klíčových slov

#### 3. Mobile API enhancements
- **Mobile-optimized endpoints**: API optimalizované pro mobilní aplikace
- **Push notifications**: Real-time notifikace
- **Location-based features**: GPS integrace pro nearest spots
- **Quick actions**: Rychlé akce (extend, cancel reservation)

#### 4. Parking lot management
- **Spot categorization**: Různé typy parkovacích míst
- **Building/floor organization**: Hierarchická struktura
- **Maintenance mode**: Dočasné vyřazení míst z provozu
- **Pricing tiers**: Různé cenové kategorie (pokud placené)

**Parking spot model:**
```python
class ParkingSpot:
    id: str
    building: str          # Budova A, B, C
    floor: int            # Patro
    spot_number: str      # Číslo místa
    spot_type: str        # 'regular', 'handicapped', 'electric', 'visitor'
    is_active: bool       # Dostupnost místa
    hourly_rate: float    # Cena za hodinu (volitelné)
```

### 4.3 Implementation Timeline

#### Fáze 1 (1-2 měsíce): High Priority Features
1. Uživatelský management s rolemi
2. Enhanced security implementace
3. Basic audit logging

#### Fáze 2 (2-3 měsíce): Core Enhancements
1. Časové rezervace
2. Email notifikace systém
3. Complete audit logging

#### Fáze 3 (3-4 měsíce): Medium Priority Features
1. Reporting a analytics
2. Pokročilé vyhledávání
3. Parking lot management

#### Fáze 4 (4+ měsíce): Advanced Features
1. Mobile API enhancements
2. Integration capabilities
3. Performance optimizations

---

*Tato dokumentace slouží jako roadmapa pro systematický vývoj robustního parking reservation systému s důrazem na bezpečnost, použitelnost a škálovatelnost.*