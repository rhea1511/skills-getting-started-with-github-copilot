from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    # Check if we get HTML content
    assert "text/html" in response.headers["content-type"]
    # Verify it contains our page title
    assert "Mergington High School" in response.text

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Test activity structure
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity():
    # Test successful signup
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # Try to sign up the same student twice
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity():
    # First, add a student
    email = "tounregister@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")

    # Test successful unregister
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered():
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]