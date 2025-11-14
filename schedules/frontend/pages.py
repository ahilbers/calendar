"""Define the pages of the website."""

from flask import Blueprint, render_template, request

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        data = dict(request.form)
        if request.form.get("request_id") == "add_person":
            _ = data  # Placeholder: add person to calendar
    return render_template("home.html")
