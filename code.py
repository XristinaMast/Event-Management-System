from flask import Flask, request, jsonify, session, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongodb:27017/DigiMeet"
app.secret_key = 'SecretKey/DidntSeeThatComingHUH?'
mongo = PyMongo(app)

# Admin Registration
@app.route('/admin-register', methods=['POST'])
def admin_setting():
    admin_user = mongo.db.users.find_one({'username': 'admin'})
    if not admin_user:
        admin = {
            "first_name": 'Admin',
            "last_name": 'user',
            "email": 'admin@user.com',
            "username": 'admin',
            "password": generate_password_hash("@dm!n69%", method='sha256'),
            "role": "admin"
        }
        mongo.db.users.insert_one(admin)
        return Response("Admin registered successfully!", status=201, mimetype="application/json")
    return Response("Admin already exists!", status=400, mimetype="application/json")

# Registration of Users
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    user = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "username": data['username'],
        "password": hashed_password,
        "role": "user"
    }

    if mongo.db.users.find_one({"username": user['username']}) or mongo.db.users.find_one({"email": user['email']}):
        return Response("Username or Email already exists!", status=409, mimetype="application/json")
    
    try:
        mongo.db.users.insert_one(user)
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

    return Response("User registered successfully!", status=201, mimetype="application/json")

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({"username": data['username']})

    if user and check_password_hash(user['password'], data['password']):
        session['user'] = str(user['_id'])
        session['role'] = user['role']
        return Response("Login successful!", status=200, mimetype="application/json")
    
    return Response("Invalid username or password!", status=401, mimetype="application/json")

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return Response("Logout successful!", status=200, mimetype="application/json")

# Create Event
@app.route('/events', methods=['POST'])
def create_event():
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    data = request.json
    event = {
        "event_title": data['event_title'],
        "event_description": data['event_description'],
        "event_date": data['event_date'],
        "event_hour": data['event_hour'],
        "event_placement": data['event_placement'],
        "event_type": data['event_type'],
        "event_creator_id": session['user']
    }
    
    try:
        mongo.db.events.insert_one(event)
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

    return Response("Event created successfully!", status=201, mimetype="application/json")

# View All Events
@app.route('/events', methods=['GET'])
def view_all_events():
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    today = datetime.now().strftime('%Y-%m-%d')
    events = list(mongo.db.events.find({"event_date": {"$gte": today}}))
    for event in events:
        event['_id'] = str(event['_id'])

    return Response(json.dumps(events), status=200, mimetype="application/json")

# View User's Created Events
@app.route('/my-events', methods=['GET'])
def view_my_events():
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    events = list(mongo.db.events.find({"event_creator_id": session['user']}))
    for event in events:
        event['_id'] = str(event['_id'])
    return Response(json.dumps(events), status=200, mimetype="application/json")

# Update Event Information
@app.route('/events/<id>', methods=['PUT'])
def update_event(id):
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    data = request.json
    mongo.db.events.update_one(
        {"_id": ObjectId(id), "event_creator_id": session['user']},
        {"$set": {
            "event_title": data['event_title'],
            "event_description": data['event_description'],
            "event_date": data['event_date'],
            "event_hour": data['event_hour'],
            "event_placement": data['event_placement'],
            "event_type": data['event_type']
        }}
    )
    return jsonify({"message": "Event updated successfully!"}), 200

# Delete Event
@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    event = mongo.db.events.find_one({"_id": ObjectId(id)})

    if not (session['role'] == "admin" or (event and event['event_creator_id'] == session['user'])):
        return Response("Unauthorized action!", status=403, mimetype="application/json")
        
    mongo.db.events.delete_one({"_id": ObjectId(id)})
    return Response("Event deleted successfully!", status=200, mimetype="application/json")

# Search Events
@app.route('/search', methods=['GET'])
def search_events():
    if 'user' not in session:
        return Response("Please log in first!", status=403, mimetype="application/json")

    criteria = {
        "event_title": request.args.get('event_title'),
        "event_type": request.args.get('event_type'),
        "event_placement": request.args.get('event_placement')
    }
    search_query = {k: v for k, v in criteria.items() if v}
    
    events = list(mongo.db.events.find(search_query))
    if not events:
        return Response("No events found!", status=404, mimetype="application/json")

    for event in events:
        event['_id'] = str(event['_id'])
    return Response(json.dumps(events), status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
