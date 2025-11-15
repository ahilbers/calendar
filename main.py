"""Start up the website."""

import logging
from schedules.frontend import create_app


if __name__ == "__main__":
    logger = logging.getLogger(__package__)
    app = create_app()
    app.run(debug=True)
