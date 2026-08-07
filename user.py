from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, Trek, Booking
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")


# Custom decorator to restrict routes to Trekker only
def trekker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Trekker":
            flash("Access denied. Trekkers only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route("/dashboard")
@login_required
@trekker_required
def dashboard():
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    query = Trek.query.filter(Trek.status == "Open", Trek.available_slots > 0)

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    available_treks = query.all()

    all_locations = [loc[0] for loc in db.session.query(Trek.location).distinct().all()]

    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template(
        "user/dashboard.html",
        available_treks=available_treks,
        my_bookings=my_bookings,
        all_locations=all_locations,
        selected_difficulty=difficulty,
        selected_location=location
    )

@user_bp.route("/trek/<int:trek_id>")
@login_required
@trekker_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    ).first()

    return render_template("user/trek_details.html", trek=trek, existing_booking=existing_booking)


@user_bp.route("/trek/<int:trek_id>/book", methods=["POST"])
@login_required
@trekker_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # Prevent booking if trek is not open
    if trek.status != "Open":
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    # Prevent booking if no slots available
    if trek.available_slots <= 0:
        flash("Sorry, this trek is fully booked.", "danger")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    # Prevent duplicate booking
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    ).first()

    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    # Create booking
    new_booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    )
    trek.available_slots -= 1

    db.session.add(new_booking)
    db.session.commit()

    flash(f"Successfully booked '{trek.name}'!", "success")
    return redirect(url_for("user.my_bookings"))

@user_bp.route("/my-bookings")
@login_required
@trekker_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template("user/my_bookings.html", bookings=bookings)


@user_bp.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required
@trekker_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("user.my_bookings"))

    if booking.status != "Booked":
        flash("This booking cannot be cancelled.", "warning")
        return redirect(url_for("user.my_bookings"))

    booking.status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()

    flash("Booking cancelled successfully.", "info")
    return redirect(url_for("user.my_bookings"))

@user_bp.route("/history")
@login_required
@trekker_required
def trekking_history():
    completed_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).order_by(Booking.booking_date.desc()).all()

    return render_template("user/history.html", completed_bookings=completed_bookings)