"""
Tests for Mergington High School Activities API

This module contains comprehensive tests for all API endpoints including:
- GET /activities - Retrieve all activities
- POST /activities/{activity_name}/signup - Sign up for activities
- DELETE /activities/{activity_name}/participants/{email} - Remove participants
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test to ensure test isolation"""
    # Store original activities
    original_activities = copy.deepcopy(activities)
    
    # Reset to known state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    })
    
    yield
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
    
    def test_get_activities_returns_json(self, client, reset_activities):
        """Test that activities endpoint returns JSON content type"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Activity/signup?email=student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered returns 400"""
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_with_spaces_in_activity_name(self, client, reset_activities):
        """Test signup works with activity names containing spaces"""
        response = client.post("/activities/Programming Class/signup?email=coder@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up coder@mergington.edu for Programming Class"
    
    def test_signup_with_encoded_email(self, client, reset_activities):
        """Test signup works with URL-encoded email addresses"""
        response = client.post("/activities/Chess Club/signup?email=test%2Bstudent@mergington.edu")
        assert response.status_code == 200
        
        # Verify the email was decoded properly
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test+student@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of a participant"""
        response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Removed michael@mergington.edu from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]  # Other participant remains
    
    def test_remove_participant_activity_not_found(self, client, reset_activities):
        """Test removing participant from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent Activity/participants/student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_found(self, client, reset_activities):
        """Test removing non-existent participant returns 404"""
        response = client.delete("/activities/Chess Club/participants/notregistered@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Participant not found in this activity"
    
    def test_remove_participant_with_spaces_in_activity_name(self, client, reset_activities):
        """Test removing participant works with activity names containing spaces"""
        response = client.delete("/activities/Programming Class/participants/emma@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Removed emma@mergington.edu from Programming Class"
    
    def test_remove_participant_with_encoded_email(self, client, reset_activities):
        """Test removing participant works with URL-encoded email addresses"""
        # First add a participant with special characters
        client.post("/activities/Chess Club/signup?email=test%2Bstudent@mergington.edu")
        
        # Then remove them using encoded email
        response = client.delete("/activities/Chess Club/participants/test%2Bstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Removed test+student@mergington.edu from Chess Club"


class TestIntegrationWorkflows:
    """Integration tests for complete user workflows"""
    
    def test_complete_signup_and_removal_workflow(self, client, reset_activities):
        """Test complete workflow: signup, verify, remove, verify"""
        # Initial state check
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])
        
        # Sign up new participant
        signup_response = client.post("/activities/Chess Club/signup?email=workflow@mergington.edu")
        assert signup_response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        after_signup_data = activities_response.json()
        assert len(after_signup_data["Chess Club"]["participants"]) == initial_count + 1
        assert "workflow@mergington.edu" in after_signup_data["Chess Club"]["participants"]
        
        # Remove participant
        remove_response = client.delete("/activities/Chess Club/participants/workflow@mergington.edu")
        assert remove_response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        after_removal_data = activities_response.json()
        assert len(after_removal_data["Chess Club"]["participants"]) == initial_count
        assert "workflow@mergington.edu" not in after_removal_data["Chess Club"]["participants"]
    
    def test_multiple_participants_same_activity(self, client, reset_activities):
        """Test adding and removing multiple participants from same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Add multiple participants
        for email in emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        data = activities_response.json()
        for email in emails:
            assert email in data["Chess Club"]["participants"]
        
        # Remove one participant
        remove_response = client.delete("/activities/Chess Club/participants/student2@mergington.edu")
        assert remove_response.status_code == 200
        
        # Verify only one was removed
        activities_response = client.get("/activities")
        final_data = activities_response.json()
        assert "student1@mergington.edu" in final_data["Chess Club"]["participants"]
        assert "student2@mergington.edu" not in final_data["Chess Club"]["participants"]
        assert "student3@mergington.edu" in final_data["Chess Club"]["participants"]


class TestErrorHandling:
    """Tests for edge cases and error conditions"""
    
    def test_missing_email_parameter(self, client, reset_activities):
        """Test signup without email parameter"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_empty_activity_name(self, client, reset_activities):
        """Test endpoints with empty activity name"""
        response = client.post("/activities//signup?email=test@mergington.edu")
        assert response.status_code == 404
    
    def test_special_characters_in_activity_name(self, client, reset_activities):
        """Test that special characters in activity names are handled properly"""
        # This should work with URL encoding
        response = client.get("/activities")
        assert response.status_code == 200
        
        # Activity names with spaces should work when properly encoded
        response = client.post("/activities/Chess%20Club/signup?email=encoded@mergington.edu")
        assert response.status_code == 200