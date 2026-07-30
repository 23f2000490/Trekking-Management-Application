from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StaffProfile

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")  # "Staff" or "Trekker"

        if not all([name, email, password, confirm_password, role]):
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            name=name,
            email=email,
            role=role,
            is_approved=True if role == "Trekker" else False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        if role == "Staff":
            staff_profile = StaffProfile(user_id=new_user.id, status="Pending")
            db.session.add(staff_profile)
            db.session.commit()
            flash("Registration successful! Please wait for Admin approval before logging in.", "info")
        else:
            flash("Registration successful! You can now log in.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if user.is_blacklisted:
            flash("Your account has been blacklisted. Contact Admin.", "danger")
            return redirect(url_for("auth.login"))

        if user.role == "Staff" and not user.is_approved:
            flash("Your account is awaiting Admin approval.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"Welcome back, {user.name}!", "success")

        if user.role == "Admin":
            return redirect(url_for("auth.admin_dashboard"))
        elif user.role == "Staff":
            return redirect(url_for("auth.staff_dashboard"))
        else:
            return redirect(url_for("auth.user_dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("admin/dashboard.html")


@auth_bp.route("/staff/dashboard")
@login_required
def staff_dashboard():
    if current_user.role != "Staff":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("staff/dashboard.html")


@auth_bp.route("/user/dashboard")
@login_required
def user_dashboard():
    if current_user.role != "Trekker":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("user/dashboard.html")