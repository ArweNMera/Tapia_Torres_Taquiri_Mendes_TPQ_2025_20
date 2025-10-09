import requests

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/v1/usuarios/register"
TIMEOUT = 30

def test_user_registration_endpoint():
    url = BASE_URL + REGISTER_ENDPOINT

    # Data payload for new user registration
    payload = {
        "usr_usuario": "testuser_tc004",
        "usr_email": "testuser_tc004@example.com",
        "usr_password": "StrongPass123!",
        "usr_nombre": "Test",
        "usr_apellido": "User"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        # Verify response status code for success (usually 201 Created or 200 OK)
        assert response.status_code in [200, 201], f"Unexpected status code: {response.status_code}"
        json_resp = response.json()
        # Expecting some indication of user created; cannot assume exact structure but at least check keys returned
        # If response includes the created user info, check for at least the 'usr_usuario' or 'usr_email' keys
        # If error, response might include error keys (we expect success here)
        assert isinstance(json_resp, dict), "Response is not JSON object"
        # Check expected keys present in response (assuming at least 'usr_usuario' or 'id')
        assert any(k in json_resp for k in ("usr_usuario", "usr_email", "id")), "Expected keys not found in response"
    except requests.RequestException as e:
        assert False, f"Request failed with exception: {e}"

test_user_registration_endpoint()
