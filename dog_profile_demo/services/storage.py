import os
import uuid
import cloudinary.uploader
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "png", "jpg", "jpeg", "txt", "gif", "webp"
}

ALLOWED_IMAGE_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "webp"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def ensure_folder_exists(folder_path):
    os.makedirs(folder_path, exist_ok=True)


def generate_unique_filename(filename):
    safe_name = secure_filename(filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name, safe_name


def save_uploaded_file(file, upload_folder):
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
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def relative_static_file_url(stored_filename, subfolder="uploads/documents"):
    return f"/static/{subfolder}/{stored_filename}"


def upload_image_to_cloudinary(file):
    """
    Upload a dog photo to Cloudinary and return the image URL.
    """
    if not file or file.filename == "":
        return None

    if not allowed_image(file.filename):
        raise ValueError("Invalid image type. Allowed: png, jpg, jpeg, gif, webp.")

    result = cloudinary.uploader.upload(
        file,
        folder=os.getenv("CLOUDINARY_FOLDER", "dogs/images"),
        resource_type="image",
        use_filename=True,
        unique_filename=True,
        overwrite=False
    )

    return result.get("secure_url")
