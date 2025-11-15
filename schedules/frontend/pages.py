"""Define the pages of the website."""

from flask import Blueprint, render_template, request as flask_request

from schedules.frontend.requests import Request, RequestType
from schedules.logic.calendar import FullCalendar

pages = Blueprint("pages", __name__)

calendar = FullCalendar()


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if flask_request.method == "POST":
        request_dict = flask_request.form.to_dict()
        request_type = RequestType(request_dict.pop("request_type"))
        request = Request(request_type=request_type, payload=request_dict)
        calendar.process_request(request=request)
    return render_template("home.html", calendar=calendar, RequestType=RequestType)
