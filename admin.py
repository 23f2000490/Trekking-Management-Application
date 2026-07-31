from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Trek, Booking, StaffProfile
from datetime import datetime
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Custom decorator to restrict routes to Admin only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="Trekker").count()
    total_staff = User.query.filter_by(role="Staff").count()
    total_bookings = Booking.query.count()

    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )
@admin_bp.route("/treks")
@login_required
@admin_required
def manage_treks():
    treks = Trek.query.all()
    return render_template("admin/manage_treks.html", treks=treks)


@admin_bp.route("/treks/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_trek():
    staff_list = StaffProfile.query.join(User).filter(StaffProfile.status == "Approved").all()

    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        duration = request.form.get("duration")
        description = request.form.get("description")
        total_slots = request.form.get("total_slots")
        assigned_staff_id = request.form.get("assigned_staff_id") or None
        status = request.form.get("status")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            description=description,
            available_slots=int(total_slots),
            total_slots=int(total_slots),
            assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None,
            status=status,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
        )
        db.session.add(new_trek)
        db.session.commit()
        flash("Trek added successfully!", "success")
        return redirect(url_for("admin.manage_treks"))

    return render_template("admin/trek_form.html", trek=None, staff_list=staff_list)


@admin_bp.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_list = StaffProfile.query.join(User).filter(StaffProfile.status == "Approved").all()

    if request.method == "POST":
        trek.name = request.form.get("name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = int(request.form.get("duration"))
        trek.description = request.form.get("description")

        new_total_slots = int(request.form.get("total_slots"))
        slots_diff = new_total_slots - trek.total_slots
        trek.total_slots = new_total_slots
        trek.available_slots = max(0, trek.available_slots + slots_diff)

        assigned_staff_id = request.form.get("assigned_staff_id") or None
        trek.assigned_staff_id = int(assigned_staff_id) if assigned_staff_id else None
        trek.status = request.form.get("status")
        trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()

        db.session.commit()
        flash("Trek updated successfully!", "success")
        return redirect(url_for("admin.manage_treks"))

    return render_template("admin/trek_form.html", trek=trek, staff_list=staff_list)


@admin_bp.route("/treks/delete/<int:trek_id>", methods=["POST"])
@login_required
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted successfully!", "success")
    return redirect(url_for("admin.manage_treks"))

@admin_bp.route("/staff")
@login_required
@admin_required
def manage_staff():
    pending_staff = StaffProfile.query.join(User).filter(StaffProfile.status == "Pending").all()
    approved_staff = StaffProfile.query.join(User).filter(StaffProfile.status == "Approved").all()
    blacklisted_staff = StaffProfile.query.join(User).filter(StaffProfile.status == "Blacklisted").all()

    return render_template(
        "admin/manage_staff.html",
        pending_staff=pending_staff,
        approved_staff=approved_staff,
        blacklisted_staff=blacklisted_staff
    )


@admin_bp.route("/staff/approve/<int:staff_id>", methods=["POST"])
@login_required
@admin_required
def approve_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.status = "Approved"
    staff.user.is_approved = True
    staff.user.is_blacklisted = False
    db.session.commit()
    flash(f"{staff.user.name} has been approved.", "success")
    return redirect(url_for("admin.manage_staff"))


@admin_bp.route("/staff/reject/<int:staff_id>", methods=["POST"])
@login_required
@admin_required
def reject_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    db.session.delete(staff.user)
    db.session.delete(staff)
    db.session.commit()
    flash("Staff registration rejected and removed.", "info")
    return redirect(url_for("admin.manage_staff"))


@admin_bp.route("/staff/blacklist/<int:staff_id>", methods=["POST"])
@login_required
@admin_required
def blacklist_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.status = "Blacklisted"
    staff.user.is_blacklisted = True
    staff.user.is_approved = False
    db.session.commit()
    flash(f"{staff.user.name} has been blacklisted.", "warning")
    return redirect(url_for("admin.manage_staff"))
@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(role="Trekker").all()
    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/users/blacklist/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f"{user.name} has been blacklisted.", "warning")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/unblacklist/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def unblacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f"{user.name} has been un-blacklisted.", "success")
    return redirect(url_for("admin.manage_users"))