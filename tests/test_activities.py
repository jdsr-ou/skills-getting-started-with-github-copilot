"""Tests for activity endpoints using the AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        # Arrange
        # No setup needed for this endpoint

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        # Arrange
        # No setup needed for this endpoint

        # Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that response contains expected activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self, client):
        """Test signup fails if student is already registered."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_signup_at_max_capacity(self, client):
        """Test signup fails when activity is at max capacity."""
        # Arrange
        activity_name = "Tennis Club"
        activities = client.get("/activities").json()
        current_participants = len(activities[activity_name]["participants"])
        max_capacity = activities[activity_name]["max_participants"]
        
        # Fill up Tennis Club to max capacity
        for i in range(max_capacity - current_participants):
            email = f"student{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"}
        )

        # Assert
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister fails if student is not registered."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_removes_participant(self, client):
        """Test that unregistering actually removes the participant."""
        # Arrange
        activity_name = "Art Studio"
        email = "testuser@mergington.edu"
        
        # Signup first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify signup was successful
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]


class TestRootRedirect:
    """Tests for root endpoint redirect."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static files."""
        # Arrange
        expected_redirect = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect
