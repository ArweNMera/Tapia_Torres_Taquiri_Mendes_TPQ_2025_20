import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "72890842@continental.edu.pe"
AUTH_PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_machine_learning_nutritional_summary_generation():
    login_url = f"{BASE_URL}/api/v1/auth/login"
    ml_summary_url = f"{BASE_URL}/api/v1/ml/summary"

    try:
        # Authenticate user to get access token
        login_payload = {
            "usr_usuario": AUTH_USERNAME,
            "usr_password": AUTH_PASSWORD
        }

        login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_response.status_code == 200, "Login failed"
        login_json = login_response.json()
        assert "access_token" in login_json, "access_token not in login response"
        assert "token_type" in login_json, "token_type not in login response"
        access_token = login_json["access_token"]
        token_type = login_json["token_type"]
        assert token_type.lower() == "bearer", "token_type is not 'bearer'"

        headers = {
            "Authorization": f"{token_type} {access_token}",
            "Content-Type": "application/json"
        }

        # Prepare sample input for features and scores
        features = {
            "age": 8,
            "weight": 25.5,
            "height": 130.2,
            "activity_level": "moderate",
            "dietary_restrictions": ["gluten"],
            "allergies": ["peanut"]
        }
        scores = {
            "caloric_needs": 1600,
            "protein_needs": 50,
            "fat_needs": 60,
            "carb_needs": 200
        }
        ml_payload = {
            "features": features,
            "scores": scores,
            "prefer_llm": True
        }

        ml_response = requests.post(ml_summary_url, headers=headers, json=ml_payload, timeout=TIMEOUT)

        assert ml_response.status_code == 200, f"ML summary generation failed with status {ml_response.status_code}"
        ml_json = ml_response.json()
        assert "text" in ml_json, "Response missing 'text' key"
        assert isinstance(ml_json["text"], str) and len(ml_json["text"].strip()) > 0, "'text' must be non-empty string"
        assert "used_llm" in ml_json, "Response missing 'used_llm' key"
        assert isinstance(ml_json["used_llm"], bool), "'used_llm' must be boolean"

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_machine_learning_nutritional_summary_generation()
