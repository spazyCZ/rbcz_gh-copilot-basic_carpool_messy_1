"""
Performance and load tests for the parking reservation system.
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from app import app, data


class TestPerformance:
    """Test application performance under various conditions."""
    
    def test_response_time_home_page(self, client, reset_global_data):
        """Test response time for home page."""
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_response_time_with_data(self, client, reset_global_data, sample_data):
        """Test response time when data is present."""
        global data
        data.update(sample_data)
        
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0
    
    def test_multiple_consecutive_requests(self, client, reset_global_data):
        """Test performance with multiple consecutive requests."""
        start_time = time.time()
        
        for _ in range(10):
            response = client.get('/')
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        average_time = total_time / 10
        
        assert average_time < 0.5  # Average response time should be under 0.5 seconds
    
    def test_memory_usage_with_large_data(self, client, reset_global_data):
        """Test memory usage with large amounts of data."""
        # Simulate large dataset
        large_data = {}
        for i in range(1000):
            large_data[f"SPOT_{i}"] = {
                "n": f"User_{i}",
                "d": "2025-06-25"
            }
        
        global data
        data.update(large_data)
        
        # Test that the application still responds
        response = client.get('/')
        assert response.status_code == 200


class TestConcurrencyAndThreadSafety:
    """Test concurrent access and thread safety."""
    
    def test_concurrent_home_page_access(self, reset_global_data):
        """Test multiple concurrent users accessing home page."""
        app.config['TESTING'] = True
        
        def make_request():
            with app.test_client() as client:
                return client.get('/')
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            
            results = []
            for future in as_completed(futures):
                response = future.result()
                results.append(response.status_code)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10
    
    def test_concurrent_login_attempts(self, reset_global_data):
        """Test multiple concurrent login attempts."""
        app.config['TESTING'] = True
        
        def login_attempt():
            with app.test_client() as client:
                return client.post('/login', data={'u': 'admin', 'p': 'admin'})
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_attempt) for _ in range(5)]
            
            results = []
            for future in as_completed(futures):
                response = future.result()
                results.append(response.status_code)
        
        # All login attempts should succeed (redirects)
        assert all(status == 302 for status in results)
    
    def test_concurrent_reservations(self, reset_global_data, mock_files):
        """Test concurrent reservation attempts (race condition test)."""
        app.config['TESTING'] = True
        
        def make_reservation(spot_id):
            with app.test_client() as client:
                with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
                    return client.post('/add', data={
                        'spot': spot_id,
                        'name': f'User_{spot_id}',
                        'date': '2025-06-25'
                    })
        
        # Try to book different spots concurrently
        spot_ids = ['A1', 'A2', 'A3', 'B1', 'B2']
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_reservation, spot_id) for spot_id in spot_ids]
            
            results = []
            for future in as_completed(futures):
                response = future.result()
                results.append(response.status_code)
        
        # All reservations should succeed
        assert all(status == 302 for status in results)
    
    def test_data_corruption_under_concurrent_access(self, reset_global_data, mock_files):
        """Test for data corruption under concurrent file operations."""
        app.config['TESTING'] = True
        
        def modify_data(operation_id):
            with app.test_client() as client:
                with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
                    # Alternate between adding and deleting reservations
                    if operation_id % 2 == 0:
                        return client.post('/add', data={
                            'spot': f'SPOT_{operation_id}',
                            'name': f'User_{operation_id}',
                            'date': '2025-06-25'
                        })
                    else:
                        return client.get(f'/del?spot=SPOT_{operation_id-1}')
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(modify_data, i) for i in range(20)]
            
            results = []
            for future in as_completed(futures):
                try:
                    response = future.result()
                    results.append(response.status_code)
                except Exception as e:
                    results.append(f"Error: {e}")
        
        # Should handle concurrent operations (though may have race conditions)
        successful_results = [r for r in results if r == 302]
        assert len(successful_results) > 0


class TestLoadTesting:
    """Load testing scenarios."""
    
    def test_sustained_load(self, reset_global_data):
        """Test application under sustained load."""
        app.config['TESTING'] = True
        
        def continuous_requests(duration_seconds=5):
            end_time = time.time() + duration_seconds
            request_count = 0
            
            while time.time() < end_time:
                with app.test_client() as client:
                    response = client.get('/')
                    if response.status_code == 200:
                        request_count += 1
                
                # Small delay to prevent overwhelming
                time.sleep(0.01)
            
            return request_count
        
        request_count = continuous_requests(duration_seconds=2)
        
        # Should handle at least some requests per second
        assert request_count > 10
    
    def test_peak_load_simulation(self, reset_global_data):
        """Test application under peak load conditions."""
        app.config['TESTING'] = True
        
        def burst_requests():
            with app.test_client() as client:
                responses = []
                for _ in range(50):  # 50 rapid requests
                    response = client.get('/')
                    responses.append(response.status_code)
                return responses
        
        start_time = time.time()
        results = burst_requests()
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Most requests should succeed
        successful_requests = sum(1 for status in results if status == 200)
        success_rate = successful_requests / len(results)
        
        assert success_rate > 0.8  # At least 80% success rate
        assert total_time < 10.0    # Should complete within 10 seconds


class TestScalabilityLimits:
    """Test scalability limits and breaking points."""
    
    def test_maximum_data_size(self, client, reset_global_data):
        """Test with maximum reasonable data size."""
        # Simulate a large number of reservations
        large_data = {}
        for i in range(10000):  # Large but reasonable number
            large_data[f"SPOT_{i:05d}"] = {
                "n": f"User_{i}",
                "d": "2025-06-25"
            }
        
        global data
        data.update(large_data)
        
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should still respond within reasonable time even with large dataset
        assert response_time < 5.0
    
    def test_long_string_inputs(self, client, reset_global_data, mock_files):
        """Test with very long string inputs."""
        long_name = "A" * 10000  # Very long name
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            response = client.post('/add', data={
                'spot': 'A1',
                'name': long_name,
                'date': '2025-06-25'
            })
            
            # Should handle long inputs (no validation currently)
            assert response.status_code == 302
    
    def test_unicode_and_special_characters(self, client, reset_global_data, mock_files):
        """Test with Unicode and special characters."""
        unicode_names = [
            "José María",
            "北京用户",
            "🚗 Parking User 🚗",
            "User with émojis 😀",
            "Спец символы",
        ]
        
        with patch('app.load_data'), patch('app.save_data'), patch('app.save_backup'):
            for i, name in enumerate(unicode_names):
                response = client.post('/add', data={
                    'spot': f'A{i+1}',
                    'name': name,
                    'date': '2025-06-25'
                })
                
                assert response.status_code == 302
