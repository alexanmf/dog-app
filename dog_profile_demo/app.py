import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename

# db.py must export these helpers.
from db import get_db, close_db, execute

from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# ---------------------------
# App & config
# ---------------------------
app = Flask(__name__)
load_dotenv()

# Use a real secret in production via env
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Max upload size (adjust if you expect bigger PDFs)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10 MB

# Cloudinary config (either CLOUDINARY_URL or individual vars)
if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))
else:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

# ---------------------------
# Allowed types
# ---------------------------
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_DOC_EXT   = {"pdf", "doc", "docx", "xls", "xlsx", "csv", "txt"}

def allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXT

def allowed_doc(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_DOC_EXT

# ---------------------------
# Upload helpers
# ---------------------------
def save_image(file_storage):
    """
    Upload an image to Cloudinary and return secure_url, or None on failure.
    """
    if not file_storage or not file_storage.filename or not allowed_image(file_storage.filename):
        return None
    try:
        original = secure_filename(file_storage.filename)
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

def save_document(file_storage):
    """
    Upload a document (PDF/DOCX/etc.) to Cloudinary as raw and
    return {url, title, content_type} or None on failure.
    """
    if not file_storage or not file_storage.filename or not allowed_doc(file_storage.filename):
        return None
    try:
        up = cloudinary.uploader.upload(
            file_storage,
            folder=os.getenv("CLOUDINARY_DOC_FOLDER", "dogs/docs"),
            resource_type="raw",   # required for non-image files
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        return {
            "url": up.get("secure_url"),
            "title": file_storage.filename,
            "content_type": file_storage.mimetype or None,
        }
    except Exception:
        return None

# ---------------------------
# DB lifecycle
# ---------------------------
@app.teardown_appcontext
def teardown_db(exception):
    close_db()

# Ensure documents table exists (Flask 3 compatible: run once on first request)
app.config["DOCS_TABLE_READY"] = False

@app.before_request
def ensure_docs_table_once():
    if not app.config["DOCS_TABLE_READY"]:
        execute("""
            CREATE TABLE IF NOT EXISTS dog_documents (
                id SERIAL PRIMARY KEY,
                dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                file_url TEXT NOT NULL,
                content_type TEXT,
                uploaded_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        get_db().commit()
        app.config["DOCS_TABLE_READY"] = True

# ---------------------------
# Routes
# ---------------------------
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

        image_url = None
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_image(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                url = save_image(file)
                if url:
                    image_url = url
                else:
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
        image_url = dog.get("image_url")

        file = request.files.get("image")
        if file and file.filename:
            if not allowed_image(file.filename):
                flash("Invalid image type. Use png/jpg/jpeg/gif/webp.")
            else:
                url = save_image(file)
                if url:
                    image_url = url
                else:
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

# -------- Detail + Documents --------
@app.route("/dog/<int:dog_id>")
def detail(dog_id):
    rows = execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
    dog = rows[0] if rows else None
    if not dog:
        flash("Dog not found.")
        return redirect(url_for("index"))

    docs = execute(
        "SELECT id, title, file_url, content_type, uploaded_at "
        "FROM dog_documents WHERE dog_id = ? ORDER BY uploaded_at DESC",
        (dog_id,)
    ) or []
    return render_template("detail.html", dog=dog, docs=docs)

@app.route("/dog/<int:dog_id>/upload_doc", methods=["POST"])
def upload_doc(dog_id):
    if not execute("SELECT id FROM dogs WHERE id = ?", (dog_id,)):
        flash("Dog not found.")
        return redirect(url_for("index"))

    file = request.files.get("document")
    meta = save_document(file)
    if not meta:
        flash("Invalid or failed document upload. Allowed: pdf/doc/docx/xls/xlsx/csv/txt.")
        return redirect(url_for("detail", dog_id=dog_id))

    title = request.form.get("title") or meta["title"]
    execute(
        "INSERT INTO dog_documents (dog_id, title, file_url, content_type) VALUES (?,?,?,?)",
        (dog_id, title, meta["url"], meta["content_type"])
    )
    get_db().commit()
    flash("Document uploaded.")
    return redirect(url_for("detail", dog_id=dog_id))

@app.route("/doc/<int:doc_id>/delete", methods=["POST"])
def delete_doc(doc_id):
    rows = execute("SELECT id, dog_id FROM dog_documents WHERE id = ?", (doc_id,))
    if not rows:
        flash("Document not found.")
        return redirect(url_for("index"))
    dog_id = rows[0]["dog_id"]

    execute("DELETE FROM dog_documents WHERE id = ?", (doc_id,))
    get_db().commit()
    flash("Document deleted.")
    return redirect(url_for("detail", dog_id=dog_id))

# Health check (optional)
@app.route("/health")
def health():
    return "ok", 200

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)



