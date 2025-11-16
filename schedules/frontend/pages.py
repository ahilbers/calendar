"""Define the pages of the website."""

from typing import cast
from flask import Blueprint, current_app, render_template, request as flask_request

from schedules.frontend.objects import AppWithCalendar
from schedules.frontend.requests import RequestType

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    app = cast(AppWithCalendar, current_app)  # Tell type checker what this is
    if flask_request.method == "POST":
        app.calendar.process_frontend_request(flask_request.form.to_dict())
    return render_template("home.html", calendar=app.calendar, RequestType=RequestType)
