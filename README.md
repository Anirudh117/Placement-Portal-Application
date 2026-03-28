# 🚀 Placement Portal Application

A full-stack web application built using **Flask, SQLAlchemy, and SQLite** that streamlines the placement process by connecting students and recruiters on a single platform.

---

## 📌 Overview

The Placement Portal enables students to register, upload resumes, and apply for job opportunities, while companies can post job drives and manage applicants efficiently. The system is designed with a structured relational database and dynamic frontend rendering using Jinja templates.

---

## ✨ Features

### 👨‍🎓 Student Module

* Register and login functionality
* Upload and manage resumes
* View available job drives
* Apply for job opportunities

### 🏢 Company Module

* Register and login
* Post job drives
* View applicants for each drive

### ⚙️ System Features

* Secure session-based authentication
* Dynamic content rendering using Jinja
* File upload support (resume handling)
* Relational database design using SQLAlchemy ORM

---

## 🧠 Tech Stack

**Frontend**

* HTML5
* CSS3
* Jinja Templating

**Backend**

* Python (Flask)

**Database**

* SQLite
* SQLAlchemy ORM

---

## 🏗️ Project Structure

```
Placement-Portal/
│
├── app.py                # Main Flask application (routes & logic)
├── models.py             # Database models (Student, Company, Drive, Application)
├── config.py             # Application configuration
├── create_db.py          # Database initialization script
├── utils.py              # Helper functions (reserved for future use)
│
├── templates/            # HTML templates (Jinja आधारित UI)
├── static/               # CSS, JS, uploads
├── instance/
│   └── placement.db      # SQLite database
│
└── requirements.txt      # Project dependencies
```

---

## 🔄 How It Works

1. Users interact with the frontend (HTML templates)
2. Requests are sent to Flask routes
3. Flask processes logic and interacts with the database
4. Data is retrieved using SQLAlchemy ORM
5. Results are rendered dynamically using Jinja templates

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/Placement-Portal-Application.git
cd Placement-Portal-Application
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Initialize database

```bash
python create_db.py
```

### 5️⃣ Run the application

```bash
python app.py
```

---

## 🌐 Usage

* Open browser and go to: `http://127.0.0.1:5000`
* Register as student or company
* Explore job drives and apply

---

## 🧩 Database Design

* **Student** → Stores student details and resumes
* **Company** → Stores recruiter details
* **Drive** → Job postings linked to companies
* **Application** → Junction table connecting students and drives

---

## 🔐 Key Concepts Implemented

* CRUD Operations (Create, Read, Update, Delete)
* Session Management
* File Handling (Resume Upload)
* ORM-based Database Interaction
* Dynamic Rendering using Jinja Templates

---

## 🚀 Future Enhancements

* Admin dashboard
* Email notifications
* Resume parsing using AI
* Advanced filtering and search
* Deployment on cloud (AWS/Render)

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo and submit pull requests.

---

## 📜 License

This project is for educational and demonstration purposes.

---

## 👤 Author

**Anirudhan M**
Aspiring Data Scientist | Full-Stack Developer

---
