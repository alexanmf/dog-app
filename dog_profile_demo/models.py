from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# =========================
# USER MODEL
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="staff")  # admin, coordinator, staff, foster
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    messages = db.relationship("DogMessage", backref="user", lazy=True)
    documents = db.relationship("Document", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# =========================
# DOG MODEL
# =========================
class Dog(db.Model):
    __tablename__ = "dogs"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100))
    age = db.Column(db.String(50))
    size = db.Column(db.String(50))
    friendliness = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False, default="Available")
    image_url = db.Column(db.String(500))  # URL or static path
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    documents = db.relationship(
        "Document",
        backref="dog",
        lazy=True,
        cascade="all, delete-orphan"
    )

    messages = db.relationship(
        "DogMessage",
        backref="dog",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Dog {self.name}>"


# =========================
# DOCUMENT MODEL
# =========================
class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    dog_id = db.Column(db.Integer, db.ForeignKey("dogs.id"), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Optional link to logged-in user
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Simple fallback/display field
    uploaded_by_name = db.Column(db.String(100))

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Document {self.filename}>"


# =========================
# CHAT / MESSAGES MODEL
# =========================
class DogMessage(db.Model):
    __tablename__ = "dog_messages"

    id = db.Column(db.Integer, primary_key=True)

    dog_id = db.Column(db.Integer, db.ForeignKey("dogs.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    sender_name = db.Column(db.String(100))   # fallback if no user system yet
    sender_role = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Message {self.id} for Dog {self.dog_id}>"
