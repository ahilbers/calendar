import os

from dotenv import load_dotenv
from flask import Flask

from schedules.frontend.pages import pages

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Set up flask key
    secret_key = os.environ.get("FLASK_KEY")
    if secret_key is None:
        raise RuntimeError("Secret key not defined. Create .env file of form:\n\n" "FLASK_KEY='<MY_SECRET_KEY>'\n\n")
    app.config["SECRET_KEY"] = secret_key

    # Generate pages
    app.register_blueprint(pages, url_prefix="/")

    return app
