import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# NOTE: db.py must export get_db, close_db, and execute()
from db import get_db, close_db, execute

from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "dev-secret"  # change in production via env

load_dotenv()

# Configure Cloudinary from CLOUDINARY_URL or individual vars
if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))
else:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

# Optional: cap upload size (5 MB)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# ---- Cloudinary upload setup (images only) ----
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file_storage):
    """
    Upload the image to Cloudinary and return secure_url, or None on failure.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    original = secure_filename(file_storage.filename)
    try:
        up = cloudinary.uploader.upload(
            file_storage,
            folder=os.getenv("CLOUDINARY_FOLDER", "dogs/images"),
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        return up.get("secure_url")
    except Exception:
        return None

# ---- DB lifecycle ----
@app.teardown_appcontext
def teardown_db(exception):
    close_db()

# ---- Routes ----
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    size = request.args.get("size", "").strip()

    sql = """
    SELECT
      id, name, age, size, status,
      kid_friendly, cat_friendly, dog_friendly, notes,
      COALESCE(image_url, '') AS image_url
    FROM dogs
    WHERE 1=1
    """
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

    dogs = execute(sql, params) or []
    return render_template("index.html", dogs=dogs)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        form = request.form

        # optional image upload
        image_url = None
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                try:
                    image_url = save_image(file)
                except Exception:
                    image_url = None
                    flash("Image upload failed.")

        execute(
            "INSERT INTO dogs (name, age, size, status, kid_friendly, cat_friendly, "
            "dog_friendly, notes, image_url) VALUES (?,?,?,?,?,?,?,?,?)",
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
        get_db().commit()
        flash("Dog created.")
        return redirect(url_for("index"))

    return render_template("form.html", dog=None)

@app.route("/edit/<int:dog_id>", methods=["GET", "POST"])
def edit(dog_id):
    rows = execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
    dog = rows[0] if rows else None
    if not dog:
        flash("Dog not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        form = request.form

        # keep old URL unless a new upload is provided
        image_url = dog.get("image_url")
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                try:
                    new_url = save_image(file)
                    if new_url:
                        image_url = new_url
                except Exception:
                    flash("Image upload failed; keeping previous image.")

        execute(
            "UPDATE dogs SET name=?, age=?, size=?, status=?, kid_friendly=?, "
            "cat_friendly=?, dog_friendly=?, notes=?, image_url=? WHERE id=?",
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
                dog_id,
            ),
        )
        get_db().commit()
        flash("Dog updated.")
        return redirect(url_for("index"))

    # simple object for the template to use dot-notation
    class Obj: pass
    o = Obj()
    for k, v in dog.items():
        setattr(o, k, v)
    return render_template("form.html", dog=o)

@app.route("/delete/<int:dog_id>")
def delete(dog_id):
    execute("DELETE FROM dogs WHERE id=?", (dog_id,))
    get_db().commit()
    flash("Dog deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

