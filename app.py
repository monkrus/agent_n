from flask import Flask, jsonify, request
from flask import render_template
from flask_cors import CORS
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Sample data to simulate a database
airdrops = [
    {'id': 1, 'name': 'Airdrop 1', 'claim_deadline': '2025-01-30', 'status': 'Unclaimed'},
    {'id': 2, 'name': 'Airdrop 2', 'claim_deadline': '2025-02-15', 'status': 'Unclaimed'},
]

# Add new route for dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# Route: Home
@app.route('/')
def home():
    return "Server is running!"

# Helper function to validate and format claim_deadline
def validate_and_format_deadline(deadline):
    try:
        return datetime.strptime(deadline, '%Y-%m-%d').strftime('%d %b %Y')
    except ValueError:
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

# Helper function to format airdrops
def format_airdrops():
    return [
        {**airdrop, 'claim_deadline': validate_and_format_deadline(airdrop['claim_deadline'])}
        for airdrop in airdrops
    ]

# Helper function to generate a new ID
def generate_new_id():
    existing_ids = [airdrop['id'] for airdrop in airdrops]
    return max(existing_ids) + 1 if existing_ids else 1

# Route: Get all airdrops
@app.route('/api/airdrops', methods=['GET'])
def get_airdrops():
    try:
        formatted_airdrops = format_airdrops()
        return jsonify(formatted_airdrops)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Add a new airdrop
@app.route('/api/airdrops', methods=['POST'])
def add_airdrop():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'claim_deadline']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        new_airdrop = {
            'id': generate_new_id(),
            'name': data['name'],
            'claim_deadline': data['claim_deadline'],  # Store original format
            'status': 'Unclaimed'
        }
        airdrops.append(new_airdrop)
        
        # Format the airdrop for response
        formatted_airdrop = {**new_airdrop, 'claim_deadline': validate_and_format_deadline(new_airdrop['claim_deadline'])}
        return jsonify({'message': 'Airdrop added successfully', 'airdrop': formatted_airdrop}), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Update an airdrop
@app.route('/api/airdrops/<int:airdrop_id>', methods=['PUT'])
def update_airdrop(airdrop_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        airdrop = next((a for a in airdrops if a['id'] == airdrop_id), None)
        if not airdrop:
            return jsonify({'error': 'Airdrop not found'}), 404

        if 'claim_deadline' in data:
            # Validate the new deadline before updating
            validate_and_format_deadline(data['claim_deadline'])
            airdrop['claim_deadline'] = data['claim_deadline']  # Store original format

        if 'name' in data:
            airdrop['name'] = data['name']
        if 'status' in data:
            airdrop['status'] = data['status']

        # Format the airdrop for response
        formatted_airdrop = {**airdrop, 'claim_deadline': validate_and_format_deadline(airdrop['claim_deadline'])}
        return jsonify({'message': 'Airdrop updated successfully', 'airdrop': formatted_airdrop}), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Delete an airdrop
@app.route('/api/airdrops/<int:airdrop_id>', methods=['DELETE'])
def delete_airdrop(airdrop_id):
    try:
        airdrop = next((a for a in airdrops if a['id'] == airdrop_id), None)
        if not airdrop:
            return jsonify({'error': 'Airdrop not found'}), 404

        airdrops[:] = [a for a in airdrops if a['id'] != airdrop_id]
        return jsonify({'message': 'Airdrop deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'The requested URL was not found on the server.'}), 404

if __name__ == '__main__':
    app.run(debug=True)