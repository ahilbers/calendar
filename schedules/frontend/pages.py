"""Define the pages of the website."""

from flask import Blueprint, render_template

pages = Blueprint("pages", __name__)


@pages.route("/")
def home() -> str:
    return render_template("home.html")
