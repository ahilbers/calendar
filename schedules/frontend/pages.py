"""Define the pages of the website."""

import datetime as dt
from typing import cast
from flask import Blueprint, current_app, render_template, request as flask_request, session

from schedules.logic import objects
from schedules.logic.calendar import FullCalendar
from schedules.logic.storage import CalendarRepository
from schedules.frontend.app_with_calendar import AppWithCalendar
from schedules.logic.requests import RequestType, Response

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    app = cast(AppWithCalendar, current_app)
    with app.database_session_maker() as session_db:
        repository = CalendarRepository(session_db)
        calendar = FullCalendar(database_repository=repository)
        calendar.load_from_repository()

        # Restore daily calendar dates from session if they exist
        if "daily_calendar_start_date" in session and "daily_calendar_end_date" in session:
            start_date = dt.date.fromisoformat(session["daily_calendar_start_date"])
            end_date = dt.date.fromisoformat(session["daily_calendar_end_date"])
            calendar.set_daily_calendars_dates(start_date, end_date)

        response = Response(code=200, message="Ready")
        if flask_request.method == "POST":
            response = calendar.process_frontend_request(flask_request.form.to_dict())
            
            # Save daily calendar dates to session if they were updated
            start_date, end_date = calendar.get_daily_calendars_dates()
            if start_date and end_date:
                session["daily_calendar_start_date"] = start_date.isoformat()
                session["daily_calendar_end_date"] = end_date.isoformat()

        return render_template(
            "home.html", calendar=calendar, objects=objects, RequestType=RequestType, response=response
        )
