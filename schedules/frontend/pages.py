"""Define the pages of the website."""

from flask import Blueprint, render_template, request

from schedules.frontend import requests as request_lib

pages = Blueprint("pages", __name__)


calendar = "Calendar Render Placeholder"


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        data = request.form
        print(data)

        if request.form.get("request_id") == "add_person":
            _ = data  # Placeholder: add person to calendar
    return render_template("home.html", calendar=calendar, request_lib=request_lib)
