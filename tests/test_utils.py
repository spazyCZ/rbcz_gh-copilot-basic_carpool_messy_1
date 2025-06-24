"""
Unit tests for utility functions.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

from utils import (
    generate_random_string, 
    validate_user_input, 
    get_parking_spots, 
    log_action,
    CONFIG
)


class TestUtilityFunctions:
    """Test utility functions from utils.py."""
    
    def test_generate_random_string_length(self):
        """Test that random string has correct length."""
        result = generate_random_string()
        assert len(result) == 10
    
    def test_generate_random_string_uniqueness(self):
        """Test that multiple calls generate different strings."""
        results = [generate_random_string() for _ in range(10)]
        # Check that all strings are unique
        assert len(set(results)) == len(results)
    
    def test_generate_random_string_characters(self):
        """Test that random string contains only valid characters."""
        import string
        valid_chars = string.ascii_letters + string.digits
        result = generate_random_string()
        
        for char in result:
            assert char in valid_chars
    
    def test_validate_user_input_always_true(self):
        """Test that validate_user_input always returns True (bug)."""
        # Test with various inputs - should all return True (documenting the bug)
        assert validate_user_input("valid input") is True
        assert validate_user_input("") is True
        assert validate_user_input(None) is True
        assert validate_user_input(123) is True
        assert validate_user_input([]) is True
        assert validate_user_input({}) is True
    
    def test_get_parking_spots_returns_config_spots(self):
        """Test that get_parking_spots returns spots from CONFIG."""
        expected_spots = CONFIG["spots"]
        result = get_parking_spots()
        assert result == expected_spots
        assert isinstance(result, list)
    
    def test_get_parking_spots_immutability(self):
        """Test that modifying returned spots doesn't affect CONFIG."""
        spots = get_parking_spots()
        original_length = len(spots)
        spots.append("NEW_SPOT")
        
        # Get spots again to verify CONFIG wasn't modified
        new_spots = get_parking_spots()
        assert len(new_spots) == original_length
    
    def test_log_action_file_creation(self, temp_dir):
        """Test that log_action creates and writes to log file."""
        log_file_path = os.path.join(temp_dir, "test_log.txt")
        test_action = "test_action_performed"
        
        with patch('utils.open', mock_open()) as mock_file:
            with patch('builtins.print'):  # Suppress print output
                log_action(test_action)
        
        # Verify file was opened for appending
        mock_file.assert_called_once_with("log.txt", "a")
        # Verify correct content was written
        mock_file().write.assert_called_once_with(f"{test_action}\n")
    
    def test_log_action_print_called(self, capsys):
        """Test that log_action prints to stdout."""
        test_action = "test_action_for_print"
        
        with patch('builtins.open', mock_open()):
            log_action(test_action)
        
        captured = capsys.readouterr()
        assert f"Logged: {test_action}" in captured.out
    
    def test_config_structure(self):
        """Test that CONFIG has expected structure."""
        assert isinstance(CONFIG, dict)
        assert "spots" in CONFIG
        assert "admin_pass" in CONFIG
        assert isinstance(CONFIG["spots"], list)
        assert isinstance(CONFIG["admin_pass"], str)
    
    def test_config_spots_content(self):
        """Test that CONFIG spots contain expected values."""
        expected_spots = ["A1", "A2", "A3", "B1", "B2", "B3"]
        assert CONFIG["spots"] == expected_spots
    
    def test_config_admin_password(self):
        """Test CONFIG admin password (security issue documentation)."""
        # This documents the security vulnerability
        assert CONFIG["admin_pass"] == "admin123"
        # Password is hardcoded and insecure


class TestUtilityIntegration:
    """Integration tests for utility functions."""
    
    def test_log_action_with_real_file(self, temp_dir):
        """Test log_action with actual file I/O."""
        original_cwd = os.getcwd()
        try:
            # Change to temp directory
            os.chdir(temp_dir)
            
            test_action = "integration_test_action"
            
            with patch('builtins.print'):  # Suppress print output
                log_action(test_action)
            
            # Verify file was created and contains expected content
            log_file = os.path.join(temp_dir, "log.txt")
            assert os.path.exists(log_file)
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert f"{test_action}\n" in content
        
        finally:
            os.chdir(original_cwd)
    
    def test_multiple_log_actions(self, temp_dir):
        """Test multiple log actions append correctly."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            actions = ["action1", "action2", "action3"]
            
            with patch('builtins.print'):
                for action in actions:
                    log_action(action)
            
            log_file = os.path.join(temp_dir, "log.txt")
            with open(log_file, 'r') as f:
                content = f.read()
                
                for action in actions:
                    assert f"{action}\n" in content
                
                # Check that actions are in order
                lines = content.strip().split('\n')
                for i, action in enumerate(actions):
                    assert lines[i] == action
        
        finally:
            os.chdir(original_cwd)


class TestErrorHandling:
    """Test error handling in utility functions."""
    
    def test_log_action_file_permission_error(self):
        """Test log_action behavior when file can't be written."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with patch('builtins.print'):
                # Should not raise exception, but file operation will fail
                try:
                    log_action("test_action")
                except PermissionError:
                    pytest.fail("log_action should handle file errors gracefully")
    
    def test_get_parking_spots_config_modification(self):
        """Test behavior when CONFIG is modified."""
        original_spots = CONFIG["spots"].copy()
        
        try:
            # Modify CONFIG
            CONFIG["spots"] = ["X1", "X2"]
            
            result = get_parking_spots()
            assert result == ["X1", "X2"]
        
        finally:
            # Restore original CONFIG
            CONFIG["spots"] = original_spots
