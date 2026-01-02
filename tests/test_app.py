"""Tests for the Mergington High School Activities API."""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis techniques and compete in matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and visual art techniques",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 18,
            "participants": ["zoe@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Compete in mathematical problem-solving competitions",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ryan@mergington.edu", "noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu"]
        },
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup: reset again
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns status 200."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary of activities."""
        response = client.get("/activities")
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_get_activities_has_expected_activities(self, client, reset_activities):
        """Test that GET /activities includes expected activity names."""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = ["Basketball", "Tennis Club", "Drama Club", "Chess Club"]
        for activity in expected_activities:
            assert activity in activities
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for a new participant."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup adds the participant to the activity's participants list."""
        new_email = "newstudent@mergington.edu"
        client.post("/activities/Basketball/signup", params={"email": new_email})
        
        response = client.get("/activities")
        activities = response.json()
        assert new_email in activities["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for a nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Test that duplicate signup returns 400 error."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "alex@mergington.edu"}  # Already registered
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count."""
        response_before = client.get("/activities")
        before_count = len(response_before.json()["Tennis Club"]["participants"])
        
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response_after = client.get("/activities")
        after_count = len(response_after.json()["Tennis Club"]["participants"])
        
        assert after_count == before_count + 1


class TestUnregister:
    """Test the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration of a participant."""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant_from_activity(self, client, reset_activities):
        """Test that unregister removes the participant from the activity."""
        email_to_remove = "alex@mergington.edu"
        client.delete(
            "/activities/Basketball/unregister",
            params={"email": email_to_remove}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email_to_remove not in activities["Basketball"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregister for a nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_unregistered_participant_returns_404(self, client, reset_activities):
        """Test that unregistering a participant not in the activity returns 404."""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count."""
        response_before = client.get("/activities")
        before_count = len(response_before.json()["Drama Club"]["participants"])
        
        client.delete(
            "/activities/Drama Club/unregister",
            params={"email": "isabella@mergington.edu"}
        )
        
        response_after = client.get("/activities")
        after_count = len(response_after.json()["Drama Club"]["participants"])
        
        assert after_count == before_count - 1
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister."""
        email = "testuser@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
