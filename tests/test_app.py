import os
import tempfile
import json
import pytest
from app import app, PARKING_FILE

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.secret_key = 'testsecret'
    global PARKING_FILE
    PARKING_FILE_OLD = PARKING_FILE
    PARKING_FILE = db_path
    with app.test_client() as client:
        yield client
    os.close(db_fd)
    os.remove(db_path)
    PARKING_FILE = PARKING_FILE_OLD

def login(client):
    return client.post('/', data={'u': 'admin', 'p': 'admin'}, follow_redirects=True)

def test_hello_world():
    assert 1 + 1 == 2

def test_login_logout(client):
    rv = client.get('/')
    assert b'User:' in rv.data
    rv = login(client)
    assert b'Parking' in rv.data
    rv = client.get('/logout', follow_redirects=True)
    assert b'User:' in rv.data

def test_add_reservation(client):
    login(client)
    rv = client.post('/add', data={'pl': 'A1', 'nm': 'Alice'}, follow_redirects=True)
    assert b'A2' in rv.data
    # Try to add the same place again
    rv = client.post('/add', data={'pl': 'A1', 'nm': 'Bob'}, follow_redirects=True)
    assert b'Already reserved' in rv.data

def test_edit_reservation(client):
    login(client)
    client.post('/add', data={'pl': 'B2', 'nm': 'Bob'}, follow_redirects=True)
    rv = client.post('/edit/B2', data={'nm': 'Bobby'}, follow_redirects=True)
    assert b'Bobby' in rv.data

def test_delete_reservation(client):
    login(client)
    client.post('/add', data={'pl': 'C3', 'nm': 'Carol'}, follow_redirects=True)
    rv = client.get('/del/C3', follow_redirects=True)
    assert b'C3' not in rv.data

def test_api_create_list_update_delete(client):
    login(client)
    # Create
    rv = client.post('/create', json={'place': 'D4', 'name': 'Dan'})
    assert rv.status_code == 200
    # List
    rv = client.get('/list')
    data = rv.get_json()
    assert 'D4' in data
    # Update
    rv = client.put('/update', json={'place': 'D4', 'name': 'Danny'})
    assert rv.status_code == 200
    rv = client.get('/list')
    data = rv.get_json()
    assert data['D4']['name'] == 'Danny'
    # Delete
    rv = client.delete('/delete', json={'place': 'D4'})
    assert rv.status_code == 200
    rv = client.get('/list')
    data = rv.get_json()
    assert 'D4' not in data

def test_api_create_duplicate(client):
    login(client)
    client.post('/create', json={'place': 'E5', 'name': 'Eve'})
    rv = client.post('/create', json={'place': 'E5', 'name': 'Eve2'})
    assert rv.status_code == 400
    assert b'Place already reserved' in rv.data

def test_api_update_not_found(client):
    login(client)
    rv = client.put('/update', json={'place': 'F6', 'name': 'Frank'})
    assert rv.status_code == 404

def test_api_delete_not_found(client):
    login(client)
    rv = client.delete('/delete', json={'place': 'G7'})
    assert rv.status_code == 404