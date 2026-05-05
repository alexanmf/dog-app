from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Dog, Document, DogMessage
from services.permissions import login_required, roles_required
from services.storage import upload_image_to_cloudinary

dogs_bp = Blueprint("dogs", __name__)


@dogs_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    size = request.args.get("size", "").strip()
    friendliness = request.args.get("friendliness", "").strip()
    breed = request.args.get("breed", "").strip()

    query = Dog.query

    if q:
        query = query.filter(
            db.or_(
                Dog.name.ilike(f"%{q}%"),
                Dog.breed.ilike(f"%{q}%"),
                Dog.friendliness.ilike(f"%{q}%")
            )
        )

    if status:
        query = query.filter(Dog.status == status)

    if size:
        query = query.filter(Dog.size == size)

    if friendliness:
        query = query.filter(Dog.friendliness.ilike(f"%{friendliness}%"))

    if breed:
        query = query.filter(Dog.breed.ilike(f"%{breed}%"))

    dogs = query.order_by(Dog.created_at.desc()).all()

    return render_template(
        "index.html",
        dogs=dogs,
        q=q,
        status=status,
        size=size,
        friendliness=friendliness,
        breed=breed
    )

        image_file = request.files.get("image")
        image_url = None

        if not name:
            flash("Dog name is required.", "error")
            return redirect(url_for("dogs.add_dog"))

        try:
            if image_file and image_file.filename:
                image_url = upload_image_to_cloudinary(image_file)

            new_dog = Dog(
                name=name,
                breed=breed or None,
                age=age or None,
                size=size or None,
                friendliness=friendliness or None,
                status=status or "Available",
                image_url=image_url or None
            )

            db.session.add(new_dog)
            db.session.commit()
            flash(f"{new_dog.name} was added successfully.", "success")
            return redirect(url_for("dogs.index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding dog: {str(e)}", "error")
            return redirect(url_for("dogs.add_dog"))

    return render_template("form.html", dog=None)


@dogs_bp.route("/dog/<int:dog_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin", "coordinator", "staff")
def edit_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        breed = request.form.get("breed", "").strip()
        age = request.form.get("age", "").strip()
        size = request.form.get("size", "").strip()
        friendliness = request.form.get("friendliness", "").strip()
        status = request.form.get("status", "").strip()

        image_file = request.files.get("image")

        if not name:
            flash("Dog name is required.", "error")
            return redirect(url_for("dogs.edit_dog", dog_id=dog.id))

        try:
            dog.name = name
            dog.breed = breed or None
            dog.age = age or None
            dog.size = size or None
            dog.friendliness = friendliness or None
            dog.status = status or "Available"

            if image_file and image_file.filename:
                dog.image_url = upload_image_to_cloudinary(image_file)

            db.session.commit()
            flash(f"{dog.name} was updated successfully.", "success")
            return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating dog: {str(e)}", "error")
            return redirect(url_for("dogs.edit_dog", dog_id=dog.id))

    return render_template("form.html", dog=dog)


@dogs_bp.route("/dog/<int:dog_id>/delete", methods=["POST"])
@login_required
@roles_required("admin", "coordinator")
def delete_dog(dog_id):
    dog = Dog.query.get_or_404(dog_id)

    try:
        db.session.delete(dog)
        db.session.commit()
        flash(f"{dog.name} was deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting dog: {str(e)}", "error")

    return redirect(url_for("dogs.index"))
