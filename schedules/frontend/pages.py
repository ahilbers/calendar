"""Define the pages of the website."""

from flask import Blueprint, render_template, request

pages = Blueprint("pages", __name__)


@pages.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        pass
        # data = dict(request.form)
        # if request.form.get("request_id") == "add_person":
        #     print(f"Placeholder: add person {data}.")
    return render_template("home.html")
