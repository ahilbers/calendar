"""Define the pages of the website."""

from flask import Blueprint

pages = Blueprint("pages", __name__)


@pages.route("/")
def home() -> str:
    return "<h1>Test</h1>"
