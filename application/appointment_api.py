from flask import Blueprint, jsonify, request
from application.models import db, Appointment
from datetime import datetime

api = Blueprint('appointment_api', __name__)

# ✅ GET - Fetch all appointments
@api.route('/api/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    appointment_list = []
    for a in appointments:
        appointment_list.append({
            "appointment_id": a.appointment_id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M:%S"),
            "status": a.status
        })
    return jsonify(appointment_list)


# ✅ POST - Add a new appointment
@api.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        date_obj = datetime.strptime(data.get("date"), "%Y-%m-%d").date()
        time_obj = datetime.strptime(data.get("time"), "%H:%M:%S").time()
    except Exception:
        return jsonify({"error": "Invalid date or time format"}), 400

    new_appointment = Appointment(
        patient_id=data.get("patient_id"),
        doctor_id=data.get("doctor_id"),
        date=date_obj,
        time=time_obj,
        status=data.get("status", "Booked")
    )

    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"message": "Appointment booked successfully"}), 201


# ✅ PUT - Update appointment (date, time, or status)
@api.route('/api/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    data = request.get_json()
    if "date" in data:
        appointment.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    if "time" in data:
        appointment.time = datetime.strptime(data["time"], "%H:%M:%S").time()
    if "status" in data:
        appointment.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Appointment updated successfully"})


# ✅ DELETE - Cancel/Delete appointment
@api.route('/api/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment deleted successfully"})
