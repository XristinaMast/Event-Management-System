/*
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

app.config["MONGO_URI"] = "mongodb://mongodb:27017/HospitalDB"
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['HospitalDB']
doctors = db['Doctors']
patients = db['Patients']
appointments = db['Appointments']
#Γίνεται σύνδεση στη βάση δεδομένων MongoDB και δημιουργούνται οι συλλογές Doctors, Patients και Appointments.

app = Flask(__name__) #Εδώ δημιουργείται η εφαρμογή Flask.

def has_required_fields(field_names, data):
    # Σε αυτήν την συνάρτηση βάζουμε σε list τα ονόματα των fields που πρέπει να περιέχει το json που θα δώσει ο χρήστης.
    # Αν δεν υπάρχει κάποιο από αυτά, επιστρέφεται False
    for field in field_names:
        if field not in data:
            return False
    return True

users_sessions = list()
def create_session(username, category): # Η συνάρτηση αυτή δημιουργεί και επιστρέφει ένα μοναδικό κωδικό uuid
    user_uuid = str(uuid.uuid1())
    users_sessions.append((user_uuid, username, time.time(), category))
    return user_uuid

def is_session_valid(user_uuid, category):
    # Η συνάρτηση αυτή ελέγχει αν το uuid είναι έγκυρο και αν ο χρήστης που του ανήκει, έχει πρόσβαση στο category
    # Είναι έτσι σχεδιασμένο που αν ο χρήστης είναι admin μπορεί να έχει προσβάση στα endpoint που είναι Simple ενώ το αντίθετο δεν ισχύει
    for session in users_sessions:
        if (session[0] == user_uuid) and (session[3] == category or session[3] == "Admin"):
            return True
    return False
#Αυτές οι συναρτήσεις βοηθούν στον έλεγχο αν υπάρχουν όλα τα απαραίτητα πεδία, στη δημιουργία συνεδριών χρηστών και στον έλεγχο εγκυρότητας συνεδριών.

@app.route('/login', methods=['POST'])
def login(): #Αυτή η διαδρομή χειρίζεται το login των χρηστών, δημιουργεί μια συνεδρία και επιστρέφει ένα UUID μαζί με την κατηγορία του χρήστη.
    # Το endpoint αυτό χρησιμοποιείται για να συνδεθεί ο χρήστης
    try:
        data = json.loads(request.data)
    except Exception:
        return Response("This request needs JSON data", status=500, mimetype='application/json')
    if not has_required_fields(("username", "password"), data):
        return Response("There is missing at least one field in your request", status=500, mimetype="application/json")
    # Έλεγχος αν υπάρχει κάποιος χρήστης με αυτό το email και τον κωδικό
    user = doctors.find_one({ "$and": [{"username":data['username']},{"password":data['password']}]})
    if user is None:  # Επιτυχής ταυτοποίηση. Επιστροφή uuid
        user = patients.find_one({ "$and": [{"username":data['username']},{"password":data['password']}]})
        user_uuid = create_session(data['username'], user['category'])
        return Response(json.dumps({"uuid": user_uuid, "category": user['category']}), mimetype='application/json')
    if user is None:  # Η αυθεντικοποίηση είναι ανεπιτυχής. Μήνυμα λάθους (Λάθος email ή password)
        return Response("Invalid username or password", status=401, mimetype="application/json")
    
@app.route('/api/v1/doctors', methods=['POST'])
def add_doctor(): #Προσθέτουμε έναν νέο γιατρό στη βάση δεδομένων.
    # Αν υπάρχει ήδη, επιστρέφουμε κατάλληλο μήνυμα
    # Αν δεν υπάρχει, τον προσθέτουμε και επιστρέφουμε το νέο χρήστη σε μορφή json
    if not has_required_fields(['name', 'specialization', 'username', 'password'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    try:
        doctors.insert_one(request.json)
        return Response(json.dumps(request.json), mimetype='application/json')
    except DuplicateKeyError:
        return Response(json.dumps({'error': 'Doctor already exists'}), mimetype='application/json')

@app.route('/api/v1/patients', methods=['POST'])
def add_patient(): #Προσθέτουμε έναν νέο ασθενή στη βάση δεδομένων.
    # Αν υπάρχει ήδη, επιστρέφουμε κατάλληλο μήνυμα
    # Αν δεν υπάρχει, τον προσθέτουμε και επιστρέφουμε το νέο χρήστη σε μορφή json
    if not has_required_fields(['name', 'dob', 'username', 'password'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    try:
        patients.insert_one(request.json)
        return Response(json.dumps(request.json), mimetype='application/json')
    except DuplicateKeyError:
        return Response(json.dumps({'error': 'Patient already exists'}), mimetype='application/json')

@app.route('/api/v1/appointments', methods=['POST'])
def add_appointment(): #Προσθέτουμε ένα νέο ραντεβού στη βάση δεδομένων.
    # Αν υπάρχει ήδη, επιστρέφουμε κατάλληλο μήνυμα
    # Αν δεν υπάρχει, το προσθέτουμε και επιστρέφουμε το νέο ραντεβού σε μορφή json
    if not has_required_fields(['doctor_id', 'patient_id', 'date'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    doctor = doctors.find_one({'_id': ObjectId(request.json['doctor_id'])})
    patient = patients.find_one({'_id': ObjectId(request.json['patient_id'])})
    if not doctor or not patient:
        return Response(json.dumps({'error': 'Doctor or patient not found'}), mimetype='application/json')
    appointments.insert_one(request.json)
    return Response(json.dumps(request.json), mimetype='application/json')

@app.route('/api/v1/doctors/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id): #Αυτό το κομμάτι κώδικα επιστρέφει πληροφορίες για έναν συγκεκριμένο γιατρό.
    # Αν δεν υπάρχει, επιστρέφουμε κατάλληλο μήνυμα
    # Αν υπάρχει, το επιστρέφουμε σε μορφή json
    doctor = doctors.find_one({'_id': ObjectId(doctor_id)}, {'_id': False})
    if doctor:
        return Response(json.dumps(doctor), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Doctor not found'}), mimetype='application/json')

@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id): #Αυτό το κομμάτι κώδικα επιστρέφει πληροφορίες για έναν συγκεκριμένο ασθενή.
    # Αν δεν υπάρχει, επιστρέφουμε κατάλληλο μήνυμα
    # Αν υπάρχει, το επιστρέφουμε σε μορφή json
    patient = patients.find_one({'_id': ObjectId(patient_id)}, {'_id': False})
    if patient:
        return Response(json.dumps(patient), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Patient not found'}), mimetype='application/json')

@app.route('/api/v1/appointments/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id): #Αυτό το κομμάτι κώδικα διαγράφει ένα συγκεκριμένο ραντεβού.
    # Αν δεν υπάρχει, επιστρέφουμε κατάλληλο μήνυμα
    # Αν υπάρχει, το επιστρέφουμε σε μορφή json
    appointment = appointments.find_one({'_id': ObjectId(appointment_id)}, {'_id': False})
    if appointment:
        return Response(json.dumps(appointment), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Appointment not found'}), mimetype='application/json')

@app.route('/api/v1/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id): ##Αυτό το κομμάτι κώδικα επιστρέφει πληροφορίες για έναν συγκεκριμένο γιατρό.
    # Αν δεν υπάρχει, επιστρέφουμε κατάλληλο μήνυμα
    # Αν υπάρχει, το επιστρέφουμε σε μορφή json
    appointment = appointments.find_one({'_id': ObjectId(appointment_id)})
    if appointment:
        appointments.delete_one({'_id': ObjectId(appointment_id)})
        return Response(json.dumps({'success': 'Appointment deleted'}), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Appointment not found'}), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
*\

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
