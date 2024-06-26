from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')
# Choose database
db = client['HospitalDB']
# Choose collections
doctors = db['Doctors']
patients = db['Patients']
appointments = db['Appointments']

# Initiate Flask App
app = Flask(__name__)

def has_required_fields(field_names, data):
    for field in field_names:
        if field not in data:
            return False
    return True

users_sessions = list()
def create_session(username, category):
    user_uuid = str(uuid.uuid1())
    users_sessions.append((user_uuid, username, time.time(), category))
    return user_uuid

def is_session_valid(user_uuid, category):
    for session in users_sessions:
        if (session[0] == user_uuid) and (session[3] == category or session[3] == "Admin"):
            return True
    return False

@app.route('/login', methods=['POST'])
def login():
    try:
        data = json.loads(request.data)
    except Exception:
        return Response("This request needs JSON data", status=500, mimetype='application/json')
    if not has_required_fields(("username", "password"), data):
        return Response("There is missing at least one field in your request", status=500, mimetype="application/json")

    user = doctors.find_one({ "$and": [{"username":data['username']},{"password":data['password']}]})
    if user is None:
        user = patients.find_one({ "$and": [{"username":data['username']},{"password":data['password']}]})
    if user is None:
        return Response("Invalid username or password", status=401, mimetype="application/json")

    user_uuid = create_session(data['username'], user['category'])
    return Response(json.dumps({"uuid": user_uuid, "category": user['category']}), mimetype='application/json')

@app.route('/api/v1/doctors', methods=['POST'])
def add_doctor():
    if not has_required_fields(['name', 'specialization', 'username', 'password'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    try:
        doctors.insert_one(request.json)
        return Response(json.dumps(request.json), mimetype='application/json')
    except DuplicateKeyError:
        return Response(json.dumps({'error': 'Doctor already exists'}), mimetype='application/json')

@app.route('/api/v1/patients', methods=['POST'])
def add_patient():
    if not has_required_fields(['name', 'dob', 'username', 'password'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    try:
        patients.insert_one(request.json)
        return Response(json.dumps(request.json), mimetype='application/json')
    except DuplicateKeyError:
        return Response(json.dumps({'error': 'Patient already exists'}), mimetype='application/json')

@app.route('/api/v1/appointments', methods=['POST'])
def add_appointment():
    if not has_required_fields(['doctor_id', 'patient_id', 'date'], request.json):
        return Response(json.dumps({'error': 'Missing required fields'}), mimetype='application/json')
    doctor = doctors.find_one({'_id': ObjectId(request.json['doctor_id'])})
    patient = patients.find_one({'_id': ObjectId(request.json['patient_id'])})
    if not doctor or not patient:
        return Response(json.dumps({'error': 'Doctor or patient not found'}), mimetype='application/json')
    appointments.insert_one(request.json)
    return Response(json.dumps(request.json), mimetype='application/json')

@app.route('/api/v1/doctors/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = doctors.find_one({'_id': ObjectId(doctor_id)}, {'_id': False})
    if doctor:
        return Response(json.dumps(doctor), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Doctor not found'}), mimetype='application/json')

@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = patients.find_one({'_id': ObjectId(patient_id)}, {'_id': False})
    if patient:
        return Response(json.dumps(patient), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Patient not found'}), mimetype='application/json')

@app.route('/api/v1/appointments/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = appointments.find_one({'_id': ObjectId(appointment_id)}, {'_id': False})
    if appointment:
        return Response(json.dumps(appointment), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Appointment not found'}), mimetype='application/json')

@app.route('/api/v1/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = appointments.find_one({'_id': ObjectId(appointment_id)})
    if appointment:
        appointments.delete_one({'_id': ObjectId(appointment_id)})
        return Response(json.dumps({'success': 'Appointment deleted'}), mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Appointment not found'}), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host=' ``````')