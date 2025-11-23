"""Define the pages of the website."""

from typing import cast
from flask import Blueprint, current_app, render_template, request as flask_request

from schedules.logic import objects
from schedules.frontend.objects import AppWithCalendar
from schedules.logic.requests import RequestType, Response

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    app = cast(AppWithCalendar, current_app)
    response = Response(code=200, message="Ready")
    if flask_request.method == "POST":
        response = app.calendar.process_frontend_request(flask_request.form.to_dict())
    return render_template(
        "home.html", calendar=app.calendar, objects=objects, RequestType=RequestType, response=response
    )
