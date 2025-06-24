"""
Unit tests for Flask routes and basic application functionality.
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open

from app import app, data, load_data, save_data, load_backup, save_backup


class TestRoutes:
    """Test Flask application routes."""
    
    def test_home_route_without_authentication(self, client, reset_global_data):
        """Test home page without authentication shows login form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Username:' in response.data
        assert b'Password:' in response.data
        assert b'LOGIN' in response.data
    
    def test_home_route_with_authentication(self, authenticated_session, reset_global_data):
        """Test home page with authentication shows parking spots."""
        response = authenticated_session.get('/')
        assert response.status_code == 200
        assert b'Welcome admin!' in response.data
        assert b'Available Spots:' in response.data
        assert b'Logout' in response.data
    
    def test_login_success(self, client):
        """Test successful login with valid credentials."""
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        assert response.status_code == 302  # Redirect
        assert response.location == '/'
        
        # Check if session is set
        with client.session_transaction() as sess:
            assert sess.get('user') == 'admin'
    
    def test_login_failure(self, client):
        """Test login failure with invalid credentials."""
        response = client.post('/login', data={'u': 'invalid', 'p': 'wrong'})
        assert response.status_code == 302
        
        # Check if session is not set
        with client.session_transaction() as sess:
            assert sess.get('user') is None
    
    def test_logout(self, authenticated_session):
        """Test logout functionality."""
        response = authenticated_session.get('/logout')
        assert response.status_code == 302
        
        # Check if session is cleared
        with authenticated_session.session_transaction() as sess:
            assert sess.get('user') is None
    
    def test_add_reservation(self, client, reset_global_data, mock_files):
        """Test adding a new reservation."""
        # Mock successful file operations
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Test User',
                'date': '2025-06-25'
            })
            
            assert response.status_code == 302
            assert response.location == '/'
    
    def test_book_spot(self, client, reset_global_data, mock_files):
        """Test quick booking functionality."""
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/book?spot=A1')
            assert response.status_code == 302
            assert response.location == '/'
    
    def test_delete_reservation(self, client, reset_global_data, mock_files):
        """Test deleting a reservation."""
        # Set up initial data
        global data
        data['A1'] = {'n': 'Test User', 'd': '2025-06-25'}
        
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/del?spot=A1')
            assert response.status_code == 302
            assert response.location == '/'
    
    def test_admin_route(self, client, reset_global_data, mock_files):
        """Test admin route (should be protected but isn't)."""
        with patch('app.load_data'):
            response = client.get('/admin')
            assert response.status_code == 200
            assert b'<pre>' in response.data
            assert b'Back' in response.data
    
    def test_debug_route(self, client):
        """Test debug route (should not exist in production)."""
        response = client.get('/debug')
        assert response.status_code == 200
        assert b'Debug Info' in response.data
        assert b'Users:' in response.data
        assert b'Data:' in response.data
    
    def test_404_error_handler(self, client):
        """Test custom 404 error handler."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        assert b'404 Error' in response.data
        assert b'Path not found:' in response.data


class TestDataHandling:
    """Test data loading and saving functions."""
    
    def test_load_data_file_exists(self, mock_files, sample_data):
        """Test loading data when file exists."""
        # Create test file with sample data
        with open(mock_files['data_file'], 'w') as f:
            json.dump(sample_data, f)
        
        global data
        data.clear()
        
        with patch('app.file_path', mock_files['data_file']):
            load_data()
            assert data == sample_data
    
    def test_load_data_file_not_exists(self, mock_files):
        """Test loading data when file doesn't exist."""
        global data
        data.clear()
        
        with patch('app.file_path', mock_files['data_file']):
            load_data()
            assert data == {}
    
    def test_load_data_invalid_json(self, mock_files):
        """Test loading data with invalid JSON."""
        # Create file with invalid JSON
        with open(mock_files['data_file'], 'w') as f:
            f.write('invalid json content')
        
        global data
        data.clear()
        
        with patch('app.file_path', mock_files['data_file']):
            load_data()
            assert data == {}
    
    def test_save_data_success(self, mock_files, sample_data):
        """Test saving data successfully."""
        global data
        data.update(sample_data)
        
        with patch('app.file_path', mock_files['data_file']):
            save_data()
            
            # Verify file was created and contains correct data
            assert os.path.exists(mock_files['data_file'])
            with open(mock_files['data_file'], 'r') as f:
                saved_data = json.load(f)
                assert saved_data == sample_data
    
    def test_load_backup_success(self, mock_files, sample_data):
        """Test loading backup data successfully."""
        # Create backup file
        with open(mock_files['backup_file'], 'w') as f:
            json.dump(sample_data, f)
        
        with patch('app.backup_file', mock_files['backup_file']):
            backup_data = load_backup()
            assert backup_data == sample_data
    
    def test_load_backup_file_not_exists(self, mock_files):
        """Test loading backup when file doesn't exist."""
        with patch('app.backup_file', mock_files['backup_file']):
            backup_data = load_backup()
            assert backup_data == {}
    
    def test_save_backup_success(self, mock_files, sample_data):
        """Test saving backup successfully."""
        global data
        data.update(sample_data)
        
        with patch('app.backup_file', mock_files['backup_file']), \
             patch('app.log_file', mock_files['log_file']):
            save_backup()
            
            # Verify backup file was created
            assert os.path.exists(mock_files['backup_file'])
            with open(mock_files['backup_file'], 'r') as f:
                backup_data = json.load(f)
                assert backup_data == sample_data


class TestBusinessLogic:
    """Test business logic and edge cases."""
    
    def test_double_booking_allowed(self, client, reset_global_data, mock_files):
        """Test that double booking is currently allowed (bug)."""
        global data
        data['A1'] = {'n': 'First User', 'd': '2025-06-25'}
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            # Try to book the same spot again
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Second User',
                'date': '2025-06-26'
            })
            
            assert response.status_code == 302
            # This test documents the current bug - double booking is allowed
    
    def test_missing_form_data(self, client, reset_global_data):
        """Test handling of missing form data."""
        with pytest.raises(Exception):  # Should raise KeyError for missing form fields
            client.post('/add', data={'spot': 'A1'})  # Missing name and date
    
    def test_invalid_spot_id(self, client, reset_global_data, mock_files):
        """Test booking with invalid spot ID."""
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'INVALID',
                'name': 'Test User',
                'date': '2025-06-25'
            })
            
            assert response.status_code == 302
            # Currently no validation, so invalid spots are accepted (bug)
    
    def test_delete_nonexistent_reservation(self, client, reset_global_data, mock_files):
        """Test deleting a reservation that doesn't exist."""
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/del?spot=NONEXISTENT')
            assert response.status_code == 302
            # Should handle gracefully (currently does with try/except)
    
    def test_authentication_bypass(self, client, reset_global_data, mock_files):
        """Test that routes don't check authentication (security issue)."""
        # Should require authentication but doesn't
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Unauthorized User',
                'date': '2025-06-25'
            })
            
            assert response.status_code == 302
            # This documents the security vulnerability
