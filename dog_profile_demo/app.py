from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_db, close_db

# NEW: imports for uploads
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "dev-secret"  # for flash()

# Load env (local) and configure Cloudinary (uses CLOUDINARY_URL)
load_dotenv()
cloudinary.config(secure=True)

# Allowed image types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_cloudinary(file_storage):
    """
    Uploads the given Werkzeug FileStorage to Cloudinary.
    Returns secure URL (str) or None on failure.
    """
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        return None
    # You can change the folder name if you want
    result = cloudinary.uploader.upload(
        file_storage,
        folder="dog_app",
        use_filename=True,
        unique_filename=False,
        overwrite=False,
    )
    return result.get("secure_url")

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route("/")
def index():
    db = get_db()
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    size = request.args.get("size", "").strip()

    sql = "SELECT * FROM dogs WHERE 1=1"
    params = []
    if q:
        sql += " AND (name LIKE ? OR notes LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if status:
        sql += " AND status = ?"
        params.append(status)
    if size:
        sql += " AND size = ?"
        params.append(size)
    sql += " ORDER BY name"
    dogs = db.execute(sql, params).fetchall()
    return render_template("index.html", dogs=dogs)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        db = get_db()
        form = request.form

        # NEW: handle optional image upload
        image_url = None
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                try:
                    image_url = upload_to_cloudinary(file)
                except Exception:
                    image_url = None
                    flash("Image upload failed.")

        db.execute(
            "INSERT INTO dogs (name, age, size, status, kid_friendly, cat_friendly, dog_friendly, notes, image_url) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
                image_url,
            ),
        )
        db.commit()
        flash("Dog created.")
        return redirect(url_for("index"))
    return render_template("form.html", dog=None)

@app.route("/edit/<int:dog_id>", methods=["GET", "POST"])
def edit(dog_id):
    db = get_db()
    dog = db.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,)).fetchone()
    if not dog:
        flash("Dog not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        form = request.form

        # Keep existing URL unless a new image is uploaded
        image_url = dog["image_url"]
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                try:
                    new_url = upload_to_cloudinary(file)
                    if new_url:
                        image_url = new_url
                except Exception:
                    flash("Image upload failed; keeping previous image.")

        db.execute(
            "UPDATE dogs SET name=?, age=?, size=?, status=?, kid_friendly=?, cat_friendly=?, dog_friendly=?, notes=?, image_url=? "
            "WHERE id=?",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
                image_url,
                db.execute(
            "UPDATE dogs SET name=?, age=?, size=?, status=?, kid_friendly=?, cat_friendly=?, dog_friendly=?, notes=?, image_url=? "
            "WHERE id=?",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
                image_url,
                dog_id,            # ← this was truncated before
            ),
        )
        db.execute(
            "UPDATE dogs SET name=?, age=?, size=?, status=?, kid_friendly=?, cat_friendly=?, dog_friendly=?, notes=?, image_url=? "
            "WHERE id=?",
            (
                form.get("name"),
                int(form.get("age", 0) or 0),
                form.get("size", "Medium"),
                form.get("status", "Intake"),
                1 if form.get("kid_friendly") else 0,
                1 if form.get("cat_friendly") else 0,
                1 if form.get("dog_friendly") else 0,
                form.get("notes", ""),
                image_url,
                dog_id,            # ← this was truncated before
            ),
        )
        db.commit()
        flash("Dog updated.")
        return redirect(url_for("index"))

    # Convert Row to simple object with attrs for template convenience
    class Obj:
        pass
    o = Obj()
    for k in dog.keys():
        setattr(o, k, dog[k])
    return render_template("form.html", dog=o)

@app.route("/delete/<int:dog_id>")
def delete(dog_id):
    db = get_db()
    db.execute("DELETE FROM dogs WHERE id=?", (dog_id,))
    db.commit()
    flash("Dog deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # optional 5MB cap
    app.run(debug=True)
