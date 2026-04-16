from flask import Blueprint, request, redirect, url_for, flash
from models import db, Dog, DogMessage

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/dog/<int:dog_id>/messages/add", methods=["POST"])
def add_message(dog_id):
    """
    Add a new chat/message entry for a specific dog.
    """
    dog = Dog.query.get_or_404(dog_id)

    sender_name = request.form.get("sender_name", "").strip()
    sender_role = request.form.get("sender_role", "").strip()
    message_text = request.form.get("message", "").strip()

    if not message_text:
        flash("Message cannot be empty.", "error")
        return redirect(url_for("dogs.dog_detail", dog_id=dog.id))

    new_message = DogMessage(
        dog_id=dog.id,
        sender_name=sender_name or "Anonymous",
        sender_role=sender_role or None,
        message=message_text
    )

    try:
        db.session.add(new_message)
        db.session.commit()
        flash("Message added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding message: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog.id))


@chat_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
def delete_message(message_id):
    """
    Delete a message from a dog's chat thread.
    """
    message = DogMessage.query.get_or_404(message_id)
    dog_id = message.dog_id

    try:
        db.session.delete(message)
        db.session.commit()
        flash("Message deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting message: {str(e)}", "error")

    return redirect(url_for("dogs.dog_detail", dog_id=dog_id))
