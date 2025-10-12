import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_authentication_login_endpoint():
    url = f"{BASE_URL}/api/v1/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {"usr_usuario": "testuser", "usr_password": "qwni0W6"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to /api/v1/auth/login failed: {e}"

    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    json_data = response.json()
    assert "access_token" in json_data, "Response JSON does not contain 'access_token'"
    assert (
        isinstance(json_data["access_token"], str)
        and len(json_data["access_token"]) > 0
    ), "'access_token' is empty or not string"
    assert "token_type" in json_data, "Response JSON does not contain 'token_type'"
    assert (
        isinstance(json_data["token_type"], str) and len(json_data["token_type"]) > 0
    ), "'token_type' is empty or not string"


test_authentication_login_endpoint()
