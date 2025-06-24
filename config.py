# BAD: Empty config file with wrong extension
# This should be a .env or .ini file but it's .py

DATA_FILE = "reservations.json"        # BAD: Hardcoded file path
BACKUP_FILE = "backup_data.json"       # BAD: Not used anywhere
SECRET_KEY = "super_secret_key_123"    # BAD: Not actually secret
DEBUG = True                           # BAD: Debug mode in config
ADMIN_EMAIL = "admin@example.com"      # BAD: Unused configuration
