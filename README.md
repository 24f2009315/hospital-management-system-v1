# 🩺 HealthEase

**A Modern Web-Based Hospital Management System**  
Built with Flask, SQLite, and Bootstrap

---

## 📘 Overview

**HealthEase** is a full-stack hospital management web application designed to simplify interactions between patients, doctors, and administrators.  
It enables seamless appointment scheduling, medical record tracking, and profile management through an intuitive, secure, and responsive interface.

The goal of HealthEase is to **bridge the gap between patients and healthcare providers** by providing a digital-first experience that prioritizes accessibility, efficiency, and care continuity.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Flask (Python) |
| **Frontend** | Jinja2, HTML, CSS, Bootstrap |
| **Database** | SQLite (programmatically generated) |
| **Authentication** | Flask-Login |
| **Visualization** | Chart.js (optional analytics) |

---

## ✨ Features

### 👩‍⚕️ For Patients
- Register, log in, and manage personal profile  
- Search doctors by specialization and availability  
- Book, reschedule, or cancel appointments  
- View upcoming and past consultations with treatment history  

### 🧑‍⚕️ For Doctors
- Access personalized dashboard of daily/weekly appointments  
- Mark appointments as *Completed* or *Cancelled*  
- Add diagnosis, prescription, and treatment notes  
- Review patient medical history for informed consultations  

### 🧑‍💼 For Admins
- Manage doctor and patient records  
- Monitor all appointments and system activity  
- Add, update, or remove user profiles  
- Prevent overlapping appointments and ensure data consistency  

---

## 🗃️ Database Schema (Simplified)

- **User** → Common base for all roles (Admin, Doctor, Patient)  
- **Doctor** → Stores specialization, schedule, and contact info  
- **Patient** → Contains demographics and health records  
- **Appointment** → Maps doctor and patient with date/time/status  
- **Treatment** → Linked to appointments with diagnosis and prescription details  

All tables are programmatically created during first run — no manual DB setup required.

---

## 🧭 Application Flow

1. **Admin** adds doctors and oversees hospital operations.  
2. **Patients** register and book appointments.  
3. **Doctors** update diagnosis and complete consultations.  
4. **System** automatically tracks appointment status and history.  

---

## 🖥️ Folder Structure
```text
Hospital-Management-System-v1
|--application
|    |--admin_api.py
|    |--appointment_api.py
|    |--auth.py
|    |--doctor_api.py
|    |--models.py
|    |--patient_api.py
|--instance
|    |--model.db
|--templates
|    |--admin
|    |    |--add_doctors.html
|    |    |--admin_dashboard.html
|    |    |--admin_search.html
|    |    |--layout.html
|    |    |--patient_history.html
|    |    |--update_doctors.html
|    |--doctor
|    |    |--doctor_dashboard.html
|    |    |--layout.html
|    |    |--patient_history.html
|    |    |--update_availability.html
|    |    |--update_history.html
|    |--patient
|    |    |--book_appointment.html
|    |    |--check_availability.html
|    |    |--layout.html
|    |    |--patient_dashboard.html
|    |    |--patient_history.html
|    |    |--patient_search.html
|    |    |--reschedule.html
|    |    |--update_profile.html
|    |--layout.html
|    |--login.html
|    |--signup.html
|--app.py
|--README.md
|--project_report.pdf
```
## Getting Started

### 1️⃣ Clone the Repository
git clone https://github.com/your-username/HealthEase.git
cd HealthEase
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the Application
python app.py
Access the app at 127.0.0.1:5000

## Watch the Demo Video Here
[https://drive.google.com/file/d/1tgE6L2REwMovCwr6BmdMNwjgP1ZH3JyG/view?usp=drive_link]
