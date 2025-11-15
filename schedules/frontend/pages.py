"""Define the pages of the website."""

from flask import Blueprint, render_template, request as flask_request

from schedules.frontend import requests as request_lib
from schedules.logic.calendar import FullCalendar

pages = Blueprint("pages", __name__)

calendar = FullCalendar()


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if flask_request.method == "POST":
        request_dict = flask_request.form.to_dict()
        request_type = request_lib.RequestType(request_dict.pop("request_type"))
        print(request_type)
        print(request_dict)
        # print(data)
        # _ = data.pop("request_type")
        # print(data)
        # if request.form.get("request_type") == "add_person":
        #     _ = data  # Placeholder: add person to calendar
    return render_template("home.html", calendar=calendar, request_lib=request_lib)
