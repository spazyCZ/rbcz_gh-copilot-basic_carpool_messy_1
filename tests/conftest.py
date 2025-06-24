"""
Test configuration and fixtures for the parking reservation system tests.
"""
import pytest
import tempfile
import os
import json
import shutil
from unittest.mock import patch

# Import the Flask app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, data, spots, users


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_files(temp_dir, monkeypatch):
    """Mock file paths to use temporary directory."""
    test_data_file = os.path.join(temp_dir, 'test_data.json')
    test_backup_file = os.path.join(temp_dir, 'test_backup.json')
    test_log_file = os.path.join(temp_dir, 'test_actions.json')
    test_user_file = os.path.join(temp_dir, 'test_users.json')
    
    # Patch global variables
    monkeypatch.setattr('app.file_path', test_data_file)
    monkeypatch.setattr('app.backup_file', test_backup_file)
    monkeypatch.setattr('app.log_file', test_log_file)
    monkeypatch.setattr('app.user_file', test_user_file)
    
    return {
        'data_file': test_data_file,
        'backup_file': test_backup_file,
        'log_file': test_log_file,
        'user_file': test_user_file
    }


@pytest.fixture
def sample_data():
    """Sample reservation data for testing."""
    return {
        "A1": {"n": "John Doe", "d": "2025-06-25"},
        "B2": {"n": "Jane Smith", "d": "2025-06-26"}
    }


@pytest.fixture
def authenticated_session(client):
    """Create an authenticated session."""
    with client.session_transaction() as sess:
        sess['user'] = 'admin'
    return client


@pytest.fixture
def reset_global_data():
    """Reset global data state before each test."""
    global data
    original_data = data.copy()
    data.clear()
    yield
    data.clear()
    data.update(original_data)


@pytest.fixture
def sample_parking_config():
    """Sample parking configuration data."""
    return {
        "parking_spots": [
            {"id": "A1", "status": "free", "location": "Level A"},
            {"id": "A2", "status": "free", "location": "Level A"},
            {"id": "B1", "status": "free", "location": "Level B"},
            {"id": "B2", "status": "reserved", "location": "Level B"}
        ],
        "settings": {
            "max_reservations": 10,
            "admin_email": "admin@parking.com"
        }
    }


@pytest.fixture
def sample_users():
    """Sample users data for testing."""
    return {
        "users": {
            "admin": {
                "password": "admin123",
                "role": "administrator",
                "email": "admin@example.com"
            },
            "testuser": {
                "password": "testpass",
                "role": "user",
                "email": "test@example.com"
            }
        }
    }
