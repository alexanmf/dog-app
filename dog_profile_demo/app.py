from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_db, close_db

# --- Uploads / Cloudinary ---
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "dev-secret"  # for flash()

# Optional: cap upload size (5 MB)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Load env locally and configure Cloudinary (uses CLOUDINARY_URL)
load_dotenv()
cloudinary.config(secure=True)

# Allowed image types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_cloudinary(file_storage):
    """Upload a Werkzeug FileStorage to Cloudinary and return the secure URL (or None)."""
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    result = cloudinary.uploader.upload(
        file_storage,
        folder="dog_app",
        use_filename=True,
        unique_filename=False,
        overwrite=False,
    )
    return result.get("secure_url")


# --- DB lifecycle ---
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


# Ensure the image_url column exists even if the DB was created earlier
@app.before_first_request
def ensure_schema():
    db = get_db()
    cols = [row["name"] for row in db.execute("PRAGMA table_info(dogs)").fetchall()]
    if "image_url" not in cols:
        db.execute("ALTER TABLE dogs ADD COLUMN image_url TEXT")
        db.commit()


# --- Routes ---
@app.route("/")
def index():
    db = get_db()
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

    dogs = db.execute(sql, params).fetchall()
    return render_template("index.html", dogs=dogs)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        db = get_db()
        form = request.form

        # optional image upload
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

        # keep old URL unless a new upload is provided
        image_url = dog["image_url"] if "image_url" in dog.keys() else None
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
                dog_id,
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
    app.run(debug=True)


