"""Start up the website."""

from schedules.frontend import create_app

from schedules.frontend import requests

if __name__ == "__main__":
    # breakpoint()
    app = create_app()
    app.run(debug=True)
