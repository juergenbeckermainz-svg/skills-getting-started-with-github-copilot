"""
Tests for the Mergington High School Activities API endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern for clarity and consistency.
"""

import pytest


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        
        Arrange: Prepare expected activity fields
        Act: Send GET request to /activities
        Assert: Verify status 200 and all 9 activities with required fields
        """
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        
        # Verify each activity has required fields
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert activity_details.keys() == expected_fields
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity(self, client):
        """
        Test that signing up a student for an activity succeeds.
        
        Arrange: Select an activity and email
        Act: Send POST request to signup endpoint
        Assert: Verify status 200 and participant added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        test_email = "test.student@mergington.edu"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert test_email in response.json()["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == len(initial_participants) + 1
        assert test_email in updated_participants


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_remove_participant(self, client):
        """
        Test that removing a participant from an activity succeeds.
        
        Arrange: Identify an activity with existing participants
        Act: Send DELETE request to remove a participant
        Assert: Verify status 200 and participant removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        # Use an existing participant from the initial data
        participant_to_remove = "michael@mergington.edu"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        assert participant_to_remove in initial_participants
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == len(initial_participants) - 1
        assert participant_to_remove not in updated_participants


class TestRootEndpoint:
    """Tests for the GET / endpoint."""
    
    def test_root_redirect(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: No setup needed
        Act: Send GET request to / with follow_redirects disabled
        Assert: Verify status 307 and Location header points to /static/index.html
        """
        # Arrange
        expected_redirect_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_location
