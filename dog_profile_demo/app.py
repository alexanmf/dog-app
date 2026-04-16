import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)

    # ---------------------------
    # Core Config
    # ---------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["MAX_CONTENT_LENGTH"] = int(
        os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    )

    # ---------------------------
    # Optional: Database URL (future use)
    # ---------------------------
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

    # ---------------------------
    # Cloudinary Config
    # ---------------------------
    import cloudinary

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
    # Register Blueprints
    # ---------------------------
    from routes.dogs import dogs_bp
    from routes.documents import documents_bp
    from routes.chat import chat_bp
    from routes.auth import auth_bp

    app.register_blueprint(dogs_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)

    # ---------------------------
    # Health Check
    # ---------------------------
    @app.route("/health")
    def health():
        return "ok", 200

    return app


# Create app instance for Gunicorn
app = create_app()


# ---------------------------
# Local Development Entry
# ---------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("DEBUG", "True") == "True",
    )



