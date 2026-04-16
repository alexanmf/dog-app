from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Dog, Document, DogMessage

dogs_bp = Blueprint("dogs", __name__)


@dogs_bp.route("/")
def index():
    """
    Show all dogs on the homepage.
    """
    dogs = Dog.query.order_by(Dog.created_at.desc()).all()
    return render_template("index.html", dogs=dogs)


@dogs_bp.route("/dogs")
def list_dogs():
    """
    Optional separate route for listing dogs.
    """
    dogs = Dog.query.order_by(Dog.created_at.desc()).all()
    return render_template("index.html", dogs=dogs)


@dogs_bp.route("/dog/<int:dog_id>")
def dog_detail(dog_id):
    """
    Show a single dog's profile page, including documents and messages.
    """
    dog = Dog.query.get_or_404(dog_id)

    documents = Document.query.filter_by(dog_id=dog_id).order_by(Document.uploaded_at.desc()).all()
    messages = DogMessage.query.filter_by(dog_id=dog_id).order_by(DogMessage.created_at.asc()).all()

    return render_template(
        "dog_detail.html",
        dog=dog,
        documents=documents,
        messages=messages
    )


@dogs_bp.route("/dog/add", methods=["GET", "POST"])
def add_dog():
    """
    Add a new dog.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        breed = request.form.get("breed", "").strip()
        age = request.form.get("age", "").strip()
        size = request.form.get("size", "").strip()
        friendliness = request.form.get("friendliness", "").strip()
        status = request.form.get("status", "").strip()
        image_url = request.form.get("image_url", "").strip()

        if not name:
            flash("Dog name is required.", "error")
            return redirect(url_for("dogs.add_dog"))

        new_dog = Dog(
            name=name,
            breed=breed or None,
            age=age or None,
            size=size or None,
            friendliness=friendliness or None,
            status=status or "Available",
            image_url=image_url or None
        )

        try:
            db.session.add(new_dog)
            db.session.commit()
            flash(f"{new_dog.name} was added successfully.", "success")
            return redirect(url_for("dogs.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding dog: {str(e)}", "error")
            return redirect(url_for("dogs.add_dog"))

    return render_template("add_dog.html")


@dogs_bp.route("/dog/<int:dog_id>/edit", methods=["GET", "POST"])
def edit_dog(dog_id):
    """
    Edit an existing dog.
    """
    dog = Dog.query.get_or_404(dog_id)

    if request.method == "POST":
        dog.name = request.form.get("name", "").strip()
        dog.breed = request.form.get("breed", "").strip() or None
        dog.age = request.form.get("age", "").strip() or None
        dog.size = request.form.get("size", "").strip() or None
        dog.friendliness = request.form.get("friendliness", "").strip() or None
        dog.status = request.form.get("status", "").strip() or "Available"
        dog.image_url = request.form.get("image_url", "").strip() or None

        if not dog.name:
            flash("Dog name is required.", "error")
            return redirect(url_for("dogs.edit_dog", dog_id=dog.id))

        try:
            db.session.commit()
            flash(f"{dog.name} was updated successfully.", "success")
            return redirect(url_for("dogs.dog_detail", dog_id=dog.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating dog: {str(e)}", "error")
            return redirect(url_for("dogs.edit_dog", dog_id=dog.id))

    return render_template("edit_dog.html", dog=dog)


@dogs_bp.route("/dog/<int:dog_id>/delete", methods=["POST"])
def delete_dog(dog_id):
    """
    Delete a dog.
    """
    dog = Dog.query.get_or_404(dog_id)

    try:
        db.session.delete(dog)
        db.session.commit()
        flash(f"{dog.name} was deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting dog: {str(e)}", "error")

    return redirect(url_for("dogs.index"))
