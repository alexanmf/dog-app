import os
import uuid
from flask import Blueprint, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from models import db, Dog, Document

documents_bp = Blueprint("documents", __name__)


ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "png", "jpg", "jpeg", "txt"
}


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_folder(folder_path):
    """
    Make sure the upload folder exists.
    """
    os.makedirs(folder_path, exist_ok=True)


@documents_bp.route("/dog/<int:dog_id>/documents/upload", methods=["POST"])
def upload_document(dog_id):
    """
    Upload a document for a specific dog.
    """
    dog = Dog.query.get_or_404(dog_id)

    if "document" not in request.files:
        flash("No file was selected.", "error")
        return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

    file = request.files["document"]
    document_type = request.form.get("document_type", "").strip()
    notes = request.form.get("notes", "").strip()
    uploaded_by_name = request.form.get("uploaded_by_name", "").strip()

    if file.filename == "":
        flash("Please choose a file to upload.", "error")
        return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

    if not allowed_file(file.filename):
        flash("Invalid file type. Allowed: PDF, DOC, DOCX, PNG, JPG, JPEG, TXT.", "error")
        return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

    try:
        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(current_app.root_path, "static", "uploads", "documents")
        )

        ensure_upload_folder(upload_folder)

        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Relative URL for browser access
        file_url = url_for(
            "static",
            filename=f"uploads/documents/{unique_filename}"
        )

        new_document = Document(
            dog_id=dog.id,
            filename=original_filename,
            file_url=file_url,
            document_type=document_type or None,
            notes=notes or None
        )

        db.session.add(new_document)
        db.session.commit()

        flash(f"Document uploaded successfully for {dog.name}.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error uploading document: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog.id))


@documents_bp.route("/documents/<int:document_id>/delete", methods=["POST"])
def delete_document(document_id):
    """
    Delete a document record and remove the local file if it exists.
    """
    document = Document.query.get_or_404(document_id)
    dog_id = document.dog_id

    try:
        # If the file is stored locally under /static, try deleting it too.
        if document.file_url and document.file_url.startswith("/static/"):
            relative_path = document.file_url.replace("/static/", "", 1)
            absolute_path = os.path.join(current_app.root_path, "static", relative_path)

            if os.path.exists(absolute_path):
                os.remove(absolute_path)

        db.session.delete(document)
        db.session.commit()

        flash("Document deleted successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting document: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog_id))
