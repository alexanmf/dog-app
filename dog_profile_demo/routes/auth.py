from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    Good for testing and small internal apps.
    """
    if "user_id" in session:
        return redirect(url_for("dogs.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        role = request.form.get("role", "staff").strip().lower()

        if not username or not password or not confirm_password:
            flash("Username, password, and confirm password are required.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username already exists.", "error")
            return redirect(url_for("auth.register"))

        allowed_roles = {"admin", "coordinator", "staff", "foster"}
        if role not in allowed_roles:
            role = "staff"

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password_hash=hashed_password,
            role=role
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Log a user in by saving basic user info into the session.
    """
    if "user_id" in session:
        return redirect(url_for("dogs.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dogs.index"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """
    Log the user out by clearing the session.
    """
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
