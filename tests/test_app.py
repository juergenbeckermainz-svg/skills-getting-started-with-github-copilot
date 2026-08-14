"""
Tests for the Mergington High School Activities API endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern for clarity and consistency.
Coverage includes happy paths, error cases, and edge cases.
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
    
    def test_get_activities_contains_specific_activities(self, client):
        """
        Test that GET /activities returns specific expected activities.
        
        Arrange: Define activity names to check for
        Act: Send GET request to /activities
        Assert: Verify all expected activities are present
        """
        # Arrange
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Drama Society",
            "Robotics Club",
            "Debate Team"
        }
        
        # Act
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        activity_names = set(activities.keys())
        assert expected_activities == activity_names


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
    
    def test_signup_multiple_students_same_activity(self, client):
        """
        Test that multiple different students can sign up for same activity.
        
        Arrange: Prepare two different email addresses
        Act: Sign up both students sequentially
        Assert: Verify both are added to participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1.unique@mergington.edu"
        email2 = "student2.unique@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act - Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        
        # Act - Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        updated_response = client.get("/activities")
        participants = updated_response.json()[activity_name]["participants"]
        assert len(participants) == initial_count + 2
        assert email1 in participants
        assert email2 in participants
    
    def test_signup_duplicate_student_returns_400(self, client):
        """
        Test that signing up a student already registered returns 400 error.
        
        Arrange: Sign up a student once, then attempt to sign up again
        Act: Send POST request for duplicate signup
        Assert: Verify status 400 and error message
        """
        # Arrange
        activity_name = "Art Club"
        test_email = "duplicate.test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response1.status_code == 200
        
        # Act - Attempt duplicate signup
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signing up for non-existent activity returns 404 error.
        
        Arrange: Prepare a non-existent activity name
        Act: Send POST request for non-existent activity
        Assert: Verify status 404 and error message
        """
        # Arrange
        nonexistent_activity = "Fictional Activity"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_with_special_characters_in_email(self, client):
        """
        Test that signup works with email addresses containing special characters.
        
        Arrange: Prepare email with special characters
        Act: Send POST request with special character email
        Assert: Verify signup succeeds
        """
        # Arrange
        activity_name = "Soccer Team"
        special_email = "student+test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": special_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify email was added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert special_email in participants


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
    
    def test_remove_nonexistent_participant_returns_400(self, client):
        """
        Test that removing a non-existent participant returns 400 error.
        
        Arrange: Prepare an email that is not signed up
        Act: Send DELETE request for non-existent participant
        Assert: Verify status 400 and error message
        """
        # Arrange
        activity_name = "Swimming Club"
        nonexistent_email = "never.signed.up@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Test that removing from non-existent activity returns 404 error.
        
        Arrange: Prepare a non-existent activity name
        Act: Send DELETE request for non-existent activity
        Assert: Verify status 404 and error message
        """
        # Arrange
        nonexistent_activity = "Ghost Activity"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_then_signup_again(self, client):
        """
        Test that a removed participant can sign up again.
        
        Arrange: Get activity and prepare email
        Act: Sign up, remove, then sign up again
        Assert: Verify all operations succeed and final count is correct
        """
        # Arrange
        activity_name = "Drama Society"
        test_email = "remove.signup.test@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act - Sign up
        signup_response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup_response1.status_code == 200
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        assert remove_response.status_code == 200
        
        # Act - Sign up again
        signup_response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert signup_response2.status_code == 200
        
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert test_email in final_response.json()[activity_name]["participants"]


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
    
    def test_root_redirect_follow(self, client):
        """
        Test that following the redirect from / reaches the static index.html.
        
        Arrange: No setup needed
        Act: Send GET request to / with follow_redirects enabled
        Assert: Verify final status 200 and HTML content is served
        """
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        # Verify HTML content is served
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text


class TestIntegration:
    """Integration tests for complex workflows."""
    
    def test_signup_remove_signup_workflow(self, client):
        """
        Test complete workflow: signup, verify, remove, verify, signup again.
        
        Arrange: Prepare activity and email
        Act: Execute complete workflow
        Assert: Verify each step produces expected results
        """
        # Arrange
        activity_name = "Robotics Club"
        test_email = "workflow.test@mergington.edu"
        
        # Step 1: Get initial state
        initial = client.get("/activities").json()[activity_name]
        initial_count = len(initial["participants"])
        
        # Step 2: Sign up
        signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup.status_code == 200
        
        # Step 3: Verify signup
        after_signup = client.get("/activities").json()[activity_name]
        assert len(after_signup["participants"]) == initial_count + 1
        assert test_email in after_signup["participants"]
        
        # Step 4: Remove
        remove = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        assert remove.status_code == 200
        
        # Step 5: Verify removal
        after_remove = client.get("/activities").json()[activity_name]
        assert len(after_remove["participants"]) == initial_count
        assert test_email not in after_remove["participants"]
        
        # Step 6: Sign up again
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup2.status_code == 200
        
        # Step 7: Verify final state
        final = client.get("/activities").json()[activity_name]
        assert len(final["participants"]) == initial_count + 1
        assert test_email in final["participants"]
