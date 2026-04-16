from functools import wraps
from flask import session, redirect, url_for, flash


# -------------------------
# Basic auth check
# -------------------------
def login_required(view_func):
    """
    Require a user to be logged in before accessing a route.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped_view


# -------------------------
# Role-based route protection
# -------------------------
def roles_required(*allowed_roles):
    """
    Restrict a route to one or more roles.

    Example:
        @roles_required("admin", "coordinator")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            user_role = session.get("role")

            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("auth.login"))

            if user_role not in allowed_roles:
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for("dogs.index"))

            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator


# -------------------------
# Simple helper functions
# -------------------------
def current_user_id():
    """
    Return the current logged-in user's ID, or None.
    """
    return session.get("user_id")


def current_username():
    """
    Return the current logged-in username, or None.
    """
    return session.get("username")


def current_user_role():
    """
    Return the current logged-in user's role, or None.
    """
    return session.get("role")


def is_logged_in():
    """
    Return True if a user is logged in.
    """
    return "user_id" in session


def has_role(*roles):
    """
    Return True if the logged-in user has one of the given roles.
    """
    return session.get("role") in roles


def is_admin():
    return has_role("admin")


def is_coordinator():
    return has_role("coordinator")


def is_staff():
    return has_role("staff")


def is_foster():
    return has_role("foster")


# -------------------------
# Permission rules by action
# -------------------------
def can_view_dogs():
    """
    Who can view dog profiles?
    """
    return has_role("admin", "coordinator", "staff", "foster")


def can_add_dogs():
    """
    Who can add new dog records?
    """
    return has_role("admin", "coordinator", "staff")


def can_edit_dogs():
    """
    Who can edit dog records?
    """
    return has_role("admin", "coordinator", "staff")


def can_delete_dogs():
    """
    Who can delete dog records?
    """
    return has_role("admin", "coordinator")


def can_upload_documents():
    """
    Who can upload documents?
    """
    return has_role("admin", "coordinator", "staff", "foster")


def can_delete_documents():
    """
    Who can delete documents?
    """
    return has_role("admin", "coordinator")


def can_post_messages():
    """
    Who can post chat/messages?
    """
    return has_role("admin", "coordinator", "staff", "foster")


def can_delete_messages():
    """
    Who can delete chat/messages?
    """
    return has_role("admin", "coordinator")
