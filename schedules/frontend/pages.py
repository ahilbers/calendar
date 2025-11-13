"""Define the pages of the website."""

from flask import Blueprint, render_template, request

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        data = dict(request.form)
        print(data)
    return render_template("home.html")
