from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, Trek, Booking, StaffProfile

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


# Custom decorator to restrict routes to Staff only
def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Staff":
            flash("Access denied. Staff only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@staff_bp.route("/dashboard")
@login_required
@staff_required
def dashboard():
    staff_profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_profile.id).all() if staff_profile else []

    total_assigned = len(assigned_treks)
    total_participants = sum(len(trek.bookings) for trek in assigned_treks)
    open_treks = sum(1 for trek in assigned_treks if trek.status == "Open")

    return render_template(
        "staff/dashboard.html",
        assigned_treks=assigned_treks,
        total_assigned=total_assigned,
        total_participants=total_participants,
        open_treks=open_treks
    )

@staff_bp.route("/trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
@staff_required
def manage_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_profile = StaffProfile.query.filter_by(user_id=current_user.id).first()

    # Security check: only the assigned staff can manage this trek
    if not staff_profile or trek.assigned_staff_id != staff_profile.id:
        flash("Access denied. You are not assigned to this trek.", "danger")
        return redirect(url_for("staff.dashboard"))

    if request.method == "POST":
        new_status = request.form.get("status")
        new_available_slots = request.form.get("available_slots")

        trek.status = new_status
        trek.available_slots = min(int(new_available_slots), trek.total_slots)

        # If trek is marked Completed, auto-complete all active bookings
        if new_status == "Completed":
            active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
            for booking in active_bookings:
                booking.status = "Completed"

        db.session.commit()
        flash("Trek updated successfully!", "success")
        return redirect(url_for("staff.manage_trek", trek_id=trek.id))

    participants = [booking for booking in trek.bookings]

    return render_template("staff/manage_trek.html", trek=trek, participants=participants)