from flask import Flask, request, jsonify, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongodb:27017/HospitalDB"
app.secret_key = 'your_secret_key'
mongo = PyMongo(app)

# Registration of Users
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    user = {
        "onoma": data['onoma'],
        "eponimo": data['eponimo'],
        "email": data['email'],
        "username": data['username'],
        "password": hashed_password,
        "role": "user"  # Default role is user
    }

    if mongo.db.users.find_one({"username": user['username']}) or mongo.db.users.find_one({"email": user['email']}):
        return jsonify({"message": "Username or Email already exists!"}), 409
    
    mongo.db.users.insert_one(user)
    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({"username": data['username']})

    if user and check_password_hash(user['password'], data['password']):
        session['user'] = str(user['_id'])
        session['role'] = user['role']
        return jsonify({"message": "Login successful!"}), 200
    
    return jsonify({"message": "Invalid username or password!"}), 401

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return jsonify({"message": "Logout successful!"}), 200

# Create Event
@app.route('/events', methods=['POST'])
def create_event():
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    data = request.json
    event = {
        "titlos_ekdilosis": data['titlos_ekdilosis'],
        "perigrafi_ekdilosis": data['perigrafi_ekdilosis'],
        "imerominia": data['imerominia'],
        "ora": data['ora'],
        "meros": data['meros'],
        "typos_ekdilosis": data['typos_ekdilosis'],
        "dimiourgos_id": session['user']
    }
    mongo.db.events.insert_one(event)
    return jsonify({"message": "Event created successfully!"}), 201

# View All Events
@app.route('/events', methods=['GET'])
def view_all_events():
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    events = list(mongo.db.events.find({"imerominia": {"$gte": request.args.get('today')}}))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events), 200

# View User's Created Events
@app.route('/my-events', methods=['GET'])
def view_my_events():
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    events = list(mongo.db.events.find({"dimiourgos_id": session['user']}))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events), 200

# Update Event Information
@app.route('/events/<id>', methods=['PUT'])
def update_event(id):
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    data = request.json
    mongo.db.events.update_one(
        {"_id": ObjectId(id), "dimiourgos_id": session['user']},
        {"$set": {
            "titlos_ekdilosis": data['titlos_ekdilosis'],
            "perigrafi_ekdilosis": data['perigrafi_ekdilosis'],
            "imerominia": data['imerominia'],
            "ora": data['ora'],
            "meros": data['meros'],
            "typos_ekdilosis": data['typos_ekdilosis']
        }}
    )
    return jsonify({"message": "Event updated successfully!"}), 200

# Delete Event
@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    event = mongo.db.events.find_one({"_id": ObjectId(id)})

    if session['role'] == "admin" or (event and event['dimiourgos_id'] == session['user']):
        mongo.db.events.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Event deleted successfully!"}), 200

    return jsonify({"message": "Unauthorized action!"}), 403

# Search Events
@app.route('/search', methods=['GET'])
def search_events():
    if 'user' not in session:
        return jsonify({"message": "Please log in first!"}), 403

    criteria = {
        "titlos_ekdilosis": request.args.get('titlos_ekdilosis'),
        "typos_ekdilosis": request.args.get('typos_ekdilosis'),
        "meros": request.args.get('meros')
    }
    search_query = {k: v for k, v in criteria.items() if v}
    
    events = list(mongo.db.events.find(search_query))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
