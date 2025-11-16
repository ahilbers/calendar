import os

from dotenv import load_dotenv
from flask import Flask

from schedules.frontend.pages import pages
from schedules.logic.calendar import FullCalendar

load_dotenv()


class AppWithCalendar(Flask):
    """An app, with a calendar object attached."""

    def __init__(self, import_name: str):
        super().__init__(import_name)
        self.calendar = FullCalendar()


def create_app():
    app = AppWithCalendar(__name__)

    # Set up flask key
    secret_key = os.environ.get("FLASK_KEY")
    if secret_key is None:
        raise RuntimeError("Secret key not defined. Create .env file of form:\n\n" "FLASK_KEY='<MY_SECRET_KEY>'\n\n")
    app.config["SECRET_KEY"] = secret_key

    # Generate pages
    app.register_blueprint(pages, url_prefix="/")

    return app
