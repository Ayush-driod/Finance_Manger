from flask import Flask, render_template, request, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "transactions.json")

def load_data():
    """Load transactions from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []

def save_data(data):
    """Save transactions to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    data = load_data()
    # Sort by date descending
    data.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(data)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = load_data()
    req_data = request.json
    
    try:
        amount = float(req_data.get('amount', 0))
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
            
        date_str = req_data.get('date')
        datetime.strptime(date_str, "%Y-%m-%d") # Validate date format
        
        record = {
            "id": str(uuid.uuid4()),
            "date": date_str,
            "amount": amount,
            "type": req_data.get('type'),
            "category": req_data.get('category', '').strip(),
            "description": req_data.get('description', '').strip()
        }
        
        data.append(record)
        save_data(data)
        
        return jsonify({'message': 'Transaction added successfully', 'transaction': record}), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid date or amount format'}), 400

@app.route('/api/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = load_data()
    req_data = request.json
    
    for i, transaction in enumerate(data):
        if transaction['id'] == transaction_id:
            try:
                amount = float(req_data.get('amount', 0))
                if amount <= 0:
                    return jsonify({'error': 'Amount must be greater than zero'}), 400
                    
                date_str = req_data.get('date')
                datetime.strptime(date_str, "%Y-%m-%d") # Validate date format
                
                # Update record while preserving the ID
                record = {
                    "id": transaction_id,
                    "date": date_str,
                    "amount": amount,
                    "type": req_data.get('type'),
                    "category": req_data.get('category', '').strip(),
                    "description": req_data.get('description', '').strip()
                }
                
                data[i] = record
                save_data(data)
                
                return jsonify({'message': 'Transaction updated successfully', 'transaction': record}), 200
                
            except ValueError:
                return jsonify({'error': 'Invalid date or amount format'}), 400
                
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    data = load_data()
    
    for i, transaction in enumerate(data):
        if transaction['id'] == transaction_id:
            del data[i]
            save_data(data)
            return jsonify({'message': 'Transaction deleted successfully'}), 200
            
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/api/summary', methods=['GET'])
def get_summary():
    data = load_data()
    
    total_income = sum(item['amount'] for item in data if item['type'] == 'income')
    total_expense = sum(item['amount'] for item in data if item['type'] == 'expense')
    balance = total_income - total_expense
    
    expenses_by_category = {}
    for item in data:
        if item['type'] == 'expense':
            category = item['category']
            expenses_by_category[category] = expenses_by_category.get(category, 0) + item['amount']
            
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'expenses_by_category': expenses_by_category
    })

if __name__ == '__main__':
    app.run(debug=True, port=3000)
