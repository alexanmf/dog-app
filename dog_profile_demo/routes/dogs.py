from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Dog, Document, DogMessage, DogPhoto
from services.permissions import login_required, roles_required
from services.storage import upload_image_to_cloudinary

dogs_bp = Blueprint("dogs", __name__)


def get_dashboard_counts():
    total_dogs = Dog.query.count()

    available_dogs = Dog.query.filter(
        Dog.status.in_(["Available", "Intake", "Fostered", "Hold"])
    ).count()

    adopted_dogs = Dog.query.filter_by(status="Adopted").count()

    foster_needed_dogs = Dog.query.filter_by(immediate_foster=True).count()

    return total_dogs, available_dogs, adopted_dogs, foster_needed_dogs


@dogs_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    size = request.args.get("size", "").strip()
    breed = request.args.get("breed", "").strip()
    friendliness = request.args.get("friendliness", "").strip()

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

    if breed:
        query = query.filter(Dog.breed.ilike(f"%{breed}%"))

    if friendliness:
        query = query.filter(Dog.friendliness.ilike(f"%{friendliness}%"))

    dogs = query.order_by(Dog.created_at.desc()).all()

    total_dogs, available_dogs, adopted_dogs, foster_needed_dogs = get_dashboard_counts()

    return render_template(
        "index.html",
        dogs=dogs,
        total_dogs=total_dogs,
        available_dogs=available_dogs,
        adopted_dogs=adopted_dogs,
        foster_needed_dogs=foster_needed_dogs,
        foster_view=False
    )


@dogs_bp.route("/dogs")
@login_required
def list_dogs():
    return redirect(url_for("dogs.index"))


@dogs_bp.route("/foster-needed")
@login_required
def foster_needed():
    dogs = Dog.query.filter_by(
        immediate_foster=True
    ).order_by(
        Dog.created_at.desc()
    ).all()

    total_dogs, available_dogs, adopted_dogs, foster_needed_dogs = get_dashboard_counts()

    return render_template(
        "index.html",
        dogs=dogs,
        total_dogs=total_dogs,
        available_dogs=available_dogs,
        adopted_dogs=adopted_dogs,
        foster_needed_dogs=foster_needed_dogs,
        foster_view=True
    )


@dogs_bp.route("/dog/<int:dog_id>")
@login_required
def dog_detail(dog_id):
    dog = Dog.query.get_or_404(dog_id)

    documents = Document.query.filter_by(
        dog_id=dog_id
    ).order_by(
        Document.uploaded_at.desc()
    ).all()

    messages = DogMessage.query.filter_by(
        dog_id=dog_id
    ).order_by(
        DogMessage.created_at.asc()
    ).all()

    photos = DogPhoto.query.filter_by(
        dog_id=dog_id
    ).order_by(
        DogPhoto.uploaded_at.desc()
    ).all()

    return render_template(
        "dog_detail.html",
        dog=dog,
        documents=documents,
        messages=messages,
        photos=photos
    )


@dogs_bp.route("/dog/add", methods=["GET", "POST"])
@login_required
@roles_required("admin", "coordinator", "staff")
def add_dog():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        breed = request.form.get("breed", "").strip()
        age = request.form.get("age", "").strip()
        size = request.form.get("size", "").strip()
        friendliness = request.form.get("friendliness", "").strip()
        status = request.form.get("status", "").strip()
        immediate_foster = bool(request.form.get("immediate_foster"))

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
                image_url=image_url or None,
                immediate_foster=immediate_foster
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
        immediate_foster = bool(request.form.get("immediate_foster"))

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
            dog.immediate_foster = immediate_foster

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


@dogs_bp.route("/dog/<int:dog_id>/photos/add", methods=["POST"])
@login_required
@roles_required("admin", "coordinator", "staff")
def add_photo(dog_id):
    dog = Dog.query.get_or_404(dog_id)

    image_file = request.files.get("photo")
    caption = request.form.get("caption", "").strip()

    if not image_file or not image_file.filename:
        flash("Please choose a photo to upload.", "error")
        return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

    try:
        image_url = upload_image_to_cloudinary(image_file)

        new_photo = DogPhoto(
            dog_id=dog.id,
            image_url=image_url,
            caption=caption or None
        )

        db.session.add(new_photo)
        db.session.commit()

        flash("Photo added successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error uploading photo: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog.id))


@dogs_bp.route("/dog/photo/<int:photo_id>/delete", methods=["POST"])
@login_required
@roles_required("admin", "coordinator")
def delete_photo(photo_id):
    photo = DogPhoto.query.get_or_404(photo_id)
    dog_id = photo.dog_id

    try:
        db.session.delete(photo)
        db.session.commit()
        flash("Photo deleted successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting photo: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog_id))


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
