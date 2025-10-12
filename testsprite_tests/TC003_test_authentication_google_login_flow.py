import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Basic auth credentials for initial login
BASIC_AUTH_CREDENTIALS = {
    "usr_usuario": "72890842@continental.edu.pe",
    "usr_password": "qwni0W6",
}


def test_authentication_google_login_flow():
    try:
        # Step 1: Login with basic authentication to obtain JWT token for authorized requests if needed
        login_resp = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=BASIC_AUTH_CREDENTIALS,
            timeout=TIMEOUT,
        )
        assert (
            login_resp.status_code == 200
        ), f"Login failed with status {login_resp.status_code}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        token_type = login_data.get("token_type")
        assert (
            access_token and token_type
        ), "Login response missing access_token or token_type"
        # headers_auth = {"Authorization": f"{token_type} {access_token}"}  # Unused for now

        # Step 2: Call POST /api/v1/auth/google with a dummy id_token (simulate Google id_token)
        fake_id_token = "dummy-valid-google-id-token-for-testing"
        google_login_resp = requests.post(
            f"{BASE_URL}/api/v1/auth/google",
            json={"id_token": fake_id_token},
            timeout=TIMEOUT,
        )
        # This endpoint will validate id_token; likely will reject an invalid token.
        # Assert for either 200 or 401 unauthorized (handled compliant)
        assert google_login_resp.status_code in (
            200,
            401,
        ), f"/api/v1/auth/google unexpected status: {google_login_resp.status_code}"
        if google_login_resp.status_code == 200:
            google_login_json = google_login_resp.json()
            assert (
                "access_token" in google_login_json
                and "token_type" in google_login_json
            ), "Google login success response missing tokens"

        # Step 3: GET /api/v1/auth/google/start?redirect_to=someurl
        redirect_url = "http://localhost:8000/welcome"
        google_start_resp = requests.get(
            f"{BASE_URL}/api/v1/auth/google/start",
            params={"redirect_to": redirect_url},
            timeout=TIMEOUT,
        )
        # This should redirect or return a URL to initiate Google OAuth
        assert (
            google_start_resp.status_code == 200
        ), f"/api/v1/auth/google/start returned status {google_start_resp.status_code}"
        # Usually returns some OAuth2 URL to redirect user; verify text or json response
        # Accept text or json containing URL
        content_type = google_start_resp.headers.get("Content-Type", "")
        assert content_type.startswith(
            ("text/", "application/json")
        ), "Unexpected content type for /api/v1/auth/google/start"
        if "application/json" in content_type:
            json_data = google_start_resp.json()
            assert (
                "url" in json_data or "redirect_url" in json_data or len(json_data) > 0
            ), "Expected URL or redirect info in JSON response of /api/v1/auth/google/start"

        # Step 4: GET /api/v1/auth/google/callback with parameters code and state (simulate callback)
        # Simulate a successful callback with dummy code and state, no error param.
        callback_params = {
            "code": "dummy-code-for-callback",
            "state": "dummy-state-string",
        }
        google_callback_resp = requests.get(
            f"{BASE_URL}/api/v1/auth/google/callback",
            params=callback_params,
            timeout=TIMEOUT,
        )
        assert (
            google_callback_resp.status_code == 200
        ), f"/api/v1/auth/google/callback unexpected status {google_callback_resp.status_code}"
        # The callback may return HTML or JSON acknowledging success
        # Accept content type text/html or application/json
        callback_content_type = google_callback_resp.headers.get("Content-Type", "")
        assert callback_content_type.startswith(
            ("text/html", "application/json")
        ), "Unexpected content type for /api/v1/auth/google/callback"

        # Step 5: GET /api/v1/auth/google/callback with error parameter to simulate OAuth error
        error_params = {"error": "access_denied", "state": "dummy-state-string"}
        google_callback_error_resp = requests.get(
            f"{BASE_URL}/api/v1/auth/google/callback",
            params=error_params,
            timeout=TIMEOUT,
        )
        # Should return 200 with error info or redirect, or specific error code handled gracefully
        assert (
            google_callback_error_resp.status_code in (200, 400, 401)
        ), f"/api/v1/auth/google/callback with error param returned unexpected status {google_callback_error_resp.status_code}"

    except RequestException as e:
        assert False, f"HTTP request failed: {e}"
    except AssertionError as ae:
        raise ae


test_authentication_google_login_flow()
