"""
Integration tests for the parking reservation system.
Tests the complete workflow and interactions between components.
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch

from app import app, data, spots, users


class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    def test_complete_reservation_workflow(self, client, mock_files, reset_global_data):
        """Test complete workflow: login -> view spots -> make reservation -> logout."""
        # Step 1: Login
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        assert response.status_code == 302
        
        # Step 2: View home page (should show spots)
        response = client.get('/')
        assert response.status_code == 200
        assert b'Available Spots:' in response.data
        
        # Step 3: Make a reservation
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Integration Test User',
                'date': '2025-06-30'
            })
            assert response.status_code == 302
        
        # Step 4: Quick book another spot
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/book?spot=B1')
            assert response.status_code == 302
        
        # Step 5: Delete a reservation
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/del?spot=A1')
            assert response.status_code == 302
        
        # Step 6: Logout
        response = client.get('/logout')
        assert response.status_code == 302
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert sess.get('user') is None
    
    def test_unauthenticated_user_workflow(self, client, reset_global_data):
        """Test workflow for unauthenticated user."""
        # Step 1: Try to access home page without login
        response = client.get('/')
        assert response.status_code == 200
        assert b'Username:' in response.data  # Should show login form
        
        # Step 2: Try to make reservation without authentication
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Unauthorized User',
                'date': '2025-06-30'
            })
            # Currently allows unauthorized access (security bug)
            assert response.status_code == 302
    
    def test_admin_workflow(self, client, mock_files, reset_global_data):
        """Test admin-specific workflow."""
        # Login as admin
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        assert response.status_code == 302
        
        # Access admin page
        with patch('app.load_data'):
            response = client.get('/admin')
            assert response.status_code == 200
            assert b'<pre>' in response.data
        
        # Access debug page (should be restricted in production)
        response = client.get('/debug')
        assert response.status_code == 200
        assert b'Debug Info' in response.data


class TestDataPersistence:
    """Test data persistence and file operations."""
    
    def test_data_persistence_across_requests(self, client, temp_dir, reset_global_data):
        """Test that data persists across multiple requests."""
        # Create test files
        data_file = os.path.join(temp_dir, 'test_data.json')
        backup_file = os.path.join(temp_dir, 'test_backup.json')
        log_file = os.path.join(temp_dir, 'test_actions.json')
        
        initial_data = {"A1": {"n": "Test User", "d": "2025-06-25"}}
        
        # Write initial data
        with open(data_file, 'w') as f:
            json.dump(initial_data, f)
        
        with patch('app.file_path', data_file), \
             patch('app.backup_file', backup_file), \
             patch('app.log_file', log_file):
            
            # First request - should load existing data
            response = client.get('/')
            assert response.status_code == 200
            
            # Add new reservation
            response = client.post('/add', data={
                'spot': 'B1',
                'name': 'New User',
                'date': '2025-06-26'
            })
            assert response.status_code == 302
            
            # Verify data was saved
            with open(data_file, 'r') as f:
                saved_data = json.load(f)
                assert 'A1' in saved_data  # Original data preserved
                assert 'B1' in saved_data  # New data added
    
    def test_backup_creation(self, client, temp_dir, reset_global_data):
        """Test that backups are created properly."""
        data_file = os.path.join(temp_dir, 'test_data.json')
        backup_file = os.path.join(temp_dir, 'test_backup.json')
        log_file = os.path.join(temp_dir, 'test_actions.json')
        
        with patch('app.file_path', data_file), \
             patch('app.backup_file', backup_file), \
             patch('app.log_file', log_file):
            
            # Make a reservation (triggers backup)
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Backup Test User',
                'date': '2025-06-25'
            })
            assert response.status_code == 302
            
            # Verify backup file exists and contains data
            assert os.path.exists(backup_file)
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
                assert 'A1' in backup_data
    
    def test_file_corruption_handling(self, client, temp_dir, reset_global_data):
        """Test handling of corrupted data files."""
        data_file = os.path.join(temp_dir, 'corrupted_data.json')
        
        # Create corrupted JSON file
        with open(data_file, 'w') as f:
            f.write('{ invalid json content }')
        
        with patch('app.file_path', data_file):
            # Should handle corruption gracefully
            response = client.get('/')
            assert response.status_code == 200


class TestConcurrency:
    """Test concurrent access scenarios."""
    
    def test_multiple_simultaneous_bookings(self, client, mock_files, reset_global_data):
        """Test multiple bookings happening simultaneously."""
        # This test documents the race condition vulnerability
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            # Simulate two users booking the same spot simultaneously
            response1 = client.post('/add', data={
                'spot': 'A1',
                'name': 'User 1',
                'date': '2025-06-25'
            })
            
            response2 = client.post('/add', data={
                'spot': 'A1',  # Same spot
                'name': 'User 2',
                'date': '2025-06-26'
            })
            
            # Both should succeed (documenting the bug)
            assert response1.status_code == 302
            assert response2.status_code == 302


class TestSecurityVulnerabilities:
    """Test security vulnerabilities in the application."""
    
    def test_session_security(self, client):
        """Test session security issues."""
        # Test weak secret key
        assert app.secret_key == "123"  # Documents security vulnerability
    
    def test_plaintext_passwords(self):
        """Test that passwords are stored in plaintext."""
        # Documents security vulnerability
        assert users["admin"] == "admin"
        assert users["user"] == "pass"
    
    def test_sql_injection_prevention(self, client, mock_files, reset_global_data):
        """Test SQL injection prevention (not applicable but good practice)."""
        # Since we're using JSON files, SQL injection isn't possible,
        # but we can test for JSON injection/manipulation
        
        malicious_input = '{"malicious": "data"}'
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': malicious_input,
                'date': '2025-06-25'
            })
            
            # Should accept the input (no sanitization currently)
            assert response.status_code == 302
    
    def test_xss_vulnerability(self, client, reset_global_data):
        """Test XSS vulnerability in templates."""
        xss_payload = '<script>alert("XSS")</script>'
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': xss_payload,
                'date': '2025-06-25'
            })
            
            assert response.status_code == 302
            
            # The XSS payload would be rendered without escaping (vulnerability)
    
    def test_unauthorized_access_to_admin_routes(self, client):
        """Test that admin routes can be accessed without proper authentication."""
        # Should require admin authentication but doesn't
        response = client.get('/admin')
        assert response.status_code == 200  # Documents the vulnerability
        
        response = client.get('/debug')
        assert response.status_code == 200  # Documents the vulnerability


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""
    
    def test_invalid_form_data(self, client, reset_global_data):
        """Test handling of invalid form data."""
        # Test missing required fields
        with pytest.raises(Exception):  # Should raise KeyError
            client.post('/add', data={'spot': 'A1'})  # Missing name and date
    
    def test_invalid_spot_deletion(self, client, mock_files, reset_global_data):
        """Test deleting non-existent spots."""
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/del?spot=NONEXISTENT')
            assert response.status_code == 302  # Should handle gracefully
    
    def test_file_permission_errors(self, client, mock_files, reset_global_data):
        """Test handling of file permission errors."""
        with patch('app.save_data', side_effect=PermissionError("Permission denied")):
            with patch('app.load_data'):
                # Should not crash the application
                response = client.post('/add', data={
                    'spot': 'A1',
                    'name': 'Test User',
                    'date': '2025-06-25'
                })
                assert response.status_code == 302
    
    def test_disk_space_errors(self, client, mock_files, reset_global_data):
        """Test handling of disk space errors."""
        with patch('app.save_data', side_effect=OSError("No space left on device")):
            with patch('app.load_data'):
                response = client.post('/add', data={
                    'spot': 'A1',
                    'name': 'Test User',
                    'date': '2025-06-25'
                })
                assert response.status_code == 302
