"""Test main function(s)."""

from schedules.frontend import create_app


def test_create_site():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
