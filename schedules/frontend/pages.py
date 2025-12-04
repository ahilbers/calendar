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

    # TODO: DO NOT MERGE
    person_1 = objects.Person(
        last_name=objects.StrID("hilbers"),
        first_name=objects.StrID("adriaan"),
        home=objects.Location(objects.Country.SWITZERLAND, city=objects.StrID("zurich")),
    )
    person_2 = objects.Person(
        last_name=objects.StrID("thorsdottir"),
        first_name=objects.StrID("eva"),
        home=objects.Location(objects.Country.NORWAY, city=objects.StrID("oslo")),
    )
    for person in [person_1, person_2]:
        if person not in app.calendar.calendars.keys():
            app.calendar._add_person(person)

    if flask_request.method == "POST":
        response = app.calendar.process_frontend_request(flask_request.form.to_dict())
    return render_template(
        "home.html", calendar=app.calendar, objects=objects, RequestType=RequestType, response=response
    )
