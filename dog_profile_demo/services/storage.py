import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "png", "jpg", "jpeg", "txt"
}


def allowed_file(filename):
    """
    Return True if the filename has an allowed extension.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def ensure_folder_exists(folder_path):
    """
    Create the folder if it does not already exist.
    """
    os.makedirs(folder_path, exist_ok=True)


def generate_unique_filename(filename):
    """
    Create a unique, secure filename while preserving the original extension.
    """
    safe_name = secure_filename(filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name, safe_name


def save_uploaded_file(file, upload_folder):
    """
    Save an uploaded file locally.

    Returns a dictionary with:
    - original_filename
    - stored_filename
    - file_path
    """
    if not file or file.filename == "":
        raise ValueError("No file selected.")

    if not allowed_file(file.filename):
        raise ValueError("File type is not allowed.")

    ensure_folder_exists(upload_folder)

    stored_filename, original_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(upload_folder, stored_filename)

    file.save(file_path)

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": file_path
    }


def delete_local_file(file_path):
    """
    Delete a local file if it exists.
    """
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def relative_static_file_url(stored_filename, subfolder="uploads/documents"):
    """
    Build a relative static URL path for a saved file.

    Example output:
    /static/uploads/documents/abc123.pdf
    """
    return f"/static/{subfolder}/{stored_filename}"
