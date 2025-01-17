import pytest
from flask import json
from datetime import datetime, timedelta
from app import app, airdrops

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_airdrops():
    """Reset the airdrops list before each test"""
    global airdrops
    airdrops[:] = [
        {'id': 1, 'name': 'Airdrop 1', 'claim_deadline': '2025-01-30', 'status': 'Unclaimed'},
        {'id': 2, 'name': 'Airdrop 2', 'claim_deadline': '2025-02-15', 'status': 'Unclaimed'},
    ]
    yield

@pytest.fixture
def sample_airdrop():
    return {
        'name': 'Test Airdrop',
        'claim_deadline': '2025-03-01'
    }

def test_home_route(client):
    """Test the home route returns correct message"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Server is running!" in response.data

def test_get_airdrops(client):
    """Test getting all airdrops"""
    response = client.get('/api/airdrops')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 2  # Should have exactly 2 airdrops after reset
    
    # Verify data structure
    for airdrop in data:
        assert all(key in airdrop for key in ['id', 'name', 'claim_deadline', 'status'])
        # Verify date format (DD MMM YYYY)
        assert datetime.strptime(airdrop['claim_deadline'], '%d %b %Y')

def test_add_airdrop_success(client, sample_airdrop):
    """Test successfully adding a new airdrop"""
    # Get initial count
    initial_response = client.get('/api/airdrops')
    initial_count = len(json.loads(initial_response.data))

    response = client.post(
        '/api/airdrops',
        data=json.dumps(sample_airdrop),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert 'airdrop' in data
    assert data['airdrop']['name'] == sample_airdrop['name']
    
    # Verify the airdrop was actually added
    get_response = client.get('/api/airdrops')
    all_airdrops = json.loads(get_response.data)
    assert len(all_airdrops) == initial_count + 1
    assert any(a['name'] == sample_airdrop['name'] for a in all_airdrops)

def test_add_airdrop_invalid_date(client):
    """Test adding airdrop with invalid date format"""
    invalid_airdrop = {
        'name': 'Invalid Date Airdrop',
        'claim_deadline': '2025/03/01'  # Wrong format
    }
    response = client.post(
        '/api/airdrops',
        data=json.dumps(invalid_airdrop),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Invalid date format' in data['error']

def test_add_airdrop_missing_fields(client):
    """Test adding airdrop with missing required fields"""
    invalid_airdrop = {'name': 'Incomplete Airdrop'}
    response = client.post(
        '/api/airdrops',
        data=json.dumps(invalid_airdrop),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing required field' in data['error']

def test_update_airdrop_success(client):
    """Test successfully updating an existing airdrop"""
    # Update the first airdrop
    update_data = {
        'name': 'Updated Airdrop Name',
        'status': 'Claimed'
    }
    response = client.put(
        '/api/airdrops/1',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['airdrop']['name'] == update_data['name']
    assert data['airdrop']['status'] == update_data['status']

def test_update_nonexistent_airdrop(client):
    """Test updating a non-existent airdrop"""
    response = client.put(
        '/api/airdrops/9999',
        data=json.dumps({'name': 'New Name'}),
        content_type='application/json'
    )
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_delete_airdrop_success(client):
    """Test successfully deleting an airdrop"""
    # Get initial airdrops
    initial_response = client.get('/api/airdrops')
    initial_airdrops = json.loads(initial_response.data)
    assert len(initial_airdrops) > 0
    
    # Delete the first airdrop
    airdrop_id = 1
    response = client.delete(f'/api/airdrops/{airdrop_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'deleted successfully' in data['message'].lower()
    
    # Verify it was deleted
    get_response = client.get('/api/airdrops')
    all_airdrops = json.loads(get_response.data)
    assert len(all_airdrops) == len(initial_airdrops) - 1
    assert not any(a['id'] == airdrop_id for a in all_airdrops)

def test_delete_nonexistent_airdrop(client):
    """Test deleting a non-existent airdrop"""
    response = client.delete('/api/airdrops/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_404_error_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent/route')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data