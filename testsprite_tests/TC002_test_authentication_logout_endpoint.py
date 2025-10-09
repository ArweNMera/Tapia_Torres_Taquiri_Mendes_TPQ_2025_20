import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LOGOUT_URL = f"{BASE_URL}/api/v1/auth/logout"
TIMEOUT = 30

USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"


def test_authentication_logout_endpoint():
    # Login to get the JWT token
    login_payload = {
        "usr_usuario": USERNAME,
        "usr_password": PASSWORD,
    }
    try:
        login_response = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
        login_json = login_response.json()
        access_token = login_json.get("access_token")
        token_type = login_json.get("token_type")
        assert access_token and token_type, "Missing access_token or token_type in login response"

        headers = {
            "Authorization": f"{token_type} {access_token}"
        }

        # Call logout endpoint
        logout_response = requests.post(LOGOUT_URL, headers=headers, timeout=TIMEOUT)
        assert logout_response.status_code in (200, 204), f"Logout failed with status {logout_response.status_code}"

        # Verify token is invalidated by calling a protected endpoint (/api/v1/usuarios/me)
        protected_url = f"{BASE_URL}/api/v1/usuarios/me"
        protected_response_after_logout = requests.get(protected_url, headers=headers, timeout=TIMEOUT)
        assert protected_response_after_logout.status_code == 401, (
            f"Token not invalidated after logout, status {protected_response_after_logout.status_code}"
        )

    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_authentication_logout_endpoint()