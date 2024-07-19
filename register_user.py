from flask import Flask, jsonify
import requests
import json

# Import the Flask app instance from your application
from app import create_app

# Create a Flask app instance
app = create_app()

# Define the API endpoint
url = 'http://127.0.0.1:5000/register'

# Define the user data
user_data = {
    'name': 'Bob Smith',
    'email': 'bob.smith@example.com',
    'username': 'bob_smith',
    'password': 'Password234'
}

def register_user():
    with app.app_context():
        # Send POST request to the /register route
        response = requests.post(url, json=user_data)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:", response.json())

if __name__ == '__main__':
    register_user()
