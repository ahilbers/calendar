"""Start up the website."""

import logging
from schedules.frontend import create_app

# Create app instance for gunicorn
app = create_app()

if __name__ == "__main__":
    logger = logging.getLogger(__package__)
    app.run(host="0.0.0.0", port=5000, debug=True)
