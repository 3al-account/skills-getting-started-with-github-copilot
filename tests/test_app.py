import pytest
from fastapi.testclient import TestClient
from src.app import app


# GET /activities tests
def test_get_activities_success(client, reset_activities):
    """Test GET /activities returns all activities"""
    # Arrange
    # Already arranged by reset_activities fixture
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_get_activities_returns_participant_info(client, reset_activities):
    """Test GET /activities includes participant information"""
    # Arrange & Act
    response = client.get("/activities")
    
    # Assert
    data = response.json()
    activity = data["Chess Club"]
    assert "participants" in activity
    assert "michael@mergington.edu" in activity["participants"]
    assert "daniel@mergington.edu" in activity["participants"]


def test_get_activities_includes_all_required_fields(client, reset_activities):
    """Test GET /activities returns all required activity fields"""
    # Arrange & Act
    response = client.get("/activities")
    
    # Assert
    data = response.json()
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


# POST /activities/{activity_name}/signup tests
def test_signup_success(client, reset_activities):
    """Test successful signup for an activity (AAA: Arrange-Act-Assert)"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]


def test_signup_adds_participant_to_list(client, reset_activities):
    """Test signup actually adds student to participants list"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    activities_response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = activities_response.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup fails when activity doesn't exist"""
    # Arrange
    email = "student@mergington.edu"
    activity = "NonexistentActivity"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate_student(client, reset_activities):
    """Test signup fails when student is already registered"""
    # Arrange
    email = "michael@mergington.edu"  # Already registered for Chess Club
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_multiple_students(client, reset_activities):
    """Test multiple different students can sign up"""
    # Arrange
    activity = "Chess Club"
    emails = ["student1@mergington.edu", "student2@mergington.edu"]
    
    # Act
    responses = [client.post(f"/activities/{activity}/signup?email={email}") for email in emails]
    get_response = client.get("/activities")
    
    # Assert
    assert all(r.status_code == 200 for r in responses)
    data = get_response.json()
    for email in emails:
        assert email in data[activity]["participants"]


# DELETE /activities/{activity_name}/unregister tests
def test_unregister_success(client, reset_activities):
    """Test successful unregister from an activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email in data["message"]


def test_unregister_removes_participant_from_list(client, reset_activities):
    """Test unregister actually removes student from participants list"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    activities_response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = activities_response.json()
    assert email not in data[activity]["participants"]


def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister fails when activity doesn't exist"""
    # Arrange
    email = "student@mergington.edu"
    activity = "NonexistentActivity"
    
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_student_not_registered(client, reset_activities):
    """Test unregister fails when student is not registered"""
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


# Integration tests
def test_signup_and_unregister_flow(client, reset_activities):
    """Test complete flow: signup then unregister"""
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    
    # Act - signup
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    activities_after_signup = client.get("/activities")
    
    # Assert setup worked
    assert signup_response.status_code == 200
    assert email in activities_after_signup.json()[activity]["participants"]
    
    # Act - unregister
    unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
    activities_after_unregister = client.get("/activities")
    
    # Assert cleanup worked
    assert unregister_response.status_code == 200
    assert email not in activities_after_unregister.json()[activity]["participants"]
