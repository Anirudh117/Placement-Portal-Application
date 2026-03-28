from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from models import db, User, Company, Student, Drive, Application
from sqlalchemy import text


app = Flask(__name__)
app.config.from_object('config.Config')


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def initialize_database():
    with app.app_context():
        db.create_all()

        
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin_user = User(
                role="admin",
                name="Admin",
                email="admin@portal.com",
                password=generate_password_hash("admin123")
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user (admin@portal.com / admin123)")
        else:
            
            if admin.email != "admin@portal.com" or not check_password_hash(admin.password, "admin123"):
                admin.email = "admin@portal.com"
                admin.password = generate_password_hash("admin123")
                db.session.commit()
                print("Reset admin credentials to admin@portal.com / admin123")

        # make sure the company table has a details column (simple dev-time migration)
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE company ADD COLUMN details TEXT'))
        except Exception:
            
            pass


    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)




@app.route("/")
def home():
    # index.html already exists; use it as the homepage
    return render_template("index.html")




@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        contact = request.form["contact"]

        
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("register_student"))

        hashed = generate_password_hash(password)
        new_user = User(role="student", name=name, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        student = Student(user_id=new_user.id, contact=contact)
        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully")
        return redirect(url_for("login"))

    return render_template("auth/register_student.html")




@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        company_name = request.form["company_name"]
        hr_contact = request.form.get("hr_contact")
        website = request.form.get("website")
        details = request.form.get("details")

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("register_company"))

        hashed = generate_password_hash(password)
        new_user = User(role="company", name=name, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        company = Company(user_id=new_user.id,
                          company_name=company_name,
                          hr_contact=hr_contact,
                          website=website,
                          details=details)
        db.session.add(company)
        db.session.commit()

        flash("Company registered. Wait for admin approval.")
        return redirect(url_for("login"))

    return render_template("auth/register_company.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # additional restrictions
            if not user.active:
                flash("Account is disabled", "error")
            elif user.blacklisted:
                flash("Account has been blacklisted", "error")
            else:
                if user.role == "company":
                    comp = Company.query.filter_by(user_id=user.id).first()
                    if comp and comp.approval_status != "Approved":
                        flash("Your company registration is not approved by admin.", "error")
                        return redirect(url_for("login"))
                # passed all checks
                login_user(user)
                flash("Login successful")
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("auth/login.html")




@app.route("/dashboard")
@login_required
def dashboard():
    # redirect to the appropriate dashboard page based on role
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "company":
        return redirect(url_for("company_dashboard"))
    elif current_user.role == "student":
        return redirect(url_for("student_dashboard"))
    else:
        # fallback
        return f"Welcome {current_user.name} | Role: {current_user.role}"


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    students_count = Student.query.count()
    companies_count = Company.query.count()
    applications_count = Application.query.count()
    drives_count = Drive.query.count()
    return render_template("admin/dashboard.html",
                           students_count=students_count,
                           companies_count=companies_count,
                           applications_count=applications_count,
                           drives_count=drives_count)


@app.route("/admin/companies")
@admin_required
def admin_companies():
    action = request.args.get("action")
    cid = request.args.get("id")
    if action and cid:
        comp = Company.query.get(cid)
        if comp:
            if action == "approve":
                comp.approval_status = "Approved"
            elif action == "reject":
                comp.approval_status = "Rejected"
            elif action == "deactivate":
                user = User.query.get(comp.user_id)
                if user:
                    user.active = False
            elif action == "blacklist":
                user = User.query.get(comp.user_id)
                if user:
                    user.blacklisted = True
            db.session.commit()
        return redirect(url_for("admin_companies"))

    search = request.args.get("search", "")
    companies_query = Company.query
    if search:
        companies_query = companies_query.filter(Company.company_name.ilike(f"%{search}%"))
    companies = companies_query.all()
    return render_template("admin/companies.html", companies=companies, search=search)


@app.route("/admin/drives")
@admin_required
def admin_drives():
    action = request.args.get("action")
    did = request.args.get("id")
    if action and did:
        drive = Drive.query.get(did)
        if drive:
            if action == "approve":
                drive.status = "Approved"
            elif action == "reject":
                drive.status = "Rejected"
            db.session.commit()
        return redirect(url_for("admin_drives"))
    drives = Drive.query.all()
    return render_template("admin/drives.html", drives=drives)


@app.route("/admin/applications")
@admin_required
def admin_applications():
    applications = Application.query.all()
    return render_template("admin/applications.html", applications=applications)


@app.route("/admin/students")
@admin_required
def admin_students():
    action = request.args.get("action")
    sid = request.args.get("id")
    if action and sid:
        student = Student.query.get(sid)
        if student:
            user = User.query.get(student.user_id)
            if user:
                if action == "deactivate":
                    user.active = False
                elif action == "blacklist":
                    user.blacklisted = True
                db.session.commit()
        return redirect(url_for("admin_students"))

    search = request.args.get("search", "")
    students_query = Student.query.join(User)
    if search:
        term = f"%{search}%"
        filters = [User.name.ilike(term), Student.contact.ilike(term)]
        if search.isdigit():
            filters.append(User.id == int(search))
        students_query = students_query.filter(db.or_(*filters))
    students = students_query.all()
    return render_template("admin/students.html", students=students, search=search)


@app.route("/company/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "company":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    comp = Company.query.filter_by(user_id=current_user.id).first()
    drives = []
    if comp:
        drives = Drive.query.filter_by(company_id=comp.id).all()
        
        drive_info = []
        for d in drives:
            drive_info.append({
                'drive': d,
                'applicants': len(d.applications)
            })
    else:
        drive_info = []
    return render_template("company/dashboard.html", comp=comp, drives=drive_info)


@app.route("/company/profile", methods=["GET", "POST"])
@login_required
def company_profile():
    if current_user.role != "company":
        return redirect(url_for("dashboard"))
    comp = Company.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        comp.company_name = request.form.get('company_name')
        comp.hr_contact = request.form.get('hr_contact')
        comp.website = request.form.get('website')
        comp.details = request.form.get('details')
        db.session.commit()
        flash("Profile updated")
        return redirect(url_for('company_profile'))
    return render_template("company/profile.html", comp=comp)


@app.route("/company/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():
    if current_user.role != "company":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    comp = Company.query.filter_by(user_id=current_user.id).first()
    if not comp or comp.approval_status != "Approved":
        flash("Your company is not approved to create drives", "error")
        return redirect(url_for("company_dashboard"))
    if request.method == "POST":
        title = request.form['job_title']
        desc = request.form['job_description']
        eligibility = request.form['eligibility']
        deadline = request.form['deadline']
        new = Drive(company_id=comp.id, job_title=title, job_description=desc,
                    eligibility=eligibility, deadline=deadline)
        db.session.add(new)
        db.session.commit()
        flash("Drive created, pending admin approval")
        return redirect(url_for("company_dashboard"))
    return render_template("company/create_drive.html")


@app.route("/company/edit_drive/<int:did>", methods=["GET", "POST"])
@login_required
def edit_drive(did):
    if current_user.role != "company":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    drive = Drive.query.get(did)
    if not drive or drive.company.user_id != current_user.id:
        flash("Drive not found", "error")
        return redirect(url_for("company_dashboard"))
    if request.method == "POST":
        drive.job_title = request.form['job_title']
        drive.job_description = request.form['job_description']
        drive.eligibility = request.form['eligibility']
        drive.deadline = request.form['deadline']
        db.session.commit()
        flash("Drive updated")
        return redirect(url_for("company_dashboard"))
    return render_template("company/edit_drive.html", drive=drive)


@app.route("/company/close_drive/<int:did>")
@login_required
def close_drive(did):
    if current_user.role != "company":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    drive = Drive.query.get(did)
    if drive and drive.company.user_id == current_user.id:
        drive.status = "Closed"
        db.session.commit()
    return redirect(url_for("company_dashboard"))


@app.route("/company/drive/<int:did>/applications", methods=["GET", "POST"])
@login_required
def company_view_apps(did):
    if current_user.role != "company":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    drive = Drive.query.get(did)
    if not drive or drive.company.user_id != current_user.id:
        flash("Drive not found", "error")
        return redirect(url_for("company_dashboard"))
    if request.method == "POST":
        app_id = request.form.get('app_id')
        status = request.form.get('status')
        application = Application.query.get(app_id)
        if application and application.drive_id == drive.id:
            application.status = status
            db.session.commit()
        return redirect(url_for('company_view_apps', did=did))
    applications = drive.applications
    return render_template("company/view_applications.html", drive=drive, applications=applications)




@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    drives = (Drive.query.join(Company)
              .filter(Drive.status != 'Closed', Company.approval_status == 'Approved')
              .all())
    
    apps = Application.query.filter_by(student_id=student.id).all() if student else []
    applied = [a.drive_id for a in apps]
    return render_template("student/dashboard.html", drives=drives, apps=apps, student=student, applied=applied)


@app.route("/student/drives")
@login_required
def student_drives():
    if current_user.role != "student":
        flash("Access denied", "error")
        return redirect(url_for("dashboard"))
    student = Student.query.filter_by(user_id=current_user.id).first()
    applied = [a.drive_id for a in (Application.query.filter_by(student_id=student.id).all() if student else [])]
    drives = (Drive.query.join(Company)
              .filter(Drive.status != 'Closed', Company.approval_status == 'Approved')
              .all())
    return render_template("student/drives.html", drives=drives, applied=applied)


@app.route("/student/apply/<int:did>")
@login_required
def student_apply(did):
    if current_user.role != "student":
        return redirect(url_for("dashboard"))
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Profile not complete", "error")
        return redirect(url_for("student_dashboard"))
    drive = Drive.query.get(did)
    if not drive or drive.status != 'Approved':
        flash("Cannot apply to this drive", "error")
        return redirect(url_for("student_drives"))
    existing = Application.query.filter_by(student_id=student.id, drive_id=did).first()
    if existing:
        flash("Already applied", "info")
        return redirect(url_for("student_drives"))
    new_app = Application(student_id=student.id, drive_id=did)
    db.session.add(new_app)
    db.session.commit()
    flash("Application submitted")
    return redirect(url_for("student_dashboard"))


@app.route("/student/applications")
@login_required
def student_applications():
    if current_user.role != "student":
        return redirect(url_for("dashboard"))
    student = Student.query.filter_by(user_id=current_user.id).first()
    # return every application the student has ever made; history is preserved
    apps = Application.query.filter_by(student_id=student.id).all() if student else []
    return render_template("student/applications.html", applications=apps)


@app.route("/student/profile", methods=["GET", "POST"])
@login_required
def student_profile():
    if current_user.role != "student":
        return redirect(url_for("dashboard"))
    student = Student.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        student.contact = request.form.get('contact')
        student.course = request.form.get('course')
        try:
            student.cgpa = float(request.form.get('cgpa') or student.cgpa)
        except ValueError:
            pass
        file = request.files.get('resume')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            student.resume = filename
        db.session.commit()
        flash("Profile updated")
        return redirect(url_for('student_profile'))
    return render_template("student/profile.html", student=student)




@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for("login"))



initialize_database()

if __name__ == "__main__":
    app.run(debug=True)