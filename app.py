from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/api/airdrops')  # Removed methods=['GET'] to test if this is the issue
def get_airdrops():
    print("Accessing airdrops route - function called")  # Debug print
    try:
        airdrops = [
            {'name': 'Airdrop 1', 'claim_deadline': '2025-01-30', 'status': 'Unclaimed'},
            {'name': 'Airdrop 2', 'claim_deadline': '2025-02-15', 'status': 'Unclaimed'},
        ]
        response = jsonify(airdrops)
        print("Data prepared:", airdrops)  # Debug print
        return response
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    print(f"404 error: {error}")  # Debug print
    return jsonify({'error': 'Not Found', 'message': 'The requested URL was not found on the server.'}), 404

if __name__ == '__main__':
    print("Starting Flask server...")  # Debug print
    app.run(debug=True)